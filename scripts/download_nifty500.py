from __future__ import annotations

import argparse
import io
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

CONSTITUENT_URL = "https://www.niftyindices.com/IndexConstituent/ind_nifty500list.csv"
REQUIRED = {"Symbol"}


def load_constituents(data: bytes) -> list[str]:
    frame = pd.read_csv(io.BytesIO(data))
    if not REQUIRED.issubset(frame.columns):
        raise ValueError("NIFTY 500 CSV must contain Symbol")
    return sorted(frame["Symbol"].dropna().astype(str).str.strip().unique())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--output", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(CONSTITUENT_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    response.raise_for_status()
    symbols = load_constituents(response.content)
    if args.limit:
        symbols = symbols[:args.limit]

    frames = []
    for symbol in symbols:
        df = yf.download(
            f"{symbol}.NS",
            start=args.start,
            end=args.end,
            interval="1d",
            auto_adjust=False,
            progress=False,
            threads=False,
        )
        if df.empty:
            continue
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        x = df[["Open", "High", "Low", "Close"]].dropna().copy()
        x["timestamp"] = pd.to_datetime(x.index, utc=True)
        x["symbol"] = symbol
        x["timeframe"] = "1d"
        x = x.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close"})
        frames.append(x[["timestamp", "symbol", "timeframe", "open", "high", "low", "close"]])

    if not frames:
        raise SystemExit("No historical data returned")

    pd.concat(frames, ignore_index=True).sort_values(["symbol", "timestamp"]).to_csv(output, index=False)
    print(f"symbols={len(symbols)} rows={sum(len(frame) for frame in frames)} output={output}")


if __name__ == "__main__":
    main()
