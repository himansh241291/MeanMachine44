from .candles import Candle
from .signals import BuySetup


def bullish_setup(candle: Candle, ma44: float) -> BuySetup | None:
    if candle.bullish and candle.low <= ma44 <= candle.high:
        return BuySetup(entry=candle.high, stop=candle.low)
    return None
