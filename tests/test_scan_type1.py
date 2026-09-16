from datetime import datetime, timedelta, timezone

import pandas as pd

from scripts.scan_type1 import find_type1_setups


def warmup(start: datetime) -> list[dict]:
    rows = []
    for i in range(45):
        close = 100 + i
        rows.append({
            "timestamp": start + timedelta(days=i),
            "symbol": "TEST",
            "open": close - 1,
            "high": close + 1,
            "low": close - 1,
            "close": close,
        })
    return rows


def test_find_type1_setups_records_later_trigger():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = warmup(start)
    rows.append({
        "timestamp": start + timedelta(days=45),
        "symbol": "TEST",
        "open": 144,
        "high": 148,
        "low": 120,
        "close": 145,
    })
    rows.append({
        "timestamp": start + timedelta(days=46),
        "symbol": "TEST",
        "open": 145,
        "high": 149,
        "low": 144,
        "close": 148,
    })

    result = find_type1_setups(pd.DataFrame(rows))

    assert len(result) == 1
    assert result[0]["setup_date"] == (start + timedelta(days=45)).isoformat()
    assert result[0]["trigger_date"] == (start + timedelta(days=46)).isoformat()
    assert result[0]["entry"] == 148.0
    assert result[0]["stop"] == 120.0


def test_find_type1_setups_does_not_trigger_on_setup_bar():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = warmup(start)
    rows.append({
        "timestamp": start + timedelta(days=45),
        "symbol": "TEST",
        "open": 144,
        "high": 148,
        "low": 120,
        "close": 145,
    })

    result = find_type1_setups(pd.DataFrame(rows))

    assert len(result) == 1
    assert result[0]["trigger_date"] is None
