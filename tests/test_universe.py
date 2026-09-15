import pytest
from meanmachine44.universe import weekly_to_daily


def test_weekly_to_daily():
    assert weekly_to_daily([True, False, True], [True, True, False]) == [True, False, False]


def test_weekly_to_daily_length():
    with pytest.raises(ValueError):
        weekly_to_daily([True], [True, False])
