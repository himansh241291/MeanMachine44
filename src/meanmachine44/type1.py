from .candles import Candle


def type1_candidate(candle: Candle, sma44: float, ma_rising: bool) -> bool:
    return ma_rising and candle.low <= sma44 and candle.close > sma44 and candle.bullish
