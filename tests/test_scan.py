from meanmachine44.scan import passes_ma44_scan, rising_ma44


def test_rising_ma44():
    closes = list(range(1, 48))
    result = rising_ma44(closes)
    assert result[:45] == [False] * 45
    assert result[45:]


def test_passes_ma44_scan_requires_weekly_and_daily_rising():
    rising = list(range(1, 48))
    flat = [100.0] * 47
    assert passes_ma44_scan(rising, rising)
    assert not passes_ma44_scan(flat, rising)
    assert not passes_ma44_scan(rising, flat)
