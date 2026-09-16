import importlib.util
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "download_nifty500", Path(__file__).parents[1] / "scripts" / "download_nifty500.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_load_constituents_returns_unique_sorted_symbols():
    data = b"Symbol,Company Name\nRELIANCE,RELIANCE INDUSTRIES\nTCS,TATA CONSULTANCY\nRELIANCE,RELIANCE INDUSTRIES\n"
    assert MODULE.load_constituents(data) == ["RELIANCE", "TCS"]
