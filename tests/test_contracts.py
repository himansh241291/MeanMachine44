import pytest

from meanmachine44.atr import atr_sma
from meanmachine44.indicators import sma
from meanmachine44.ma44 import rising
from meanmachine44.signals import triggered_later


def test_sma_rejects_non_positive_period():
    with pytest.raises(ValueError):
        sma([1, 2, 3], 0)


def test_rising_requires_two_periods():
    with pytest.raises(ValueError):
        rising([1, 2, 3], 1)


def test_rising_needs_complete_window():
    assert rising([None, 1, 2], 3) == [False, False, False]


def test_atr_rejects_non_positive_period():
    with pytest.raises(ValueError):
        atr_sma([1, 2], 0)


def test_triggered_later_requires_price_above_high():
    assert not triggered_later(103, 10, 11, 103)
    assert triggered_later(103, 10, 11, 103.01)
