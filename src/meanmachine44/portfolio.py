from __future__ import annotations

from dataclasses import dataclass
from math import floor, isnan


def _present(value) -> bool:
    if value is None:
        return False
    if isinstance(value, float) and isnan(value):
        return False
    return bool(value)


@dataclass(frozen=True)
class CostModel:
    brokerage_bps: float = 0.0
    exchange_bps: float = 0.0
    stt_sell_bps: float = 0.0
    stamp_buy_bps: float = 0.0
    sebi_bps: float = 0.0
    gst_rate: float = 0.0
    spread_bps: float = 0.0
    slippage_bps: float = 0.0

    def _fee_rate(self) -> float:
        return self.brokerage_bps + self.exchange_bps + self.sebi_bps

    def fees(self, turnover: float, is_buy: bool) -> float:
        base = turnover * self._fee_rate() / 10_000
        tax = base * self.gst_rate
        if is_buy:
            stamp = turnover * self.stamp_buy_bps / 10_000
            return base + tax + stamp
        stt = turnover * self.stt_sell_bps / 10_000
        return base + tax + stt

    def fill_price(self, reference: float, is_buy: bool) -> float:
        spread = self.spread_bps / 20_000
        slippage = self.slippage_bps / 10_000
        if is_buy:
            return reference * (1 + spread + slippage)
        return reference * (1 - spread - slippage)

    def execution_costs(self, reference: float, quantity: int) -> tuple[float, float]:
        spread_cost = quantity * reference * self.spread_bps / 20_000
        slippage_cost = quantity * reference * self.slippage_bps / 10_000
        return spread_cost, slippage_cost


@dataclass(frozen=True)
class PortfolioConfig:
    initial_capital: float = 1_000_000.0
    risk_per_trade: float = 0.01
    max_open_positions: int = 10
    max_position_pct: float = 0.20
    unresolved_policy: str = "exclude"

    def __post_init__(self) -> None:
        if self.initial_capital <= 0:
            raise ValueError("initial_capital must be > 0")
        if not 0 < self.risk_per_trade <= 1:
            raise ValueError("risk_per_trade must be in (0, 1]")
        if self.max_open_positions < 1:
            raise ValueError("max_open_positions must be >= 1")
        if not 0 < self.max_position_pct <= 1:
            raise ValueError("max_position_pct must be in (0, 1]")
        if self.unresolved_policy not in {"exclude"}:
            raise ValueError("unresolved_policy must be 'exclude'")


def _risk_budget(cash: float, config: PortfolioConfig) -> float:
    return cash * config.risk_per_trade


def _quantity(cash: float, entry: float, stop: float, config: PortfolioConfig, costs: CostModel) -> int:
    risk_per_share = entry - stop
    buy_price = costs.fill_price(entry, True)
    buy_fee_rate = (costs.brokerage_bps + costs.exchange_bps + costs.sebi_bps) * (1 + costs.gst_rate) / 10_000
    buy_fee_rate += costs.stamp_buy_bps / 10_000
    risk_qty = floor(_risk_budget(cash, config) / risk_per_share)
    cash_qty = floor(cash / (buy_price * (1 + buy_fee_rate)))
    cap_qty = floor((cash * config.max_position_pct) / (buy_price * (1 + buy_fee_rate)))
    return max(0, min(risk_qty, cash_qty, cap_qty))


def _close(position: dict, cash: float, costs: CostModel, closed: list[dict]) -> float:
    exit_price = costs.fill_price(position["exit_reference"], False)
    exit_notional = position["quantity"] * exit_price
    exit_fees = costs.fees(exit_notional, False)
    exit_spread_cost, exit_slippage_cost = costs.execution_costs(
        position["exit_reference"], position["quantity"]
    )
    net_proceeds = exit_notional - exit_fees
    cost_basis = position["quantity"] * position["entry_price"] + position["entry_fees"]
    net_pnl = net_proceeds - cost_basis
    explicit_fees = position["entry_fees"] + exit_fees
    spread_cost = position["entry_spread_cost"] + exit_spread_cost
    slippage_cost = position["entry_slippage_cost"] + exit_slippage_cost
    total_costs = explicit_fees + spread_cost + slippage_cost
    turnover = position["quantity"] * (
        position["entry_reference"] + position["exit_reference"]
    )
    cash += net_proceeds
    closed.append({
        **position["row"],
        "quantity": position["quantity"],
        "entry_fill": position["entry_price"],
        "exit_fill": exit_price,
        "entry_fees": position["entry_fees"],
        "exit_fees": exit_fees,
        "explicit_fees": explicit_fees,
        "entry_spread_cost": position["entry_spread_cost"],
        "exit_spread_cost": exit_spread_cost,
        "spread_cost": spread_cost,
        "entry_slippage_cost": position["entry_slippage_cost"],
        "exit_slippage_cost": exit_slippage_cost,
        "slippage_cost": slippage_cost,
        "total_costs": total_costs,
        "turnover": turnover,
        "effective_cost_bps": total_costs / turnover * 10_000,
        "gross_pnl": position["quantity"] * (
            position["exit_reference"] - position["entry_reference"]
        ),
        "net_pnl": net_pnl,
        "net_r": net_pnl / (position["quantity"] * (position["entry_reference"] - position["stop"])),
        "portfolio_equity": cash,
    })
    return cash


