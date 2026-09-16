from datetime import datetime, timedelta, timezone

import pandas as pd

from scripts.compare_type1_research import compare


def test_compare_type1_research_variants():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    rows = []
    for i in range(50):
        close = 100 + i
        rows.append({
            "timestamp": start + timedelta(days=i),
            "symbol": "TEST",
            "open": close - 1,
            "high": close + 1,
            "low": close - 1,
            "close": close,
        })
    rows.append({
        "timestamp": start + timedelta(days=50),
        "symbol": "TEST",
        "open": 149,
        "high": 151,
        "low": 145,
        "close": 150,
    })
    frame = pd.DataFrame(rows)
    result = compare(frame, lookback=5)
    assert result["ma_touch_reclaim"] == 0
    assert result["local_low_reclaim"] == 0
