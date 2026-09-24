from pathlib import Path

import pandas as pd
import pytest

from scripts.analyze_type1_yearly import analyze


def test_analyze_uses_executed_r(tmp_path: Path):
    frame = pd.DataFrame(
        {
            "setup_date": ["2026-01-01", "2026-01-02", "2026-01-03"],
            "variant": ["ma_touch_reclaim"] * 3,
            "target_multiple": [2, 2, 2],
            "outcome": ["TARGET", "STOP", None],
            "r": [2.0, -1.0, None],
            "executed_r": [1.0, -1.5, None],
        }
    )
    path = tmp_path / "trades.csv"
    frame.to_csv(path, index=False)
    result = analyze(path)
    row = result.iloc[0]
    assert row["trades"] == 2
    assert row["wins"] == 1
    assert row["total_executed_r"] == pytest.approx(-0.5)
    assert row["avg_executed_r"] == pytest.approx(-0.25)
