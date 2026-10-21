from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yfinance as yf

OHLC = ["Open", "High", "Low", "Close"]
OUTPUT_COLUMNS = ["timestamp", "symbol", "timeframe", "open", "high", "low", "close"]


def load_membership_symbols(path: str | Path) -> list[str]:
    frame = pd.read_csv(path, usecols=["symbol"])
    symbols = (
        frame["symbol"]
        .dropna()
        .astype(str)
        .str.strip()
    )
    return sorted(symbol for symbol in symbols.unique() if symbol and symbol.casefold() != "nan")


def extract_symbol_bars(data: pd.DataFrame, ticker: str, symbol: str) -> pd.DataFrame:
    if data.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    if isinstance(data.columns, pd.MultiIndex):
        selected = None
        for level in range(data.columns.nlevels):
            if ticker in data.columns.get_level_values(level):
                selected = data.xs(ticker, axis=1, level=level)
                break
        if selected is None:
            return pd.DataFrame(columns=OUTPUT_COLUMNS)
        frame = selected
    else:
        frame = data

    if not set(OHLC).issubset(frame.columns):
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result = frame[OHLC].dropna().copy()
    if result.empty:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    result["timestamp"] = pd.to_datetime(result.index, utc=True)
    result["symbol"] = symbol
    result["timeframe"] = "1d"
    result = result.rename(
        columns={"Open": "open", "High": "high", "Low": "low", "Close": "close"}
    )
    return result[OUTPUT_COLUMNS].reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Attempt to retrieve daily OHLC for every symbol in a historical "
            "membership file. This does not guarantee delisted-symbol coverage."
        )
    )
    parser.add_argument("--membership", default="data/raw/nifty500_membership.csv")
    parser.add_argument("--start", default="2017-10-01")
    parser.add_argument("--end", default="2026-03-31", help="Exclusive end date, as in yfinance.")
    parser.add_argument(
        "--output",
        default="data/raw/nifty500_membership_daily_yfinance.csv",
    )
    parser.add_argument(
        "--audit-output",
        default="data/output/historical_membership_download_audit.csv",
    )
    parser.add_argument("--chunk-size", type=int, default=25)
    parser.add_argument("--limit", type=int, help="Optional symbol limit for a small trial run.")
    args = parser.parse_args()

    if args.chunk_size < 1:
        parser.error("--chunk-size must be >= 1")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be >= 1")

    root = Path(__file__).resolve().parents[1]
    membership_path = root / args.membership
    output_path = root / args.output
    audit_path = root / args.audit_output
    symbols = load_membership_symbols(membership_path)
    if args.limit is not None:
        symbols = symbols[:args.limit]
    if not symbols:
        raise SystemExit("No symbols found in historical membership file")

    frames: list[pd.DataFrame] = []
    audit: list[dict] = []

    for offset in range(0, len(symbols), args.chunk_size):
        chunk = symbols[offset:offset + args.chunk_size]
        tickers = [f"{symbol}.NS" for symbol in chunk]
        try:
            data = yf.download(
                tickers,
                start=args.start,
                end=args.end,
                interval="1d",
                auto_adjust=False,
                progress=False,
                threads=True,
                group_by="ticker",
            )
        except Exception as exc:
            for symbol, ticker in zip(chunk, tickers):
                audit.append({
                    "symbol": symbol,
                    "ticker": ticker,
                    "status": "CHUNK_ERROR",
                    "rows": 0,
                    "first_date": None,
                    "last_date": None,
                    "error": str(exc),
                })
            print(f"chunk error {offset + 1}-{offset + len(chunk)}: {exc}")
            continue

        for symbol, ticker in zip(chunk, tickers):
            bars = extract_symbol_bars(data, ticker, symbol)
            if bars.empty:
                status = "NO_DATA_OR_TICKER_UNAVAILABLE"
            else:
                status = "OK"
                frames.append(bars)
            audit.append({
                "symbol": symbol,
                "ticker": ticker,
                "status": status,
                "rows": len(bars),
                "first_date": bars["timestamp"].min().isoformat() if not bars.empty else None,
                "last_date": bars["timestamp"].max().isoformat() if not bars.empty else None,
                "error": None,
            })

        print(f"processed={min(offset + len(chunk), len(symbols))}/{len(symbols)}")

    audit_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(audit).to_csv(audit_path, index=False)

    if not frames:
        print(f"No OHLC data retrieved. Audit: {audit_path}")
        raise SystemExit(1)

    result = pd.concat(frames, ignore_index=True)
    result = result.drop_duplicates(["symbol", "timestamp"]).sort_values(
        ["symbol", "timestamp"]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    audit_frame = pd.DataFrame(audit)
    print(f"requested_symbols={len(symbols)}")
    print(f"symbols_with_data={result['symbol'].nunique()}")
    print(f"rows={len(result)}")
    print(f"data_output={output_path}")
    print(f"audit_output={audit_path}")
    print("\nDownload statuses:")
    print(audit_frame["status"].value_counts(dropna=False).to_string())
    print(
        "\nLimitations: exact source symbols are mapped to Yahoo Finance .NS tickers; "
        "renames, aliases, delisted tickers, corporate actions, and price adjustments "
        "are not resolved by this script. A successful download is not proof of "
        "complete or execution-grade history."
    )


if __name__ == "__main__":
    main()
