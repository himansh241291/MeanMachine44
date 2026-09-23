from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.candles import Candle
from meanmachine44.indicators import sma44
from meanmachine44.ma44 import rising
from meanmachine44.trade_research import first_touch_event, levels
from meanmachine44.type1_research import local_low_reclaim, ma_touch_reclaim
from meanmachine44.universe import HistoricalUniverse, load_membership_csv

VARIANTS = ("ma_touch_reclaim", "local_low_reclaim")
TARGETS = (1, 2, 3)


def qualifies(candle, value, rising_now, prior_lows, variant, lookback):
    if variant == "ma_touch_reclaim":
        return ma_touch_reclaim(candle, value, rising_now)
    return local_low_reclaim(candle, prior_lows, rising_now, lookback)


def backtest(
    daily: pd.DataFrame,
    variant: str,
    horizon: int = 20,
    lookback: int = 5,
    universe: HistoricalUniverse | None = None,
    start: str | None = None,
    end: str | None = None,
) -> list[dict]:
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    daily = daily.sort_values("timestamp").reset_index(drop=True)
    ma = sma44(daily["close"].tolist())
    rising_ma = rising(ma, 3)
    trades = []
    for i, row in daily.iterrows():
        value = ma[i]
        if value is None:
            continue
        if start is not None and row.timestamp < pd.Timestamp(start, tz="UTC"):
            continue
        if end is not None and row.timestamp > pd.Timestamp(end, tz="UTC"):
            continue
        if universe is not None and not universe.contains(row.symbol, row.timestamp):
            continue
        candle = Candle(row.open, row.high, row.low, row.close)
        prior_lows = daily.iloc[:i]["low"].tolist()
        if not qualifies(candle, value, rising_ma[i], prior_lows, variant, lookback):
            continue
        trigger = None
        scan_end = min(i + horizon + 1, len(daily))
        if end is not None:
            cutoff = pd.Timestamp(end, tz="UTC")
            while scan_end > i + 1 and daily.iloc[scan_end - 1]["timestamp"] > cutoff:
                scan_end -= 1
        for j in range(i + 1, scan_end):
            if daily.iloc[j]["high"] > candle.high:
                trigger = j
                break
        if trigger is None:
            continue
        entry = candle.high
        stop = candle.low
        if entry <= stop:
            continue
        risk = entry - stop
        target_levels = levels(entry, stop)
        future_highs = daily.iloc[trigger + 1:scan_end]["high"].tolist()
        future_lows = daily.iloc[trigger + 1:scan_end]["low"].tolist()
        for multiple in TARGETS:
            raw_outcome, offset = first_touch_event(
                future_highs,
                future_lows,
                {f"{multiple}R": target_levels[f"{multiple}R"]},
                stop,
            )
            outcome = "STOP" if raw_outcome == "STOP" else "TARGET" if raw_outcome else None
            r_value = -1.0 if outcome == "STOP" else float(multiple) if outcome == "TARGET" else None
            exit_index = trigger + 1 + offset if offset is not None else None
            trades.append({
                "symbol": row.symbol,
                "setup_date": row.timestamp.isoformat(),
                "trigger_date": daily.iloc[trigger]["timestamp"].isoformat(),
                "exit_date": daily.iloc[exit_index]["timestamp"].isoformat() if exit_index is not None else None,
                "entry": entry,
                "stop": stop,
                "risk": risk,
                "target_multiple": multiple,
                "target": target_levels[f"{multiple}R"],
                "outcome": outcome,
                "r": r_value,
                "variant": variant,
            })
    return trades


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--horizon", type=int, default=20)
    parser.add_argument("--lookback", type=int, default=5)
    parser.add_argument("--membership")
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--output", default="data/output/type1_trades.csv")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    frame = pd.read_csv(root / args.input, parse_dates=["timestamp"])
    universe = load_membership_csv(root / args.membership) if args.membership else None
    rows = []
    for _, daily in frame.groupby("symbol", sort=True):
        for variant in VARIANTS:
            rows.extend(
                backtest(
                    daily,
                    variant,
                    args.horizon,
                    args.lookback,
                    universe,
                    args.start,
                    args.end,
                )
            )
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    result = pd.DataFrame(rows)
    for variant in VARIANTS:
        part = result[result.variant == variant]
        print(variant)
        for multiple in TARGETS:
            target_part = part[part.target_multiple == multiple]
            counts = target_part.outcome.fillna("NONE").value_counts().to_dict()
            total_r = target_part["r"].dropna().sum()
            avg_r = target_part["r"].dropna().mean()
            print(
                f"  {multiple}R: trades={len(target_part)} stop={counts.get('STOP', 0)} "
                f"target={counts.get('TARGET', 0)} none={counts.get('NONE', 0)} "
                f"total_r={total_r:.2f} avg_r={avg_r:.4f}"
            )


if __name__ == "__main__":
    main()
