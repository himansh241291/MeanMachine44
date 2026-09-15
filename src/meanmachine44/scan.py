from .indicators import sma44
from .ma44 import rising


def rising_ma44(closes: list[float]) -> list[bool]:
    return rising(sma44(closes), 3)
