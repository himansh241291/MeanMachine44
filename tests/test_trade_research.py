import pytest

from meanmachine44.trade_research import first_touch, levels


def test_levels():
    assert levels(100, 90) == {"1R": 110, "2R": 120, "3R": 130}


def test_levels_rejects_invalid_risk():
    with pytest.raises(ValueError):
        levels(100, 100)


def test_first_touch_stop_before_target():
    assert first_touch([101, 103], [99, 89], {"1R": 110}, 90) == "STOP"


def test_first_touch_target():
    assert first_touch([111], [100], {"1R": 110}, 90) == "1R"
