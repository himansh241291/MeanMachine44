from meanmachine44.scan import rising_ma44


def test_rising_ma44():
    closes = list(range(1, 48))
    result = rising_ma44(closes)
    assert result[:45] == [False] * 45
    assert result[45:]
