from datetime import datetime, timedelta, timezone

import pandas as pd

from scripts.analyze_type1_timing import delays


def frame():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = []
    for i in range(50):
        close = 100 + i
        rows.append({"timestamp": start + timedelta(days=i), "symbol": "TEST", "open": close - 1, "high": close + 1, "low": close - 1, "close": close})
    rows.append({"timestamp": start + timedelta(days=50), "symbol": "TEST", "open": 149, "high": 155, "low": 120, "close": 152})
    rows.append({"timestamp": start + timedelta(days=51), "symbol": "TEST", "open": 152, "high": 156, "low": 150, "close": 154})
    return pd.DataFrame(rows)


def test_delays_records_first_later_trigger():
    result = delays(frame(), "ma_touch_reclaim", horizon=20)
    assert result == [1]


def test_delays_respects_horizon():
    result = delays(frame(), "ma_touch_reclaim", horizon=0)
    assert result == []
