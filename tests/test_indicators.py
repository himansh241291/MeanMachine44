from meanmachine44.indicators import sma44


def test_sma44_waits_for_44_values():
    values = sma44(list(range(1, 45)))
    assert values[:43] == [None] * 43
    assert values[43] == 22.5
