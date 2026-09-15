import pytest

from meanmachine44.candles import Candle


def test_bullish_candle():
    assert Candle(100, 105, 99, 104).bullish


def test_invalid_ohlc():
    with pytest.raises(ValueError):
        Candle(100, 98, 99, 97)
