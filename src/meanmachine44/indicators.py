from collections.abc import Sequence


def sma(values: Sequence[float], period: int = 44) -> list[float | None]:
    if period <= 0:
        raise ValueError("period must be positive")
    out = [None] * len(values)
    for i in range(period - 1, len(values)):
        out[i] = sum(values[i - period + 1:i + 1]) / period
    return out


def sma44(closes: Sequence[float]) -> list[float | None]:
    return sma(closes, 44)
