from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .daily_portfolio import DailyPortfolioConfig, simulate_daily
from .portfolio import CostModel


@dataclass(frozen=True)
class CostScenario:
    name: str
    costs: CostModel


def default_cost_scenarios() -> tuple[CostScenario, ...]:
    return (
        CostScenario("zero", CostModel()),
        CostScenario(
            "low_friction",
            CostModel(
                brokerage_bps=2.0,
                exchange_bps=1.0,
                stt_sell_bps=5.0,
                stamp_buy_bps=1.0,
                sebi_bps=0.1,
                gst_rate=0.18,
                spread_bps=5.0,
                slippage_bps=5.0,
            ),
        ),
        CostScenario(
            "moderate_friction",
            CostModel(
                brokerage_bps=5.0,
                exchange_bps=2.0,
                stt_sell_bps=10.0,
                stamp_buy_bps=2.0,
                sebi_bps=0.1,
                gst_rate=0.18,
                spread_bps=10.0,
                slippage_bps=10.0,
            ),
        ),
        CostScenario(
            "high_friction",
            CostModel(
                brokerage_bps=10.0,
                exchange_bps=5.0,
                stt_sell_bps=20.0,
                stamp_buy_bps=5.0,
                sebi_bps=0.2,
                gst_rate=0.18,
                spread_bps=20.0,
                slippage_bps=20.0,
            ),
        ),
    )


def select_scenarios(names: str) -> tuple[CostScenario, ...]:
    available = {scenario.name: scenario for scenario in default_cost_scenarios()}
    selected = []
    for name in (item.strip() for item in names.split(",")):
        if not name:
            continue
        if name not in available:
            raise ValueError(f"unknown cost scenario: {name}")
        selected.append(available[name])
    if not selected:
        raise ValueError("at least one cost scenario is required")
    return tuple(selected)


def _cagr_pct(initial: float, final: float, curve: list[dict]) -> float | None:
    if initial <= 0 or final <= 0 or len(curve) < 2:
        return None
    start = datetime.fromisoformat(curve[0]["timestamp"])
    end = datetime.fromisoformat(curve[-1]["timestamp"])
    days = (end - start).total_seconds() / 86_400
    if days <= 0:
        return None
    return ((final / initial) ** (365.25 / days) - 1) * 100


def _trade_metrics(trades: list[dict]) -> tuple[float | None, float | None]:
    profits = [row["net_pnl"] for row in trades if row["net_pnl"] > 0]
    losses = [row["net_pnl"] for row in trades if row["net_pnl"] < 0]
    rs = [row["net_r"] for row in trades if row.get("net_r") is not None]
    profit_factor = sum(profits) / -sum(losses) if losses else None
    expectancy_r = sum(rs) / len(rs) if rs else None
    return profit_factor, expectancy_r


def run_cost_sensitivity(
    rows: list[dict],
    bars: list[object],
    config: DailyPortfolioConfig,
    scenarios: tuple[CostScenario, ...] | None = None,
    variants: tuple[str, ...] = ("ma_touch_reclaim", "local_low_reclaim"),
    targets: tuple[int, ...] = (1, 2, 3),
) -> list[dict]:
    scenarios = scenarios or default_cost_scenarios()
    results = []

    for scenario in scenarios:
        for variant in variants:
            for target in targets:
                selected = [
                    row
                    for row in rows
                    if row.get("variant") == variant and row.get("target_multiple") == target
                ]
                if not selected:
                    continue

                result = simulate_daily(selected, bars, config, scenario.costs)
                profit_factor, expectancy_r = _trade_metrics(result["trades"])
                results.append({
                    "cost_scenario": scenario.name,
                    "variant": variant,
                    "target_multiple": target,
                    "initial_capital": result["initial_capital"],
                    "final_equity": result["final_equity"],
                    "net_pnl": result["net_pnl"],
                    "return_pct": result["return_pct"],
                    "cagr_pct": _cagr_pct(
                        result["initial_capital"],
                        result["final_equity"],
                        result["equity_curve"],
                    ),
                    "max_drawdown_pct": result["max_drawdown_pct"],
                    "profit_factor": profit_factor,
                    "expectancy_r": expectancy_r,
                    "closed_trades": result["closed_trades"],
                    "unresolved_trades": result["unresolved_trades"],
                    "skipped_entries": result["skipped_entries"],
                    "peak_open_positions": result["peak_open_positions"],
                    "peak_capital_utilization_pct": result["peak_capital_utilization_pct"],
                    "total_costs": result["total_costs"],
                    "brokerage_bps": scenario.costs.brokerage_bps,
                    "exchange_bps": scenario.costs.exchange_bps,
                    "stt_sell_bps": scenario.costs.stt_sell_bps,
                    "stamp_buy_bps": scenario.costs.stamp_buy_bps,
                    "sebi_bps": scenario.costs.sebi_bps,
                    "gst_rate": scenario.costs.gst_rate,
                    "spread_bps": scenario.costs.spread_bps,
                    "slippage_bps": scenario.costs.slippage_bps,
                })

    return results
