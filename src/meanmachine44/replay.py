from dataclasses import dataclass

from .market import MarketBar
from .signals import BuySetup


@dataclass(frozen=True)
class TriggerEvent:
    setup_bar: int
    trigger_bar: int
    entry: float
    stop: float


def first_trigger(bars: list[MarketBar], setup_bar: int, setup: BuySetup) -> TriggerEvent | None:
    for i in range(setup_bar + 1, len(bars)):
        if bars[i].high > setup.entry:
            return TriggerEvent(setup_bar, i, setup.entry, setup.stop)
    return None
