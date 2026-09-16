import importlib.util
from pathlib import Path

import pandas as pd


SCRIPT = Path(__file__).parents[1] / "scripts" / "report_nifty500_scan.py"
SPEC = importlib.util.spec_from_file_location("report_nifty500_scan", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)
main = MODULE.main


def test_report_writes_candidate_metrics(tmp_path, monkeypatch):
    root = tmp_path
    data = root / "raw.csv"
    scan = root / "scan.csv"
    output = root / "report.csv"

    dates = pd.date_range("2025-01-01", periods=50, freq="D", tz="UTC")
    pd.DataFrame({
        "timestamp": dates,
        "symbol": "TEST",
        "timeframe": "1d",
        "open": range(1, 51),
        "high": range(2, 52),
        "low": range(0, 50),
        "close": range(1, 51),
    }).to_csv(data, index=False)
    pd.DataFrame({"symbol": ["TEST"], "as_of": ["2025-02-19"]}).to_csv(scan, index=False)

    monkeypatch.setattr(
        "sys.argv",
        ["report_nifty500_scan.py", "--input", str(data), "--scan", str(scan), "--output", str(output)],
    )

    main()
    result = pd.read_csv(output)
    assert list(result.columns) == [
        "symbol", "as_of", "close", "daily_sma44", "daily_sma44_prev", "weekly_sma44", "weekly_sma44_prev"
    ]
    assert len(result) == 1
