from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.candles import Candle
from meanmachine44.indicators import sma44
from meanmachine44.ma44 import rising
from meanmachine44.type1_research import local_low_reclaim, ma_touch_reclaim


def delays(daily: pd.DataFrame, variant: str, horizon: int, lookback: int = 5) -> list[int]:
    daily = daily.sort_values("timestamp").reset_index(drop=True)
    ma = sma44(daily["close"].tolist())
    rising_ma = rising(ma, 3)
    result: list[int] = []
    for i, row in daily.iterrows():
        value = ma[i]
        if value is None:
            continue
        candle = Candle(row.open, row.high, row.low, row.close)
        prior_lows = daily.iloc[:i]["low"].tolist()
        if variant == "ma_touch_reclaim":
            qualifies = ma_touch_reclaim(candle, value, rising_ma[i])
        elif variant == "local_low_reclaim":
            qualifies = local_low_reclaim(candle, prior_lows, rising_ma[i], lookback)
        else:
            raise ValueError(f"unknown variant: {variant}")
        if not qualifies:
            continue
        end = min(i + horizon + 1, len(daily))
        for j in range(i + 1, end):
            if daily.iloc[j]["high"] > candle.high:
                result.append(j - i)
                break
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--horizon", type=int, default=20)
    parser.add_argument("--lookback", type=int, default=5)
    args = parser.parse_args()
    if args.horizon < 1:
        raise ValueError("horizon must be >= 1")

    root = Path(__file__).resolve().parents[1]
    frame = pd.read_csv(root / args.input, parse_dates=["timestamp"])
    print(f"horizon_days={args.horizon} lookback={args.lookback}")
    for variant in ("ma_touch_reclaim", "local_low_reclaim"):
        values: list[int] = []
        for _, daily in frame.groupby("symbol", sort=True):
            values.extend(delays(daily, variant, args.horizon, args.lookback))
        series = pd.Series(values)
        print(
            f"{variant}: n={len(values)} median={series.median():.1f} "
            f"p25={series.quantile(.25):.1f} p75={series.quantile(.75):.1f} "
            f"day1={sum(v == 1 for v in values)} day2_5={sum(2 <= v <= 5 for v in values)} "
            f"day6_20={sum(6 <= v <= args.horizon for v in values)}"
        )


if __name__ == "__main__":
    main()
