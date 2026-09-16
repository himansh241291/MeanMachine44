from datetime import datetime, timedelta, timezone

import pandas as pd

from scripts.measure_type1_outcomes import measure


def frame():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = []
    for i in range(50):
        close = 100 + i
        rows.append({"timestamp": start + timedelta(days=i), "symbol": "TEST", "open": close - 1, "high": close + 1, "low": close - 1, "close": close})
    rows.append({"timestamp": start + timedelta(days=50), "symbol": "TEST", "open": 149, "high": 155, "low": 120, "close": 152})
    rows.append({"timestamp": start + timedelta(days=51), "symbol": "TEST", "open": 152, "high": 156, "low": 150, "close": 154})
    return pd.DataFrame(rows)


def test_measure_counts_later_trigger_only():
    result = measure(frame(), "ma_touch_reclaim", horizon=20)
    assert result["setups"] == 1
    assert result["triggered"] == 1
    assert result["untriggered"] == 0
    assert result["trigger_rate_pct"] == 100.0
    assert result["median_days"] == 1.0


def test_measure_horizon_can_miss_late_trigger():
    result = measure(frame(), "ma_touch_reclaim", horizon=1)
    assert result["setups"] == 1
    assert result["triggered"] == 1


def test_measure_rejects_invalid_horizon():
    try:
        measure(frame(), "ma_touch_reclaim", horizon=0)
    except ValueError as exc:
        assert "horizon" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_measure_rejects_unknown_variant():
    try:
        measure(frame(), "unknown")
    except ValueError as exc:
        assert "unknown variant" in str(exc)
    else:
        raise AssertionError("expected ValueError")