def simulate(rows: list[dict], config: PortfolioConfig, costs: CostModel) -> dict:
    cash = config.initial_capital
    active: list[dict] = []
    closed: list[dict] = []
    skipped_entries = 0
    unresolved = sum(1 for row in rows if not _present(row.get("outcome")))

    entries_by_date: dict[str, list[dict]] = {}
    exit_dates = set()
    for row in rows:
        if not _present(row.get("outcome")):
            continue
        entries_by_date.setdefault(row["trigger_date"], []).append(row)
        if _present(row.get("exit_date")):
            exit_dates.add(row["exit_date"])

    all_dates = sorted(set(entries_by_date) | exit_dates)
    for current_date in all_dates:
        still_open = []
        for position in active:
            if position["exit_date"] == current_date:
                cash = _close(position, cash, costs, closed)
            else:
                still_open.append(position)
        active = still_open

        for row in sorted(entries_by_date.get(current_date, []), key=lambda item: (item["symbol"], item["setup_date"])):
            if len(active) >= config.max_open_positions:
                skipped_entries += 1
                continue
            if any(position["row"]["symbol"] == row["symbol"] for position in active):
                skipped_entries += 1
                continue

            entry_reference = float(row["entry"])
            stop = float(row["stop"])
            exit_date = row.get("exit_date")
            if not _present(exit_date) or entry_reference <= stop:
                skipped_entries += 1
                continue
            quantity = _quantity(cash, entry_reference, stop, config, costs)
            if quantity < 1:
                skipped_entries += 1
                continue

            entry_price = costs.fill_price(entry_reference, True)
            entry_notional = quantity * entry_price
            entry_fees = costs.fees(entry_notional, True)
            entry_spread_cost, entry_slippage_cost = costs.execution_costs(
                entry_reference, quantity
            )
            total_entry = entry_notional + entry_fees
            if total_entry > cash:
                skipped_entries += 1
                continue
            cash -= total_entry
            active.append({
                "row": row,
                "quantity": quantity,
                "entry_reference": entry_reference,
                "entry_price": entry_price,
                "stop": stop,
                "exit_reference": float(row["target"]) if row["outcome"] == "TARGET" else stop,
                "exit_date": exit_date,
                "entry_fees": entry_fees,
                "entry_spread_cost": entry_spread_cost,
                "entry_slippage_cost": entry_slippage_cost,
            })

    final_equity = cash + sum(p["quantity"] * p["entry_price"] for p in active)
    equity_values = [config.initial_capital] + [row["portfolio_equity"] for row in closed]
    peak = equity_values[0]
    max_drawdown = 0.0
    for equity in equity_values:
        peak = max(peak, equity)
        max_drawdown = min(max_drawdown, (equity - peak) / peak)
    wins = [row["net_pnl"] for row in closed if row["net_pnl"] > 0]
    losses = [row["net_pnl"] for row in closed if row["net_pnl"] < 0]
    gross_profit = sum(wins)
    gross_loss = -sum(losses)
    total_costs = sum(row["total_costs"] for row in closed)
    turnover = sum(row["turnover"] for row in closed)
    return {
        "initial_capital": config.initial_capital,
        "final_equity": final_equity,
        "net_pnl": final_equity - config.initial_capital,
        "return_pct": (final_equity / config.initial_capital - 1) * 100,
        "max_drawdown_pct": max_drawdown * 100,
        "closed_trades": len(closed),
        "open_trades": len(active),
        "unresolved_trades": unresolved,
        "skipped_entries": skipped_entries,
        "wins": len(wins),
        "losses": len(losses),
        "win_rate_pct": (len(wins) / len(closed) * 100) if closed else 0.0,
        "profit_factor": (gross_profit / gross_loss) if gross_loss else None,
        "explicit_fees": sum(row["explicit_fees"] for row in closed),
        "spread_cost": sum(row["spread_cost"] for row in closed),
        "slippage_cost": sum(row["slippage_cost"] for row in closed),
        "total_costs": total_costs,
        "turnover": turnover,
        "effective_cost_bps": (total_costs / turnover * 10_000) if turnover else 0.0,
        "trades": closed,
    }
