import pytest

from meanmachine44.signals import BuySetup, buy_setup, triggered, triggered_later


def test_buy_setup():
    assert buy_setup(103, 98) == BuySetup(entry=103, stop=98)


def test_trigger():
    assert not triggered(103, 103)
    assert triggered(103, 103.01)
    assert not triggered(103, 102.99)


def test_trigger_requires_later_bar():
    assert not triggered_later(103, 10, 10, 104)
    assert triggered_later(103, 10, 11, 103.01)


def test_invalid_candle():
    with pytest.raises(ValueError):
        buy_setup(98, 103)
