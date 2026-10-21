from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

try:
    from download_historical_membership_prices import (
        OUTPUT_COLUMNS,
        extract_symbol_bars,
    )
except ModuleNotFoundError:
    from scripts.download_historical_membership_prices import (
        OUTPUT_COLUMNS,
        extract_symbol_bars,
    )


def missing_symbols(audit: pd.DataFrame) -> list[str]:
    required = {"symbol", "status"}
    if not required.issubset(audit.columns):
        raise ValueError("download audit must contain symbol,status")
    frame = audit.copy()
    frame["symbol"] = frame["symbol"].astype(str).str.strip()
    status = frame["status"].astype(str).str.strip().str.upper()
    return sorted(
        symbol
        for symbol in frame.loc[status != "OK", "symbol"].dropna().unique()
        if symbol and symbol.casefold() != "nan"
    )


def merge_price_frames(base: pd.DataFrame, recovered: pd.DataFrame) -> pd.DataFrame:
    required = set(OUTPUT_COLUMNS)
    for label, frame in (("base", base), ("recovered", recovered)):
        if not required.issubset(frame.columns):
            raise ValueError(f"{label} price frame missing required OHLC columns")

    combined = pd.concat(
        [base[OUTPUT_COLUMNS], recovered[OUTPUT_COLUMNS]],
        ignore_index=True,
    )
    combined["timestamp"] = pd.to_datetime(combined["timestamp"], utc=True, errors="raise")
    combined["symbol"] = combined["symbol"].astype(str).str.strip()
    combined["timeframe"] = combined["timeframe"].astype(str).str.strip()
    combined = combined.drop_duplicates(
        ["timestamp", "symbol", "timeframe"], keep="last"
    )
    return combined.sort_values(["symbol", "timestamp"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Retry only symbols without data in the prior historical-membership "
            "download audit, one ticker at a time."
        )
    )
    parser.add_argument(
        "--market",
        default="data/raw/nifty500_membership_daily_yfinance.csv",
    )
    parser.add_argument(
        "--audit",
        default="data/output/historical_membership_download_audit.csv",
    )
    parser.add_argument("--start", default="2017-10-01")
    parser.add_argument("--end", default="2026-03-31", help="Exclusive end date.")
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--pause", type=float, default=0.5)
    parser.add_argument(
        "--output",
        default="data/raw/nifty500_membership_daily_yfinance_retry.csv",
    )
    parser.add_argument(
        "--retry-audit",
        default="data/output/historical_membership_download_retry_audit.csv",
    )
    args = parser.parse_args()
    if args.retries < 1 or args.timeout <= 0 or args.pause < 0:
        parser.error("--retries must be >= 1, --timeout > 0, and --pause >= 0")

    root = Path(__file__).resolve().parents[1]
    market_path = root / args.market
    audit_path = root / args.audit
    if not market_path.is_file() or not audit_path.is_file():
        raise SystemExit("Existing market file and first-pass download audit are required")

    base = pd.read_csv(market_path)
    audit = pd.read_csv(audit_path)
    symbols = missing_symbols(audit)
    recovered_frames: list[pd.DataFrame] = []
    retry_rows: list[dict] = []

    print(f"symbols_to_retry={len(symbols)}")
    for index, symbol in enumerate(symbols, start=1):
        ticker = f"{symbol}.NS"
        bars = pd.DataFrame(columns=OUTPUT_COLUMNS)
        errors: list[str] = []
        attempts = 0

        for attempts in range(1, args.retries + 1):
            try:
                data = yf.download(
                    ticker,
                    start=args.start,
                    end=args.end,
                    interval="1d",
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                    timeout=args.timeout,
                )
                bars = extract_symbol_bars(data, ticker, symbol)
            except Exception as exc:
                errors.append(f"attempt {attempts}: {type(exc).__name__}: {exc}")
                bars = pd.DataFrame(columns=OUTPUT_COLUMNS)

            if not bars.empty:
                break
            if attempts < args.retries:
                time.sleep(args.pause * attempts)

        if not bars.empty:
            status = "RECOVERED"
            recovered_frames.append(bars)
        elif errors:
            status = "RETRY_ERROR"
        else:
            status = "NO_DATA_AFTER_RETRY"

        retry_rows.append(
            {
                "symbol": symbol,
                "ticker": ticker,
                "status": status,
                "attempts": attempts,
                "rows": len(bars),
                "first_date": bars["timestamp"].min().isoformat() if not bars.empty else None,
                "last_date": bars["timestamp"].max().isoformat() if not bars.empty else None,
                "error": " | ".join(errors) if errors else None,
            }
        )
        if index % 10 == 0 or index == len(symbols):
            recovered_count = sum(row["status"] == "RECOVERED" for row in retry_rows)
            print(f"processed={index}/{len(symbols)} recovered={recovered_count}")

    if recovered_frames:
        recovered = pd.concat(recovered_frames, ignore_index=True)
    else:
        recovered = pd.DataFrame(columns=OUTPUT_COLUMNS)

    merged = merge_price_frames(base, recovered)
    output_path = root / args.output
    retry_audit_path = root / args.retry_audit
    output_path.parent.mkdir(parents=True, exist_ok=True)
    retry_audit_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)
    pd.DataFrame(retry_rows).to_csv(retry_audit_path, index=False)

    print(f"recovered_symbols={sum(row['status'] == 'RECOVERED' for row in retry_rows)}")
    print(f"merged_symbols={merged['symbol'].nunique()}")
    print(f"merged_rows={len(merged)}")
    print(f"data_output={output_path}")
    print(f"retry_audit={retry_audit_path}")
    print("\nRetry statuses:")
    if retry_rows:
        print(pd.DataFrame(retry_rows)["status"].value_counts().to_string())
    else:
        print("No symbols required retry.")
    print(
        "\nThis retry only addresses retrieval failures. It does not resolve old/new "
        "symbol aliases, delisting coverage, or corporate-action adjustments."
    )


if __name__ == "__main__":
    main()
