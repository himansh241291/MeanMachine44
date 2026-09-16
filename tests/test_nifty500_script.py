from scripts.download_nifty500 import load_constituents


def test_load_constituents_returns_unique_sorted_symbols():
    data = b"Symbol,Company Name\nRELIANCE,RELIANCE INDUSTRIES\nTCS,TATA CONSULTANCY\nRELIANCE,RELIANCE INDUSTRIES\n"
    assert load_constituents(data) == ["RELIANCE", "TCS"]
