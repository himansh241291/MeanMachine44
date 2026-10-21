from datetime import datetime, timezone

import pandas as pd
import pytest

from scripts.merge_historical_price_fallback import merge_missing_bars


def frame(rows):
    return pd.DataFrame(
        rows,
        columns=["timestamp", "symbol", "timeframe", "open", "high", "low", "close"],
    )


def test_merge_fills_missing_keys_without_overwriting_primary():
    primary = frame([
        ["2020-01-02T00:00:00Z", "AAA", "1d", 10, 12, 9, 11],
    ])
    fallback = frame([
        ["2020-01-02T00:00:00Z", "AAA", "1d", 10, 12, 9, 11],
        ["2020-01-03T00:00:00Z", "AAA", "1d", 11, 13, 10, 12],
        ["2020-01-02T00:00:00Z", "BBB", "1d", 20, 22, 19, 21],
    ])
    merged, audit = merge_missing_bars(primary, fallback, "2020-01-01", "2020-01-31")
    assert len(merged) == 3
    assert len(merged[(merged["symbol"] == "AAA") & (merged["timestamp"] == pd.Timestamp("2020-01-02", tz="UTC"))]) == 1
    assert int(audit["fallback_rows_added"].sum()) == 2
    assert int(audit["overlap_ohlc_mismatch_keys"].sum()) == 0


def test_merge_reports_mismatch_and_preserves_primary_values():
    primary = frame([
        ["2020-01-02T00:00:00Z", "AAA", "1d", 10, 12, 9, 11],
    ])
    fallback = frame([
        ["2020-01-02T00:00:00Z", "AAA", "1d", 10, 13, 9, 12],
    ])
    merged, audit = merge_missing_bars(primary, fallback, "2020-01-01", "2020-01-31")
    assert merged.iloc[0]["high"] == 12
    assert merged.iloc[0]["close"] == 11
    assert int(audit["overlap_ohlc_mismatch_keys"].sum()) == 1


def test_merge_rejects_duplicate_keys():
    base = ["2020-01-02T00:00:00Z", "AAA", "1d", 10, 12, 9, 11]
    dup = frame([base, base])
    with pytest.raises(ValueError):
        merge_missing_bars(dup, frame([]), "2020-01-01", "2020-01-31")
