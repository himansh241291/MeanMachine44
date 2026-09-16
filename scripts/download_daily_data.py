from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import yfinance as yf


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("symbols", nargs="+", help="Yahoo Finance symbols, e.g. RELIANCE.NS")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--output", default="data/raw/market.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    frames = []
    for symbol in args.symbols:
        df = yf.download(
            symbol,
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
        x["symbol"] = symbol.removesuffix(".NS")
        x["timeframe"] = "1d"
        x = x.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close"})
        frames.append(x[["timestamp", "symbol", "timeframe", "open", "high", "low", "close"]])

    if not frames:
        raise SystemExit("No historical data returned")

    pd.concat(frames, ignore_index=True).sort_values(["symbol", "timestamp"]).to_csv(output, index=False)
    print(output)


if __name__ == "__main__":
    main()
