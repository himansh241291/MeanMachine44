import math

import pytest

from meanmachine44.indicators import sma44, sma


def test_sma44_waits_for_44_values():
    values = sma44(list(range(1, 45)))
    assert values[:43] == [None] * 43
    assert values[43] == 22.5


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_sma_rejects_non_finite_values(value):
    with pytest.raises(ValueError):
        sma([1, 2, value], 2)
