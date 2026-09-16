from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.candles import Candle
from meanmachine44.indicators import sma44
from meanmachine44.ma44 import rising
from meanmachine44.type1_research import local_low_reclaim, ma_touch_reclaim


def compare(daily: pd.DataFrame, lookback: int = 5) -> dict[str, int]:
    daily = daily.sort_values("timestamp").reset_index(drop=True)
    closes = daily["close"].tolist()
    ma = sma44(closes)
    rising_ma = rising(ma, 3)
    counts = {"ma_touch_reclaim": 0, "local_low_reclaim": 0}
    for i, row in daily.iterrows():
        value = ma[i]
        if value is None:
            continue
        candle = Candle(row.open, row.high, row.low, row.close)
        prior_lows = daily.iloc[:i]["low"].tolist()
        counts["ma_touch_reclaim"] += ma_touch_reclaim(candle, value, rising_ma[i])
        counts["local_low_reclaim"] += local_low_reclaim(candle, prior_lows, rising_ma[i], lookback)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--lookback", type=int, default=5)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    frame = pd.read_csv(root / args.input, parse_dates=["timestamp"])
    totals = {"ma_touch_reclaim": 0, "local_low_reclaim": 0}
    for _, daily in frame.groupby("symbol", sort=True):
        counts = compare(daily, args.lookback)
        for name, count in counts.items():
            totals[name] += count

    print(f"lookback={args.lookback}")
    for name, count in totals.items():
        print(f"{name}={count}")


if __name__ == "__main__":
    main()
