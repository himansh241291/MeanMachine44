from datetime import datetime, timezone

from meanmachine44.execution_audit import audit_execution
from meanmachine44.market import MarketBar


def row(outcome="TARGET"):
    return {
        "symbol": "TEST",
        "trigger_date": "2026-01-02T00:00:00+00:00",
        "exit_date": "2026-01-04T00:00:00+00:00",
        "entry": 100.0,
        "stop": 90.0,
        "target_multiple": 1,
        "target": 110.0,
        "outcome": outcome,
        "variant": "ma_touch_reclaim",
    }


def bars():
    return [
        MarketBar(datetime(2026, 1, 2, tzinfo=timezone.utc), "TEST", "1d", 105, 108, 100, 107),
        MarketBar(datetime(2026, 1, 4, tzinfo=timezone.utc), "TEST", "1d", 115, 120, 112, 118),
    ]


def test_audit_detects_entry_and_target_gap():
    result = audit_execution([row()], bars())[0]
    assert result["entry_gap_count"] == 1
    assert result["entry_gap_pct"] == 100.0
    assert result["entry_gap_median_bps"] == 500.0
    assert result["exit_gap_count"] == 1
    assert result["exit_gap_median_bps"] == (5 / 110) * 10_000


def test_audit_detects_adverse_stop_gap():
    item = row("STOP")
    result = audit_execution([item], [
        MarketBar(datetime(2026, 1, 2, tzinfo=timezone.utc), "TEST", "1d", 100, 108, 99, 105),
        MarketBar(datetime(2026, 1, 4, tzinfo=timezone.utc), "TEST", "1d", 80, 85, 75, 78),
    ])[0]
    assert result["exit_gap_count"] == 1


def test_audit_reports_missing_bars():
    result = audit_execution([row()], [bars()[0]])[0]
    assert result["missing_exit_bar"] == 1
    assert result["exit_gap_count"] == 0
