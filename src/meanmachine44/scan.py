from .indicators import sma44
from .ma44 import rising


def rising_ma44(closes: list[float]) -> list[bool]:
    return rising(sma44(closes), 3)


def passes_ma44_scan(weekly_closes: list[float], daily_closes: list[float]) -> bool:
    weekly = rising_ma44(weekly_closes)
    daily = rising_ma44(daily_closes)
    return bool(weekly and weekly[-1] and daily and daily[-1])
