from pathlib import Path


def test_data_script_is_root_relative():
    path = Path(__file__).parents[1] / "scripts" / "download_daily_data.py"
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert 'parents[1]' in text
    assert 'data/raw/market.csv' in text
