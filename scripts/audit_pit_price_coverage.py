from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

from meanmachine44.universe import HistoricalUniverse, load_membership_csv


def yearly_coverage(
    market: pd.DataFrame,
    universe: HistoricalUniverse,
    start: str = "2018-01-01",
    end: str = "2026-03-30",
) -> pd.DataFrame:
    required = {"timestamp", "symbol"}
    if not required.issubset(market.columns):
        raise ValueError("market data must contain timestamp and symbol")

    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)
    if end_date < start_date:
        raise ValueError("end must be on or after start")

    frame = market[["timestamp", "symbol"]].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="raise")
    frame["symbol"] = frame["symbol"].astype(str).str.strip()
    all_price_symbols = set(frame["symbol"])
    rows = []

    for year in range(start_date.year, end_date.year + 1):
        period_start = max(start_date, date(year, 1, 1))
        period_end = min(end_date, date(year, 12, 31))
        members = {
            interval.symbol
            for interval in universe.intervals
            if interval.effective_from <= period_end
            and (interval.effective_to is None or interval.effective_to > period_start)
        }
        period = frame[
            (frame["timestamp"].dt.date >= period_start)
            & (frame["timestamp"].dt.date <= period_end)
        ]
        period_price_symbols = set(period["symbol"])
        members_with_prices = members & period_price_symbols
        rows.append(
            {
                "year": year,
                "period_start": period_start.isoformat(),
                "period_end": period_end.isoformat(),
                "active_members_in_history": len(members),
                "active_members_with_prices_in_period": len(members_with_prices),
                "active_members_missing_prices_in_period": len(members - period_price_symbols),
                "active_members_without_any_price_history": len(members - all_price_symbols),
                "price_symbols_in_period": len(period_price_symbols),
                "price_rows_in_period": len(period),
                "period_member_coverage_pct": (
                    100 * len(members_with_prices) / len(members) if members else None
                ),
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit price-history coverage against historical index membership."
    )
    parser.add_argument("--market", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--membership", default="data/raw/nifty500_membership.csv")
    parser.add_argument("--start", default="2018-01-01")
    parser.add_argument("--end", default="2026-03-30")
    parser.add_argument("--output", default="data/output/pit_price_coverage.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    market = pd.read_csv(root / args.market, usecols=["timestamp", "symbol"])
    universe = load_membership_csv(root / args.membership)
    result = yearly_coverage(market, universe, args.start, args.end)

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print(result.to_string(index=False))
    print(f"output={output}")
    print(
        "Note: matching is exact-symbol only; symbol aliases and price-adjustment "
        "quality are not assessed by this audit."
    )


if __name__ == "__main__":
    main()
