from dataclasses import dataclass


@dataclass(frozen=True)
class BuySetup:
    entry: float
    stop: float


def buy_setup(high: float, low: float) -> BuySetup:
    if high <= low:
        raise ValueError("high must be greater than low")
    return BuySetup(entry=high, stop=low)


def triggered(high: float, price: float) -> bool:
    return price > high
