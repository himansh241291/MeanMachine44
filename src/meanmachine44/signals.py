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


def triggered_later(high: float, setup_bar: int, price_bar: int, price: float) -> bool:
    return price_bar > setup_bar and triggered(high, price)
