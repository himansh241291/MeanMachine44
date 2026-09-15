from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Candle:
    open: float
    high: float
    low: float
    close: float

    def __post_init__(self):
        if not all(isfinite(value) for value in (self.open, self.high, self.low, self.close)):
            raise ValueError("OHLC values must be finite")
        if self.high < max(self.open, self.close) or self.low > min(self.open, self.close):
            raise ValueError("invalid OHLC")

    @property
    def bullish(self) -> bool:
        return self.close > self.open
