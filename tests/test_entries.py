from meanmachine44.candles import Candle
from meanmachine44.entries import bullish_setup
from meanmachine44.signals import BuySetup


def test_bullish_ma44_setup():
    assert bullish_setup(Candle(100, 105, 99, 104), 101) == BuySetup(105, 99)


def test_bullish_ma44_setup_requires_bullish_candle():
    assert bullish_setup(Candle(104, 105, 99, 100), 101) is None
