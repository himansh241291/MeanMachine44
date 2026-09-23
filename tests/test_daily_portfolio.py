from datetime import datetime, timezone

import pytest

from meanmachine44.daily_portfolio import DailyPortfolioConfig, simulate_daily
from meanmachine44.market import MarketBar
from meanmachine44.portfolio import CostModel


def base_row(outcome="TARGET"):
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


def bars():
    return [
        MarketBar(datetime(2026, 1, 1, tzinfo=timezone.utc), "TEST", "1d", 99, 101, 98, 100),
        MarketBar(datetime(2026, 1, 2, tzinfo=timezone.utc), "TEST", "1d", 99, 102, 97, 101),
        MarketBar(datetime(2026, 1, 3, tzinfo=timezone.utc), "TEST", "1d", 101, 108, 100, 106),
        MarketBar(datetime(2026, 1, 4, tzinfo=timezone.utc), "TEST", "1d", 106, 111, 104, 108),
    ]


def test_daily_marks_open_position():
    result = simulate_daily(
        [base_row()],
        bars(),
        DailyPortfolioConfig(initial_capital=10_000, risk_per_trade=0.01, max_position_pct=1.0),
        CostModel(),
    )
    assert result["closed_trades"] == 1
    assert result["final_equity"] == pytest.approx(10_100.0)
    assert len(result["equity_curve"]) == 4
    assert result["peak_open_positions"] == 1


def test_daily_stop_loss():
    row = base_row("STOP")
    row["target"] = 120.0
    result = simulate_daily(
        [row],
        bars(),
        DailyPortfolioConfig(initial_capital=10_000, risk_per_trade=0.01, max_position_pct=1.0),
        CostModel(),
    )
    assert result["final_equity"] == pytest.approx(9_900.0)


def test_daily_unresolved_is_excluded():
    result = simulate_daily(
        [base_row(None)],
        bars(),
        DailyPortfolioConfig(initial_capital=10_000, risk_per_trade=0.01, max_position_pct=1.0),
        CostModel(),
    )
    assert result["unresolved_trades"] == 1
    assert result["final_equity"] == pytest.approx(10_000.0)

def test_daily_closes_same_day_gap_execution():
    row = base_row()
    row["entry_fill"] = 105.0
    row["exit_fill"] = 110.0
    row["trigger_date"] = "2026-01-02T00:00:00+00:00"
    row["exit_date"] = row["trigger_date"]
    result = simulate_daily(
        [row],
        bars(),
        DailyPortfolioConfig(initial_capital=10_000, risk_per_trade=0.01, max_position_pct=1.0),
        CostModel(),
    )
    assert result["closed_trades"] == 1
    assert result["open_trades"] == 0
