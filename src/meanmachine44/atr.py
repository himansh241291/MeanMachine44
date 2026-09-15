def true_range(high: float, low: float, prev_close: float | None) -> float:
    if prev_close is None:
        return high - low
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


def atr_sma(tr: list[float], period: int = 14) -> list[float | None]:
    if period <= 0:
        raise ValueError("period must be positive")
    out = [None] * len(tr)
    for i in range(period - 1, len(tr)):
        out[i] = sum(tr[i - period + 1:i + 1]) / period
    return out
