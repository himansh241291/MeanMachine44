from datetime import date, datetime, timezone

import pytest

from meanmachine44.market import MarketBar
from meanmachine44.universe import (
    HistoricalUniverse,
    MembershipInterval,
    filter_bars,
    load_membership_csv,
)


def test_membership_interval_is_start_inclusive_end_exclusive():
    interval = MembershipInterval("TEST", date(2020, 1, 1), date(2020, 2, 1))
    assert interval.contains(date(2020, 1, 1))
    assert interval.contains(date(2020, 1, 31))
    assert not interval.contains(date(2020, 2, 1))


def test_open_ended_membership():
    interval = MembershipInterval("TEST", date(2020, 1, 1))
    assert interval.contains(date(2030, 1, 1))


def test_overlapping_membership_intervals_are_rejected():
    with pytest.raises(ValueError):
        HistoricalUniverse(
            (
                MembershipInterval("TEST", date(2020, 1, 1), date(2020, 3, 1)),
                MembershipInterval("TEST", date(2020, 2, 1), date(2020, 4, 1)),
            )
        )


def test_adjacent_membership_intervals_are_allowed():
    universe = HistoricalUniverse(
        (
            MembershipInterval("TEST", date(2020, 1, 1), date(2020, 2, 1)),
            MembershipInterval("TEST", date(2020, 2, 1), date(2020, 3, 1)),
        )
    )
    assert universe.contains("TEST", date(2020, 2, 1))


def test_symbols_at():
    universe = HistoricalUniverse(
        (
            MembershipInterval("AAA", date(2020, 1, 1), date(2020, 2, 1)),
            MembershipInterval("BBB", date(2020, 1, 15)),
        )
    )
    assert universe.symbols_at(date(2020, 1, 10)) == {"AAA"}
    assert universe.symbols_at(date(2020, 1, 20)) == {"AAA", "BBB"}


def test_load_membership_csv(tmp_path):
    path = tmp_path / "membership.csv"
    path.write_text(
        "symbol,effective_from,effective_to\n"
        "AAA,2020-01-01,2020-02-01\n"
        "BBB,2020-02-01,\n",
        encoding="utf-8",
    )
    universe = load_membership_csv(path)
    assert universe.contains("AAA", date(2020, 1, 15))
    assert universe.contains("BBB", date(2030, 1, 1))


def test_load_membership_csv_requires_columns(tmp_path):
    path = tmp_path / "membership.csv"
    path.write_text("symbol,effective_from\nAAA,2020-01-01\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_membership_csv(path)


def test_filter_bars_uses_membership_dates():
    bars = [
        MarketBar(datetime(2020, 1, 15, tzinfo=timezone.utc), "AAA", "1d", 1, 2, 1, 2),
        MarketBar(datetime(2020, 2, 15, tzinfo=timezone.utc), "AAA", "1d", 1, 2, 1, 2),
        MarketBar(datetime(2020, 1, 15, tzinfo=timezone.utc), "BBB", "1d", 1, 2, 1, 2),
    ]
    universe = HistoricalUniverse(
        (
            MembershipInterval("AAA", date(2020, 1, 1), date(2020, 2, 1)),
            MembershipInterval("BBB", date(2020, 2, 1)),
        )
    )
    filtered = filter_bars(bars, universe)
    assert [bar.symbol for bar in filtered] == ["AAA"]
