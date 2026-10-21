import pandas as pd
import pytest

from scripts.retry_historical_membership_prices import (
    merge_price_frames,
    missing_symbols,
)


def test_missing_symbols_returns_only_non_ok_unique_symbols():
    audit = pd.DataFrame(
        {
            "symbol": ["AAA", "BBB", "AAA", "CCC"],
            "status": ["OK", "NO_DATA_OR_TICKER_UNAVAILABLE", "RETRY_ERROR", "OK"],
        }
    )
    assert missing_symbols(audit) == ["AAA", "BBB"]


def test_missing_symbols_requires_columns():
    with pytest.raises(ValueError):
        missing_symbols(pd.DataFrame({"symbol": ["AAA"]}))


def test_merge_price_frames_deduplicates_and_sorts():
    columns = ["timestamp", "symbol", "timeframe", "open", "high", "low", "close"]
    base = pd.DataFrame(
        [
            ["2020-01-02T00:00:00Z", "AAA", "1d", 10, 12, 9, 11],
            ["2020-01-03T00:00:00Z", "AAA", "1d", 11, 13, 10, 12],
        ],
        columns=columns,
    )
    recovered = pd.DataFrame(
        [
            ["2020-01-03T00:00:00Z", "AAA", "1d", 11, 13, 10, 12],
            ["2020-01-02T00:00:00Z", "BBB", "1d", 20, 22, 19, 21],
        ],
        columns=columns,
    )
    result = merge_price_frames(base, recovered)
    assert len(result) == 3
    assert list(zip(result["symbol"], result["timestamp"].astype(str))) == [
        ("AAA", "2020-01-02 00:00:00+00:00"),
        ("AAA", "2020-01-03 00:00:00+00:00"),
        ("BBB", "2020-01-02 00:00:00+00:00"),
    ]
