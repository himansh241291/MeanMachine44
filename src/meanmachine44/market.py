from dataclasses import dataclass
from datetime import datetime

from .candles import Candle


@dataclass(frozen=True)
class MarketBar:
    timestamp: datetime
    symbol: str
    timeframe: str
    open: float
    high: float
    low: float
    close: float

    def __post_init__(self) -> None:
        if not self.symbol or not self.timeframe:
            raise ValueError("symbol and timeframe are required")
        Candle(self.open, self.high, self.low, self.close)

    @property
    def candle(self) -> Candle:
        return Candle(self.open, self.high, self.low, self.close)
