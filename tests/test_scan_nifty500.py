from pathlib import Path

import pandas as pd


def test_scan_script_exists():
    assert Path("scripts/scan_nifty500.py").exists()


def test_scan_script_runs(tmp_path, monkeypatch):
    data = pd.DataFrame(
        [
            ["2026-01-02", "AAA", "1d", 10, 11, 9, 10.5],
            ["2026-01-09", "AAA", "1d", 11, 12, 10, 11.5],
        ],
        columns=["timestamp", "symbol", "timeframe", "open", "high", "low", "close"],
    )
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    data.to_csv(input_path, index=False)

    import runpy

    monkeypatch.setattr(
        "sys.argv",
        ["scan_nifty500.py", "--input", str(input_path), "--output", str(output_path)],
    )
    runpy.run_path("scripts/scan_nifty500.py", run_name="__main__")
    assert output_path.exists()
