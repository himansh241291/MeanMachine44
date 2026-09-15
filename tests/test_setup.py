from meanmachine44.candles import Candle
from meanmachine44.setup import ma44_support


def test_ma44_support():
    assert ma44_support(Candle(101, 105, 99, 104), 100)
    assert not ma44_support(Candle(102, 105, 101, 104), 100)
