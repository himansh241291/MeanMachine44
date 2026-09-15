from .candles import Candle


def ma44_support(candle: Candle, ma44: float) -> bool:
    return candle.low <= ma44 <= candle.high
