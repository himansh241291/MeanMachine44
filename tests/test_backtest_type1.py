from datetime import datetime, timedelta, timezone

import pandas as pd

from scripts.backtest_type1 import backtest


def frame():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = []
    for i in range(50):
        close = 100 + i
        rows.append({"timestamp": start + timedelta(days=i), "symbol": "TEST", "open": close - 1, "high": close + 1, "low": close - 1, "close": close})
    rows.append({"timestamp": start + timedelta(days=50), "symbol": "TEST", "open": 134, "high": 151, "low": 120, "close": 136})
    rows.append({"timestamp": start + timedelta(days=51), "symbol": "TEST", "open": 136, "high": 155, "low": 130, "close": 150})
    rows.append({"timestamp": start + timedelta(days=52), "symbol": "TEST", "open": 150, "high": 185, "low": 145, "close": 180})
    return pd.DataFrame(rows)


def test_backtest_records_target_per_multiple():
    result = backtest(frame(), "ma_touch_reclaim", horizon=20)
    assert len(result) == 3
    one_r = next(row for row in result if row["target_multiple"] == 1)
    assert one_r["outcome"] == "TARGET"
    assert one_r["r"] == 1.0


def test_backtest_has_triggered_entry_and_stop_geometry():
    result = backtest(frame(), "ma_touch_reclaim", horizon=20)
    one_r = next(row for row in result if row["target_multiple"] == 1)
    assert one_r["entry"] == 151
    assert one_r["stop"] == 120
    assert one_r["risk"] == 31


def test_backtest_applies_point_in_time_membership_to_setup_date():
    from datetime import date

    from meanmachine44.universe import HistoricalUniverse, MembershipInterval

    universe = HistoricalUniverse(
        (MembershipInterval("TEST", date(2026, 2, 21)),)
    )
    assert backtest(
        frame(),
        "ma_touch_reclaim",
        horizon=20,
        universe=universe,
    ) == []


def test_backtest_keeps_price_history_for_indicator_warmup():
    from datetime import date

    from meanmachine44.universe import HistoricalUniverse, MembershipInterval

    universe = HistoricalUniverse(
        (MembershipInterval("TEST", date(2026, 2, 1)),)
    )
    result = backtest(
        frame(),
        "ma_touch_reclaim",
        horizon=20,
        universe=universe,
    )
    assert len(result) == 3
