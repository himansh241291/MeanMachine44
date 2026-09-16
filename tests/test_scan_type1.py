from datetime import datetime, timedelta, timezone

import pandas as pd

from scripts.scan_type1 import find_type1_setups


def test_find_type1_setups_records_later_trigger():
    rows = []
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(44):
        close = 100 + i * 0.5
        rows.append({
            "timestamp": start + timedelta(days=i),
            "symbol": "TEST",
            "open": close - 1,
            "high": close + 1,
            "low": close - 1.5,
            "close": close,
        })
    rows.append({
        "timestamp": start + timedelta(days=44),
        "symbol": "TEST",
        "open": 120,
        "high": 122,
        "low": 110,
        "close": 121,
    })
    rows.append({
        "timestamp": start + timedelta(days=45),
        "symbol": "TEST",
        "open": 121,
        "high": 123,
        "low": 120,
        "close": 122,
    })
    result = find_type1_setups(pd.DataFrame(rows))
    assert len(result) == 1
    assert result[0]["trigger_date"] is not None
    assert result[0]["entry"] == 122.0
    assert result[0]["stop"] == 110.0
