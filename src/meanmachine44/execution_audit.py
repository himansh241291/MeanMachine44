from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from math import isnan


def _present(value) -> bool:
    return value is not None and not (isinstance(value, float) and isnan(value)) and bool(value)


def _parse_time(value) -> datetime:
    if not _present(value):
        raise ValueError("timestamp is required")
    return datetime.fromisoformat(str(value))


def _field(bar, name: str):
    return getattr(bar, name) if hasattr(bar, name) else bar[name]


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
        "unresolved_trades": 0,
        "missing_trigger_bar": 0,
        "missing_exit_bar": 0,
        "entry_gaps": [],
        "exit_gaps": [],
        "trigger_gap_stops": 0,
        "trigger_gap_targets": 0,
        "trigger_gap_both": 0,
        "entry_gap_cross_target": 0,
    })

    for row in rows:
        key = (row.get("variant"), int(row.get("target_multiple")))
        group = groups[key]
        group["trades"] += 1

        trigger = None
        if _present(row.get("trigger_date")):
            trigger = lookup.get((row["symbol"], _parse_time(row["trigger_date"])))

        outcome = row.get("outcome")
        if trigger is None:
            group["missing_trigger_bar"] += 1
        else:
            entry = float(row["entry"])
            stop = float(row["stop"])
            target = float(row["target"])
            open_price = float(_field(trigger, "open"))
            high = float(_field(trigger, "high"))
            low = float(_field(trigger, "low"))

            if open_price > entry:
                group["entry_gaps"].append((open_price - entry) / entry * 10_000)
                gap_stop = low <= stop
                gap_target = high >= target
                group["trigger_gap_stops"] += int(gap_stop)
                group["trigger_gap_targets"] += int(gap_target)
                group["trigger_gap_both"] += int(gap_stop and gap_target)
                group["entry_gap_cross_target"] += int(open_price >= target)

        if outcome not in {"STOP", "TARGET"}:
            group["unresolved_trades"] += 1
            continue

        if not _present(row.get("exit_date")):
            group["missing_exit_bar"] += 1
            continue

        exit_bar = lookup.get((row["symbol"], _parse_time(row["exit_date"])))
        if exit_bar is None:
            group["missing_exit_bar"] += 1
            continue

        open_price = float(_field(exit_bar, "open"))
        reference = float(row["stop"] if outcome == "STOP" else row["target"])
        through = open_price < reference if outcome == "STOP" else open_price > reference
        if through:
            group["exit_gaps"].append(abs(open_price - reference) / reference * 10_000)

    results = []
    for (variant, target), group in sorted(groups.items()):
        entry_median, entry_p95 = _stats(group["entry_gaps"])
        exit_median, exit_p95 = _stats(group["exit_gaps"])
        results.append({
            "variant": variant,
            "target_multiple": target,
            "trades": group["trades"],
            "unresolved_trades": group["unresolved_trades"],
            "missing_trigger_bar": group["missing_trigger_bar"],
            "missing_exit_bar": group["missing_exit_bar"],
            "entry_gap_count": len(group["entry_gaps"]),
            "entry_gap_pct": len(group["entry_gaps"]) / group["trades"] * 100,
            "entry_gap_median_bps": entry_median,
            "entry_gap_p95_bps": entry_p95,
            "trigger_gap_stop_touch_count": group["trigger_gap_stops"],
            "trigger_gap_target_touch_count": group["trigger_gap_targets"],
            "trigger_gap_both_count": group["trigger_gap_both"],
            "entry_gap_cross_target_count": group["entry_gap_cross_target"],
            "exit_gap_count": len(group["exit_gaps"]),
            "exit_gap_pct": len(group["exit_gaps"]) / group["trades"] * 100,
            "exit_gap_median_bps": exit_median,
            "exit_gap_p95_bps": exit_p95,
        })

    return results
