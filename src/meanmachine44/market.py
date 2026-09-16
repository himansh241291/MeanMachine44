import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

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


def load_csv(path: str | Path) -> list[MarketBar]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        rows = csv.DictReader(handle)
        required = {"timestamp", "symbol", "timeframe", "open", "high", "low", "close"}
        if not rows.fieldnames or not required.issubset(rows.fieldnames):
            raise ValueError("CSV must contain timestamp,symbol,timeframe,open,high,low,close")
        return [
            MarketBar(
                datetime.fromisoformat(row["timestamp"]),
                row["symbol"],
                row["timeframe"],
                float(row["open"]),
                float(row["high"]),
                float(row["low"]),
                float(row["close"]),
            )
            for row in rows
        ]
