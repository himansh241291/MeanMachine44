import math

import pytest

from meanmachine44.atr import (
    atr14_sma,
    atr_sma,
    lower_atr_boundary,
    lower_atr_exhausted,
    true_range,
)
from meanmachine44.candles import Candle


def test_true_range():
    assert true_range(110, 100, 105) == 10
    assert true_range(110, 100, 120) == 20


def test_true_range_rejects_inverted_range():
    with pytest.raises(ValueError):
        true_range(99, 100, 105)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_true_range_rejects_non_finite(value):
    with pytest.raises(ValueError):
        true_range(value, 100, 105)


def test_atr_sma():
    assert atr_sma([1, 2, 3], 2) == [None, 1.5, 2.5]


def test_atr_sma_rejects_negative_true_range():
    with pytest.raises(ValueError):
        atr_sma([1, -1, 3], 2)


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_atr_sma_rejects_non_finite_true_range(value):
    with pytest.raises(ValueError):
        atr_sma([1, value, 3], 2)


def test_atr14_sma_uses_ohlc():
    candles = [Candle(100, 110, 100, 105)] * 14
    assert atr14_sma(candles) == [None] * 13 + [10]


def test_lower_atr_exhaustion():
    assert lower_atr_boundary(438, 10) == 428
    assert lower_atr_exhausted(438, 427.35, 10)
    assert not lower_atr_exhausted(438, 428.01, 10)


def test_negative_atr_is_invalid():
    with pytest.raises(ValueError):
        lower_atr_boundary(438, -1)
