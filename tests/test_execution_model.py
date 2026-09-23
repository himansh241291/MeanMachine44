from datetime import datetime, timezone

import pytest

from meanmachine44.daily_portfolio import DailyPortfolioConfig, simulate_daily
from meanmachine44.execution_model import apply_gap_aware_execution
from meanmachine44.market import MarketBar
from meanmachine44.portfolio import CostModel


def row(outcome="TARGET"):
    return {
        "symbol": "TEST",
        "setup_date": "2026-01-01T00:00:00+00:00",
        "trigger_date": "2026-01-02T00:00:00+00:00",
        "exit_date": "2026-01-04T00:00:00+00:00",
        "entry": 100.0,
        "stop": 90.0,
        "risk": 10.0,
        "target_multiple": 1,
        "target": 110.0,
        "outcome": outcome,
        "r": 1.0 if outcome == "TARGET" else -1.0,
        "variant": "ma_touch_reclaim",
    }


def test_gap_entry_uses_trigger_open():
    result = apply_gap_aware_execution([row()], [
        MarketBar(datetime(2026, 1, 2, tzinfo=timezone.utc), "TEST", "1d", 105, 108, 101, 107),
        MarketBar(datetime(2026, 1, 4, tzinfo=timezone.utc), "TEST", "1d", 106, 111, 104, 108),
    ])[0]
    assert result["entry_fill"] == 105.0
    assert result["execution_status"] == "REFERENCE_FILL"


def test_ambiguous_trigger_is_excluded():
    result = apply_gap_aware_execution([row()], [
        MarketBar(datetime(2026, 1, 2, tzinfo=timezone.utc), "TEST", "1d", 105, 112, 89, 110),
    ])[0]
    assert result["execution_status"] == "AMBIGUOUS_TRIGGER"
    assert result["outcome"] is None


def test_daily_portfolio_honors_gap_aware_fills():
    item = row()
    item["entry_fill"] = 105.0
    item["exit_fill"] = 110.0
    result = simulate_daily([item], [
        MarketBar(datetime(2026, 1, 1, tzinfo=timezone.utc), "TEST", "1d", 99, 101, 98, 100),
        MarketBar(datetime(2026, 1, 2, tzinfo=timezone.utc), "TEST", "1d", 105, 108, 101, 107),
        MarketBar(datetime(2026, 1, 4, tzinfo=timezone.utc), "TEST", "1d", 106, 111, 104, 108),
    ], DailyPortfolioConfig(initial_capital=10_000, risk_per_trade=0.01, max_position_pct=1.0), CostModel())
    assert result["closed_trades"] == 1
    assert result["trades"][0]["quantity"] == 6
    assert result["trades"][0]["entry_fill"] == 105.0
    assert result["trades"][0]["exit_fill"] == 110.0
    assert result["final_equity"] == pytest.approx(10030.0)
