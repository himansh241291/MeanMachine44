from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass(frozen=True)
class MembershipInterval:
    symbol: str
    effective_from: date
    effective_to: date | None = None

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required")
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be after effective_from")

    def contains(self, as_of: date | datetime) -> bool:
        value = as_of.date() if isinstance(as_of, datetime) else as_of
        return self.effective_from <= value and (
            self.effective_to is None or value < self.effective_to
        )


@dataclass(frozen=True)
class HistoricalUniverse:
    intervals: tuple[MembershipInterval, ...]

    def __post_init__(self) -> None:
        grouped: dict[str, list[MembershipInterval]] = {}
        for interval in self.intervals:
            grouped.setdefault(interval.symbol, []).append(interval)
        for symbol, items in grouped.items():
            ordered = sorted(items, key=lambda item: item.effective_from)
            for previous, current in zip(ordered, ordered[1:]):
                if previous.effective_to is None or current.effective_from < previous.effective_to:
                    raise ValueError(f"overlapping membership intervals for {symbol}")

    def contains(self, symbol: str, as_of: date | datetime) -> bool:
        return any(
            interval.symbol == symbol and interval.contains(as_of)
            for interval in self.intervals
        )

    def symbols_at(self, as_of: date | datetime) -> set[str]:
        return {
            interval.symbol
            for interval in self.intervals
            if interval.contains(as_of)
        }


def load_membership_csv(path: str | Path) -> HistoricalUniverse:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        required = {"symbol", "effective_from", "effective_to"}
        if not rows.fieldnames or not required.issubset(rows.fieldnames):
            raise ValueError(
                "membership CSV must contain symbol,effective_from,effective_to"
            )
        intervals = []
        for row in rows:
            symbol = row["symbol"].strip()
            effective_from = date.fromisoformat(row["effective_from"].strip())
            raw_to = row["effective_to"].strip()
            effective_to = date.fromisoformat(raw_to) if raw_to else None
            intervals.append(
                MembershipInterval(symbol, effective_from, effective_to)
            )
    return HistoricalUniverse(tuple(intervals))


def filter_bars(bars: list[object], universe: HistoricalUniverse) -> list[object]:
    return [
        bar
        for bar in bars
        if universe.contains(
            bar.symbol if hasattr(bar, "symbol") else bar["symbol"],
            bar.timestamp if hasattr(bar, "timestamp") else datetime.fromisoformat(bar["timestamp"]),
        )
    ]
