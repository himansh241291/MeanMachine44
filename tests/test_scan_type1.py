from datetime import datetime, timedelta, timezone

import pandas as pd

from meanmachine44.candles import Candle
from meanmachine44.indicators import sma44
from meanmachine44.ma44 import rising
from meanmachine44.type1 import type1_candidate
from scripts.scan_type1 import find_type1_setups


def test_find_type1_setups_records_later_trigger():
    rows = []
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(43):
        close = 100 + i * 0.2
        rows.append({
            "timestamp": start + timedelta(days=i),
            "symbol": "TEST",
            "open": close - 0.8,
            "high": close + 0.8,
            "low": close - 1.0,
            "close": close,
        })
    rows.append({
        "timestamp": start + timedelta(days=43),
        "symbol": "TEST",
        "open": 108,
        "high": 110,
        "low": 107,
        "close": 109,
    })
    rows.append({
        "timestamp": start + timedelta(days=44),
        "symbol": "TEST",
        "open": 108,
        "high": 111,
        "low": 107,
        "close": 110,
    })
    result = find_type1_setups(pd.DataFrame(rows))
    assert len(result) == 1
    assert result[0]["setup_date"] == (start + timedelta(days=43)).isoformat()
    assert result[0]["trigger_date"] is not None
    assert result[0]["entry"] == 110.0
    assert result[0]["stop"] == 107.0


def test_find_type1_setups_does_not_trigger_on_setup_bar():
    rows = []
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(43):
        close = 100 + i * 0.2
        rows.append({
            "timestamp": start + timedelta(days=i),
            "symbol": "TEST",
            "open": close - 0.8,
            "high": close + 0.8,
            "low": close - 1.0,
            "close": close,
        })
    rows.append({
        "timestamp": start + timedelta(days=43),
        "symbol": "TEST",
        "open": 108,
        "high": 110,
        "low": 107,
        "close": 109,
    })
    result = find_type1_setups(pd.DataFrame(rows))
    assert result[0]["trigger_date"] is None
