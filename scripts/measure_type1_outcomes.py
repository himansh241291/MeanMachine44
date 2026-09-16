from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.candles import Candle
from meanmachine44.indicators import sma44
from meanmachine44.ma44 import rising
from meanmachine44.type1_research import local_low_reclaim, ma_touch_reclaim


def measure(daily: pd.DataFrame, variant: str, lookback: int = 5) -> dict[str, int | float | None]:
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
        if variant == "ma_touch_reclaim":
            qualifies = ma_touch_reclaim(candle, value, rising_ma[i])
        elif variant == "local_low_reclaim":
            qualifies = local_low_reclaim(candle, prior_lows, rising_ma[i], lookback)
        else:
            raise ValueError(f"unknown variant: {variant}")
        if not qualifies:
            continue

        setups += 1
        for j in range(i + 1, len(daily)):
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
        "max_days": None if not delays else max(delays),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--lookback", type=int, default=5)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    frame = pd.read_csv(root / args.input, parse_dates=["timestamp"])
    totals = {name: {"setups": 0, "triggered": 0} for name in ("ma_touch_reclaim", "local_low_reclaim")}
    delays = {name: [] for name in totals}

    for _, daily in frame.groupby("symbol", sort=True):
        for name in totals:
            result = measure(daily, name, args.lookback)
            totals[name]["setups"] += int(result["setups"])
            totals[name]["triggered"] += int(result["triggered"])
            if result["median_days"] is not None:
                delays[name].append(result["median_days"])

    for name in totals:
        setups = totals[name]["setups"]
        triggered = totals[name]["triggered"]
        rate = 0 if setups == 0 else round(triggered * 100 / setups, 2)
        print(f"{name}: setups={setups} triggered={triggered} untriggered={setups-triggered} trigger_rate_pct={rate}")


if __name__ == "__main__":
    main()
