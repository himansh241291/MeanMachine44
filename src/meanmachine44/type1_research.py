from .candles import Candle


def ma_touch_reclaim(candle: Candle, sma44: float, ma_rising: bool) -> bool:
    return ma_rising and candle.low <= sma44 and candle.close > sma44 and candle.bullish


def local_low_reclaim(
    candle: Candle,
    prior_lows: list[float],
    ma_rising: bool,
    lookback: int = 5,
) -> bool:
    if lookback < 1 or len(prior_lows) < lookback:
        return False
    support = min(prior_lows[-lookback:])
    return ma_rising and candle.low <= support and candle.close > support and candle.bullish
