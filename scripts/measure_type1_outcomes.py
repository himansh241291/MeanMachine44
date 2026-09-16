from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.candles import Candle
from meanmachine44.indicators import sma44
from meanmachine44.ma44 import rising
from meanmachine44.type1_research import local_low_reclaim, ma_touch_reclaim


VARIANTS = ("ma_touch_reclaim", "local_low_reclaim")


def qualifies(candle: Candle, value: float, rising_now: bool, prior_lows: list[float], variant: str, lookback: int) -> bool:
    if variant == "ma_touch_reclaim":
        return ma_touch_reclaim(candle, value, rising_now)
    if variant == "local_low_reclaim":
        return local_low_reclaim(candle, prior_lows, rising_now, lookback)
    raise ValueError(f"unknown variant: {variant}")


def measure(daily: pd.DataFrame, variant: str, horizon: int = 20, lookback: int = 5) -> dict[str, int | float | None]:
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    daily = daily.sort_values("timestamp").reset_index(drop=True)
    ma = sma44(daily["close"].tolist())
    rising_ma = rising(ma, 3)
    setups = 0
    triggered = 0
    delays: list[int] = []

    for i, row in daily.iterrows():
        value = ma[i]
        if value is None:
            continue
        candle = Candle(row.open, row.high, row.low, row.close)
        prior_lows = daily.iloc[:i]["low"].tolist()
        if not qualifies(candle, value, rising_ma[i], prior_lows, variant, lookback):
            continue
        setups += 1
        end = min(i + horizon + 1, len(daily))
        for j in range(i + 1, end):
            if daily.iloc[j]["high"] > candle.high:
                triggered += 1
                delays.append(j - i)
                break

    return {
        "setups": setups,
        "triggered": triggered,
        "untriggered": setups - triggered,
        "trigger_rate_pct": None if setups == 0 else round(triggered * 100 / setups, 2),
        "median_days": None if not delays else float(pd.Series(delays).median()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--horizon", type=int, default=20)
    parser.add_argument("--lookback", type=int, default=5)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    frame = pd.read_csv(root / args.input, parse_dates=["timestamp"])

    for name in VARIANTS:
        totals = {"setups": 0, "triggered": 0}
        delays: list[float] = []
        for _, daily in frame.groupby("symbol", sort=True):
            result = measure(daily, name, args.horizon, args.lookback)
            totals["setups"] += int(result["setups"])
            totals["triggered"] += int(result["triggered"])
            if result["median_days"] is not None:
                delays.append(float(result["median_days"]))
        setups = totals["setups"]
        triggered = totals["triggered"]
        rate = None if setups == 0 else round(triggered * 100 / setups, 2)
        median_of_symbol_medians = None if not delays else round(float(pd.Series(delays).median()), 2)
        print(
            f"{name}: horizon_days={args.horizon} setups={setups} "
            f"triggered={triggered} untriggered={setups-triggered} "
            f"trigger_rate_pct={rate} median_symbol_median_days={median_of_symbol_medians}"
        )


if __name__ == "__main__":
    main()
