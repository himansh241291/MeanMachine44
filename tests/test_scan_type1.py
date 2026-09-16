from datetime import datetime, timezone

import pandas as pd

from scripts.scan_type1 import find_type1_setups


def test_find_type1_setups_records_later_trigger():
    closes = [100 + i for i in range(50)]
    rows = []
    for i, close in enumerate(closes):
        rows.append({
            "timestamp": datetime(2026, 1, 1 + i, tzinfo=timezone.utc),
            "symbol": "TEST",
            "open": close - 1,
            "high": close + 1,
            "low": close - 2,
            "close": close,
        })
    frame = pd.DataFrame(rows)
    assert find_type1_setups(frame) == []
