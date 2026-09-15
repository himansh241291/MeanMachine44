from meanmachine44.ma44 import falling, rising


def test_rising_minimum_3():
    assert rising([1.0, 2.0, 3.0]) == [False, False, True]
    assert rising([1.0, 2.0, 2.0]) == [False, False, False]


def test_rising_ignores_warmup():
    assert rising([None, None, 1.0, 2.0, 3.0]) == [False, False, False, False, True]


def test_falling_ma44():
    assert falling([None, 3.0, 2.0, 2.0, 1.0]) == [False, False, True, False, True]
