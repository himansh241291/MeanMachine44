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


def test_backtest_records_first_target_after_trigger():
    result = backtest(frame(), "ma_touch_reclaim", horizon=20)
    assert len(result) == 1
    assert result[0]["outcome"] == "1R"
    assert result[0]["r"] == 1.0


def test_backtest_has_triggered_entry_and_stop_geometry():
    result = backtest(frame(), "ma_touch_reclaim", horizon=20)
    assert result[0]["entry"] == 151
    assert result[0]["stop"] == 120
    assert result[0]["risk"] == 31
