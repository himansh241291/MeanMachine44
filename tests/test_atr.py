from meanmachine44.atr import atr_sma, true_range


def test_true_range():
    assert true_range(110, 100, 105) == 10
    assert true_range(110, 100, 120) == 20


def test_atr_sma():
    assert atr_sma([1, 2, 3], 2) == [None, 1.5, 2.5]
