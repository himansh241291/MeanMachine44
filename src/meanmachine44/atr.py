from math import isfinite

from .candles import Candle


def true_range(high: float, low: float, prev_close: float | None) -> float:
    values = (high, low) if prev_close is None else (high, low, prev_close)
    if not all(isfinite(value) for value in values):
        raise ValueError("true range inputs must be finite")
    if high < low:
        raise ValueError("high must be greater than or equal to low")
    if prev_close is None:
        return high - low
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


def atr_sma(tr: list[float], period: int = 14) -> list[float | None]:
    if period <= 0:
        raise ValueError("period must be positive")
    if any(not isfinite(value) or value < 0 for value in tr):
        raise ValueError("true range must be finite and non-negative")
    out = [None] * len(tr)
    for i in range(period - 1, len(tr)):
        out[i] = sum(tr[i - period + 1:i + 1]) / period
    return out


def atr14_sma(candles: list[Candle]) -> list[float | None]:
    return atr_sma([
        true_range(candle.high, candle.low, candles[i - 1].close if i else None)
        for i, candle in enumerate(candles)
    ])


def lower_atr_boundary(reference: float, atr: float) -> float:
    if atr < 0:
        raise ValueError("atr must not be negative")
    return reference - atr


def lower_atr_exhausted(reference: float, low: float, atr: float) -> bool:
    return low <= lower_atr_boundary(reference, atr)
