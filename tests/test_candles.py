import math

import pytest

from meanmachine44.candles import Candle


def test_bullish_candle():
    assert Candle(100, 105, 99, 104).bullish


def test_invalid_ohlc():
    with pytest.raises(ValueError):
        Candle(100, 98, 99, 97)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_non_finite_ohlc_is_invalid(value):
    with pytest.raises(ValueError):
        Candle(100, 105, 99, value)
