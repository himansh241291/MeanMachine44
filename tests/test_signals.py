import pytest

from meanmachine44.signals import BuySetup, buy_setup, triggered


def test_buy_setup():
    assert buy_setup(103, 98) == BuySetup(entry=103, stop=98)


def test_trigger():
    assert triggered(103, 103)
    assert triggered(103, 104)
    assert not triggered(103, 102.99)


def test_invalid_candle():
    with pytest.raises(ValueError):
        buy_setup(98, 103)
