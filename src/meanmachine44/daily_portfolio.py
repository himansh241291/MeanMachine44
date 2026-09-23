from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import floor, isnan


def _present(value) -> bool:
    if value is None:
        return False
    if isinstance(value, float) and isnan(value):
        return False
    return bool(value)


@dataclass(frozen=True)
class DailyPortfolioConfig:
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
        if self.unresolved_policy != "exclude":
            raise ValueError("unresolved_policy must be 'exclude'")


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _quantity(cash: float, entry: float, stop: float, config, costs) -> int:
    risk_per_share = entry - stop
    buy_price = costs.fill_price(entry, True)
    buy_fee_rate = (
        costs.brokerage_bps + costs.exchange_bps + costs.sebi_bps
    ) * (1 + costs.gst_rate) / 10_000 + costs.stamp_buy_bps / 10_000
    risk_qty = floor((cash * config.risk_per_trade) / risk_per_share)
    cash_qty = floor(cash / (buy_price * (1 + buy_fee_rate)))
    cap_qty = floor((cash * config.max_position_pct) / (buy_price * (1 + buy_fee_rate)))
    return max(0, min(risk_qty, cash_qty, cap_qty))


def _close(position: dict, cash: float, costs, closed: list[dict]) -> float:
    exit_price = costs.fill_price(position["exit_reference"], False)
    exit_notional = position["quantity"] * exit_price
    exit_fees = costs.fees(exit_notional, False)
    net_proceeds = exit_notional - exit_fees
    cost_basis = position["quantity"] * position["entry_price"] + position["entry_fees"]
    net_pnl = net_proceeds - cost_basis
    cash += net_proceeds
    closed.append({
        **position["row"],
        "quantity": position["quantity"],
        "entry_fill": position["entry_price"],
        "exit_fill": exit_price,
        "entry_fees": position["entry_fees"],
        "exit_fees": exit_fees,
        "total_costs": position["entry_fees"] + exit_fees,
        "gross_pnl": position["quantity"] * (position["exit_reference"] - position["entry_price"]),
        "net_pnl": net_pnl,
        "net_r": net_pnl / (position["quantity"] * (position["entry_reference"] - position["stop"])),
    })
    return cash


def simulate_daily(rows: list[dict], bars: list[object], config, costs) -> dict:
    bars_by_time: dict[datetime, dict[str, float]] = {}
    dates: set[datetime] = set()
    for bar in bars:
        timestamp = bar.timestamp if hasattr(bar, "timestamp") else _parse_time(bar["timestamp"])
        symbol = bar.symbol if hasattr(bar, "symbol") else bar["symbol"]
        close = bar.close if hasattr(bar, "close") else float(bar["close"])
        dates.add(timestamp)
        bars_by_time.setdefault(timestamp, {})[symbol] = close

    valid_rows = [row for row in rows if _present(row.get("outcome")) and _present(row.get("exit_date"))]
    unresolved = sum(1 for row in rows if not _present(row.get("outcome")))
    entries: dict[datetime, list[dict]] = {}
    for row in valid_rows:
        entries.setdefault(_parse_time(row["trigger_date"]), []).append(row)
        dates.add(_parse_time(row["trigger_date"]))
        dates.add(_parse_time(row["exit_date"]))

    cash = config.initial_capital
    active: list[dict] = []
    closed: list[dict] = []
    skipped_entries = 0
    peak_open = 0
    peak_utilization = 0.0
    last_close: dict[str, float] = {}
    curve: list[dict] = []
    max_drawdown = 0.0
    peak_equity = config.initial_capital

    for current_time in sorted(dates):
        last_close.update(bars_by_time.get(current_time, {}))

        remaining = []
        for position in active:
            if position["exit_date"] == current_time:
                cash = _close(position, cash, costs, closed)
            else:
                remaining.append(position)
        active = remaining

        equity_before_entries = cash + sum(
            position["quantity"] * last_close.get(
                position["row"]["symbol"], position["entry_price"]
            )
            for position in active
        )

        for row in sorted(entries.get(current_time, []), key=lambda item: (item["symbol"], item["setup_date"])):
            if len(active) >= config.max_open_positions:
                skipped_entries += 1
                continue
            if any(position["row"]["symbol"] == row["symbol"] for position in active):
                skipped_entries += 1
                continue

            entry = float(row.get("entry_fill", row["entry"]))
            stop = float(row["stop"])
            if entry <= stop or not _present(row.get("exit_date")):
                skipped_entries += 1
                continue
            quantity = _quantity(cash, entry, stop, config, costs)
            if quantity < 1:
                skipped_entries += 1
                continue

            entry_price = costs.fill_price(entry, True)
            entry_notional = quantity * entry_price
            entry_fees = costs.fees(entry_notional, True)
            total_entry = entry_notional + entry_fees
            if total_entry > cash:
                skipped_entries += 1
                continue
            cash -= total_entry
            position = {
                "row": row,
                "quantity": quantity,
                "entry_reference": entry,
                "entry_price": entry_price,
                "stop": stop,
                "exit_reference": float(row["exit_fill"]) if _present(row.get("exit_fill")) else (float(row["target"]) if row["outcome"] == "TARGET" else stop),
                "exit_date": _parse_time(row["exit_date"]),
                "entry_fees": entry_fees,
            }
            if position["exit_date"] == current_time:
                cash = _close(position, cash, costs, closed)
            else:
                active.append(position)

        market_value = sum(
            position["quantity"] * last_close.get(
                position["row"]["symbol"], position["entry_price"]
            )
            for position in active
        )
        equity = cash + market_value
        invested = sum(position["quantity"] * position["entry_price"] for position in active)
        utilization = (invested / equity * 100) if equity else 0.0
        peak_open = max(peak_open, len(active))
        peak_utilization = max(peak_utilization, utilization)
        peak_equity = max(peak_equity, equity)
        max_drawdown = min(max_drawdown, (equity - peak_equity) / peak_equity)
        curve.append({
            "timestamp": current_time.isoformat(),
            "cash": cash,
            "market_value": market_value,
            "equity": equity,
            "open_positions": len(active),
            "capital_utilization_pct": utilization,
        })

    final_equity = curve[-1]["equity"] if curve else config.initial_capital
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
        "peak_open_positions": peak_open,
        "peak_capital_utilization_pct": peak_utilization,
        "total_costs": sum(row["total_costs"] for row in closed),
        "equity_curve": curve,
        "trades": closed,
    }
