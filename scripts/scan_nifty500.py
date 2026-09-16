from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.scan import passes_ma44_scan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--output", default="data/output/nifty500_ma44_scan.csv")
    parser.add_argument("--as-of", help="UTC date YYYY-MM-DD; defaults to latest data")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    frame = pd.read_csv(root / args.input, parse_dates=["timestamp"])
    frame = frame.sort_values(["symbol", "timestamp"])
    as_of = pd.Timestamp(args.as_of, tz="UTC") if args.as_of else frame["timestamp"].max()
    frame = frame[frame["timestamp"] <= as_of]

    rows = []
    for symbol, daily in frame.groupby("symbol", sort=True):
        daily = daily.set_index("timestamp")
        weekly = daily.resample("W-FRI").agg(
            open=("open", "first"),
            high=("high", "max"),
            low=("low", "min"),
            close=("close", "last"),
        ).dropna()
        if passes_ma44_scan(weekly["close"].tolist(), daily["close"].tolist()):
            rows.append({"symbol": symbol, "as_of": as_of.date().isoformat()})

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=["symbol", "as_of"]).to_csv(output, index=False)
    print(f"candidates={len(rows)} output={output}")


if __name__ == "__main__":
    main()
