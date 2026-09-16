from meanmachine44.candles import Candle
from meanmachine44.type1 import type1_candidate


def test_type1_candidate_requires_rising_ma_and_reclaim():
    assert type1_candidate(Candle(100, 106, 98, 104), 102, True)


def test_type1_candidate_rejects_non_bullish_or_non_rising():
    assert not type1_candidate(Candle(104, 106, 100, 102), 103, True)
    assert not type1_candidate(Candle(100, 106, 98, 104), 102, False)
    assert not type1_candidate(Candle(100, 101, 103, 104), 102, True)
