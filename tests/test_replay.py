from datetime import datetime, timezone

import pytest

from meanmachine44.market import MarketBar
from meanmachine44.replay import TriggerEvent, first_trigger
from meanmachine44.signals import buy_setup


def bar(high: float) -> MarketBar:
    return MarketBar(
        datetime(2026, 9, 15, tzinfo=timezone.utc),
        "TEST",
        "1d",
        100,
        high,
        99,
        100,
    )


def test_first_trigger_requires_later_bar():
    setup = buy_setup(103, 98)
    bars = [bar(104), bar(102), bar(105)]
    assert first_trigger(bars, 0, setup) == TriggerEvent(0, 2, 103, 98)


def test_first_trigger_returns_none_when_never_crossed():
    setup = buy_setup(103, 98)
    assert first_trigger([bar(103), bar(102)], 0, setup) is None


@pytest.mark.parametrize("setup_bar", [-1, 2])
def test_first_trigger_rejects_invalid_setup_bar(setup_bar):
    setup = buy_setup(103, 98)
    with pytest.raises(IndexError):
        first_trigger([bar(104), bar(102)], setup_bar, setup)
