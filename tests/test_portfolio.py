import pytest

from meanmachine44.portfolio import CostModel, PortfolioConfig, simulate


def row(outcome="TARGET"):
    return {
        "symbol": "TEST",
        "setup_date": "2026-01-01T00:00:00+00:00",
        "trigger_date": "2026-01-02T00:00:00+00:00",
        "exit_date": "2026-01-03T00:00:00+00:00",
        "entry": 100.0,
        "stop": 90.0,
        "risk": 10.0,
        "target_multiple": 2,
        "target": 120.0,
        "outcome": outcome,
        "r": 2.0 if outcome == "TARGET" else -1.0,
        "variant": "ma_touch_reclaim",
    }


def test_portfolio_sizes_from_risk_and_realizes_target():
    result = simulate(
        [row()],
        PortfolioConfig(initial_capital=10_000, risk_per_trade=0.01, max_position_pct=1.0),
        CostModel(),
    )
    assert result["closed_trades"] == 1
    assert result["final_equity"] == pytest.approx(10_200.0)
    assert result["net_pnl"] == pytest.approx(200.0)
    assert result["trades"][0]["quantity"] == 10
    assert result["trades"][0]["net_r"] == pytest.approx(2.0)


def test_portfolio_realizes_stop_loss():
    result = simulate(
        [row("STOP")],
        PortfolioConfig(initial_capital=10_000, risk_per_trade=0.01, max_position_pct=1.0),
        CostModel(),
    )
    assert result["final_equity"] == pytest.approx(9_900.0)
    assert result["trades"][0]["net_pnl"] == pytest.approx(-100.0)


def test_costs_reduce_pnl():
    result = simulate(
        [row()],
        PortfolioConfig(initial_capital=10_000, risk_per_trade=0.01, max_position_pct=1.0),
        CostModel(brokerage_bps=10, stt_sell_bps=5, spread_bps=5, slippage_bps=5),
    )
    assert result["final_equity"] < 10_200.0
    trade = result["trades"][0]
    assert trade["explicit_fees"] > 0
    assert trade["spread_cost"] > 0
    assert trade["slippage_cost"] > 0
    assert trade["total_costs"] == pytest.approx(
        trade["explicit_fees"] + trade["spread_cost"] + trade["slippage_cost"]
    )
    assert trade["net_pnl"] == pytest.approx(trade["gross_pnl"] - trade["total_costs"])
    assert result["effective_cost_bps"] > 0


def test_unresolved_trades_are_excluded():
    result = simulate(
        [row(None)],
        PortfolioConfig(initial_capital=10_000, risk_per_trade=0.01, max_position_pct=1.0),
        CostModel(),
    )
    assert result["unresolved_trades"] == 1
    assert result["closed_trades"] == 0
    assert result["final_equity"] == 10_000.0


def test_invalid_portfolio_config():
    with pytest.raises(ValueError):
        PortfolioConfig(risk_per_trade=0)
