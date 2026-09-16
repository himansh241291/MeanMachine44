from datetime import datetime, timezone

import pytest

from meanmachine44.candles import Candle
from meanmachine44.market import MarketBar, load_csv


def test_market_bar_preserves_metadata_and_candle():
    bar = MarketBar(
        datetime(2026, 9, 15, tzinfo=timezone.utc),
        "TEST",
        "1d",
        100,
        105,
        99,
        104,
    )
    assert bar.symbol == "TEST"
    assert bar.timeframe == "1d"
    assert bar.candle == Candle(100, 105, 99, 104)


def test_market_bar_requires_symbol_and_timeframe():
    timestamp = datetime(2026, 9, 15, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        MarketBar(timestamp, "", "1d", 100, 105, 99, 104)
    with pytest.raises(ValueError):
        MarketBar(timestamp, "TEST", "", 100, 105, 99, 104)


def test_load_csv(tmp_path):
    path = tmp_path / "bars.csv"
    path.write_text(
        "timestamp,symbol,timeframe,open,high,low,close\n"
        "2026-09-15T00:00:00+00:00,TEST,1d,100,105,99,104\n",
        encoding="utf-8",
    )
    assert load_csv(path) == [
        MarketBar(datetime(2026, 9, 15, tzinfo=timezone.utc), "TEST", "1d", 100, 105, 99, 104)
    ]


def test_load_csv_requires_columns(tmp_path):
    path = tmp_path / "bars.csv"
    path.write_text("timestamp,open,high,low,close\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_csv(path)
