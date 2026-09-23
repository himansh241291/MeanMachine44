from datetime import datetime, timezone

import pytest

from meanmachine44.cost_sensitivity import (
    default_cost_scenarios,
    run_cost_sensitivity,
    select_scenarios,
)
from meanmachine44.daily_portfolio import DailyPortfolioConfig
from meanmachine44.market import MarketBar


def row():
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
        "outcome": "TARGET",
        "r": 1.0,
        "variant": "ma_touch_reclaim",
    }


def bars():
    return [
        MarketBar(datetime(2026, 1, 1, tzinfo=timezone.utc), "TEST", "1d", 99, 101, 98, 100),
        MarketBar(datetime(2026, 1, 2, tzinfo=timezone.utc), "TEST", "1d", 99, 102, 97, 101),
        MarketBar(datetime(2026, 1, 3, tzinfo=timezone.utc), "TEST", "1d", 101, 108, 100, 106),
        MarketBar(datetime(2026, 1, 4, tzinfo=timezone.utc), "TEST", "1d", 106, 111, 104, 108),
    ]


def test_default_cost_scenarios_are_ordered():
    assert [item.name for item in default_cost_scenarios()] == [
        "zero",
        "low_friction",
        "moderate_friction",
        "high_friction",
    ]


def test_select_scenarios_rejects_unknown():
    with pytest.raises(ValueError):
        select_scenarios("zero,unknown")


def test_cost_sensitivity_reports_selected_profile():
    result = run_cost_sensitivity(
        [row()],
        bars(),
        DailyPortfolioConfig(
            initial_capital=10_000,
            risk_per_trade=0.01,
            max_position_pct=1.0,
        ),
        select_scenarios("zero,high_friction"),
        variants=("ma_touch_reclaim",),
        targets=(1,),
    )

    assert len(result) == 2
    assert result[0]["cost_scenario"] == "zero"
    assert result[0]["total_costs"] == pytest.approx(0.0)
    assert result[1]["cost_scenario"] == "high_friction"
    assert result[1]["total_costs"] > 0
    assert result[1]["final_equity"] < result[0]["final_equity"]
    assert result[0]["profit_factor"] is None
    assert result[0]["expectancy_r"] > 0
    assert result[0]["cagr_pct"] is not None
