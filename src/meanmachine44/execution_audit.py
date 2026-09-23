from __future__ import annotations

from collections import defaultdict
from datetime import datetime


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _stats(values: list[float]) -> tuple[float | None, float | None]:
    if not values:
        return None, None
    values = sorted(values)
    middle = len(values) // 2
    median = values[middle] if len(values) % 2 else (values[middle - 1] + values[middle]) / 2
    p95 = values[min(len(values) - 1, int(0.95 * len(values)))]
    return median, p95


def audit_execution(rows: list[dict], bars: list[object]) -> list[dict]:
    lookup = {}
    for bar in bars:
        timestamp = bar.timestamp if hasattr(bar, "timestamp") else _parse_time(bar["timestamp"])
        symbol = bar.symbol if hasattr(bar, "symbol") else bar["symbol"]
        lookup[(symbol, timestamp)] = bar

    groups = defaultdict(lambda: {
        "trades": 0,
        "missing_trigger_bar": 0,
        "missing_exit_bar": 0,
        "entry_gaps": [],
        "exit_gaps": [],
    })

    for row in rows:
        key = (row.get("variant"), int(row.get("target_multiple")))
        group = groups[key]
        group["trades"] += 1

        trigger = lookup.get((row["symbol"], _parse_time(row["trigger_date"])))
        exit_bar = lookup.get((row["symbol"], _parse_time(row["exit_date"]))) if row.get("exit_date") else None

        if trigger is None:
            group["missing_trigger_bar"] += 1
        else:
            entry = float(row["entry"])
            open_price = float(trigger.open if hasattr(trigger, "open") else trigger["open"])
            if open_price > entry:
                group["entry_gaps"].append((open_price - entry) / entry * 10_000)

        if exit_bar is None:
            group["missing_exit_bar"] += 1
        else:
            open_price = float(exit_bar.open if hasattr(exit_bar, "open") else exit_bar["open"])
            outcome = row.get("outcome")
            reference = float(row["stop"] if outcome == "STOP" else row["target"])
            through = open_price < reference if outcome == "STOP" else open_price > reference
            if outcome in {"STOP", "TARGET"} and through:
                group["exit_gaps"].append(abs(open_price - reference) / reference * 10_000)

    results = []
    for (variant, target), group in sorted(groups.items()):
        entry_median, entry_p95 = _stats(group["entry_gaps"])
        exit_median, exit_p95 = _stats(group["exit_gaps"])
        results.append({
            "variant": variant,
            "target_multiple": target,
            "trades": group["trades"],
            "missing_trigger_bar": group["missing_trigger_bar"],
            "missing_exit_bar": group["missing_exit_bar"],
            "entry_gap_count": len(group["entry_gaps"]),
            "entry_gap_pct": len(group["entry_gaps"]) / group["trades"] * 100,
            "entry_gap_median_bps": entry_median,
            "entry_gap_p95_bps": entry_p95,
            "exit_gap_count": len(group["exit_gaps"]),
            "exit_gap_pct": len(group["exit_gaps"]) / group["trades"] * 100,
            "exit_gap_median_bps": exit_median,
            "exit_gap_p95_bps": exit_p95,
        })

    return results
