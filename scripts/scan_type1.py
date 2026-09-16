from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.candles import Candle
from meanmachine44.indicators import sma44
from meanmachine44.ma44 import rising
from meanmachine44.type1 import type1_candidate


def find_type1_setups(daily: pd.DataFrame) -> list[dict]:
    daily = daily.sort_values("timestamp").reset_index(drop=True)
    closes = daily["close"].tolist()
    ma = sma44(closes)
    rising_ma = rising(ma, 3)
    rows = []
    for i, row in daily.iterrows():
        value = ma[i]
        if value is None:
            continue
        candle = Candle(row.open, row.high, row.low, row.close)
        if not type1_candidate(candle, value, rising_ma[i]):
            continue
        trigger = None
        for j in range(i + 1, len(daily)):
            if daily.iloc[j]["high"] > candle.high:
                trigger = daily.iloc[j]
                break
        rows.append({
            "symbol": row.symbol,
            "setup_date": row.timestamp.isoformat(),
            "setup_high": candle.high,
            "setup_low": candle.low,
            "setup_close": candle.close,
            "daily_sma44": value,
            "trigger_date": None if trigger is None else trigger["timestamp"].isoformat(),
            "entry": None if trigger is None else candle.high,
            "stop": candle.low,
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--output", default="data/output/nifty500_type1_setups.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    frame = pd.read_csv(root / args.input, parse_dates=["timestamp"])
    rows = []
    for _, daily in frame.groupby("symbol", sort=True):
        rows.extend(find_type1_setups(daily))

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    print(f"setups={len(rows)} triggered={sum(row['trigger_date'] is not None for row in rows)} output={output}")


if __name__ == "__main__":
    main()
