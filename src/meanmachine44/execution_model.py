from __future__ import annotations

from collections.abc import Mapping
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

def _lookup(bars: list[object]) -> dict[tuple[str, datetime], object]:
    result = {}
    for bar in bars:
        timestamp = bar.timestamp if hasattr(bar, "timestamp") else _parse_time(bar["timestamp"])
        symbol = bar.symbol if hasattr(bar, "symbol") else bar["symbol"]
        result[(symbol, timestamp)] = bar
    return result

def _set_executed_r(row: dict) -> None:
    entry = row.get("entry_fill")
    exit_price = row.get("exit_fill")
    stop = row.get("stop")
    if (
        row.get("outcome") in {"STOP", "TARGET"}
        and entry is not None
        and exit_price is not None
        and stop is not None
        and float(entry) > float(stop)
    ):
        row["executed_r"] = (
            float(exit_price) - float(entry)
        ) / (float(entry) - float(stop))
    else:
        row["executed_r"] = None


def apply_gap_aware_execution(rows: list[dict], bars: list[object]) -> list[dict]:
    lookup = _lookup(bars)
    output = []
    for source in rows:
        row = dict(source)
        row["baseline_outcome"] = source.get("outcome")
        row["baseline_exit_date"] = source.get("exit_date")
        row["execution_model"] = "gap_aware"
        row["execution_status"] = "UNRESOLVED"
        row["entry_fill"] = None
        row["exit_fill"] = None
        row["executed_r"] = None
        row["trigger_gap"] = False
        row["exit_gap"] = False
        trigger_date = source.get("trigger_date")
        if not _present(trigger_date):
            row["execution_status"] = "MISSING_TRIGGER_BAR"
            output.append(row)
            continue
        trigger = lookup.get((source["symbol"], _parse_time(trigger_date)))
        if trigger is None:
            row["execution_status"] = "MISSING_TRIGGER_BAR"
            output.append(row)
            continue
        entry = float(source["entry"])
        stop = float(source["stop"])
        target = float(source["target"])
        trigger_open = float(_field(trigger, "open"))
        trigger_high = float(_field(trigger, "high"))
        trigger_low = float(_field(trigger, "low"))
        gap = trigger_open > entry
        row["trigger_gap"] = gap
        row["entry_fill"] = trigger_open if gap else entry
        if gap:
            stop_touch = trigger_low <= stop
            target_touch = trigger_high >= target
            if stop_touch and target_touch:
                row["outcome"] = None
                row["exit_date"] = None
                row["execution_status"] = "AMBIGUOUS_TRIGGER"
                output.append(row)
                continue
            if trigger_open >= target or target_touch:
                row["outcome"] = "TARGET"
                row["exit_date"] = trigger_date
                row["exit_fill"] = trigger_open if trigger_open >= target else target
                row["execution_status"] = "TRIGGER_TARGET"
                _set_executed_r(row)
                output.append(row)
                continue
            if stop_touch:
                row["outcome"] = "STOP"
                row["exit_date"] = trigger_date
                row["exit_fill"] = stop
                row["execution_status"] = "TRIGGER_STOP"
                _set_executed_r(row)
                output.append(row)
                continue
        outcome = source.get("outcome")
        exit_date = source.get("exit_date")
        if outcome not in {"STOP", "TARGET"} or not _present(exit_date):
            row["execution_status"] = "UNRESOLVED"
            output.append(row)
            continue
        exit_bar = lookup.get((source["symbol"], _parse_time(exit_date)))
        if exit_bar is None:
            row["execution_status"] = "MISSING_EXIT_BAR"
            output.append(row)
            continue
        exit_open = float(_field(exit_bar, "open"))
        exit_high = float(_field(exit_bar, "high"))
        exit_low = float(_field(exit_bar, "low"))
        stop_touch = exit_low <= stop
        target_touch = exit_high >= target
        if stop_touch and target_touch:
            row["outcome"] = None
            row["exit_date"] = None
            row["execution_status"] = "AMBIGUOUS_EXIT"
            output.append(row)
            continue
        reference = stop if outcome == "STOP" else target
        exit_fill = exit_open if (outcome == "STOP" and exit_open < reference) or (outcome == "TARGET" and exit_open > reference) else reference
        row["exit_fill"] = exit_fill
        row["exit_gap"] = exit_fill != reference
        row["execution_status"] = "EXIT_GAP" if row["exit_gap"] else "REFERENCE_FILL"
        _set_executed_r(row)
        output.append(row)
    return output
