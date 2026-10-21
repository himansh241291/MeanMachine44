from pathlib import Path

import pandas as pd

from scripts.download_historical_membership_prices import (
    extract_symbol_bars,
    load_membership_symbols,
)


def test_load_membership_symbols_deduplicates_and_trims(tmp_path: Path):
    path = tmp_path / "membership.csv"
    pd.DataFrame({"symbol": [" AAA ", "BBB", "AAA", None]}).to_csv(path, index=False)
    assert load_membership_symbols(path) == ["AAA", "BBB"]


def test_extract_symbol_bars_normalizes_schema():
    source = pd.DataFrame(
        {
            "Open": [10.0, 11.0],
            "High": [12.0, 13.0],
            "Low": [9.0, 10.0],
            "Close": [11.0, 12.0],
        },
        index=pd.to_datetime(["2020-01-02", "2020-01-03"]),
    )
    result = extract_symbol_bars(source, "AAA.NS", "AAA")
    assert list(result.columns) == [
        "timestamp", "symbol", "timeframe", "open", "high", "low", "close"
    ]
    assert result["symbol"].tolist() == ["AAA", "AAA"]
    assert result["timeframe"].eq("1d").all()
    assert result["timestamp"].dt.tz is not None
    assert result["close"].tolist() == [11.0, 12.0]


def test_extract_symbol_bars_handles_missing_ticker():
    cols = pd.MultiIndex.from_product([["OTHER.NS"], ["Open", "High", "Low", "Close"]])
    source = pd.DataFrame([[1, 2, 0.5, 1.5]], columns=cols)
    result = extract_symbol_bars(source, "AAA.NS", "AAA")
    assert result.empty
