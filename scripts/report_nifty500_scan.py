from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.indicators import sma44
from meanmachine44.scan import passes_ma44_scan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--scan", default="data/output/nifty500_ma44_scan.csv")
    parser.add_argument("--output", default="data/output/nifty500_ma44_report.csv")
    parser.add_argument("--as-of", help="UTC date YYYY-MM-DD; defaults to latest data")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    frame = pd.read_csv(root / args.input, parse_dates=["timestamp"])
    frame = frame.sort_values(["symbol", "timestamp"])
    as_of = pd.Timestamp(args.as_of, tz="UTC") if args.as_of else frame["timestamp"].max()
    frame = frame[frame["timestamp"] <= as_of]
    scan = pd.read_csv(root / args.scan)
    candidates = set(scan["symbol"])

    rows = []
    for symbol, daily in frame.groupby("symbol", sort=True):
        if symbol not in candidates:
            continue
        daily = daily.set_index("timestamp")["close"]
        weekly = daily.resample("W-FRI").last().dropna()
        daily_ma = sma44(daily.tolist())
        weekly_ma = sma44(weekly.tolist())
        rows.append({
            "symbol": symbol,
            "as_of": as_of.date().isoformat(),
            "close": daily.iloc[-1],
            "daily_sma44": daily_ma[-1],
            "daily_sma44_prev": daily_ma[-2],
            "weekly_sma44": weekly_ma[-1],
            "weekly_sma44_prev": weekly_ma[-2],
        })

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"candidates={len(rows)} output={output}")


if __name__ == "__main__":
    main()
