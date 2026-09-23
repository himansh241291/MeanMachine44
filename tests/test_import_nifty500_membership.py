import pandas as pd
import pytest

from scripts.import_nifty500_membership import normalize_nifty500


def test_normalize_nifty500():
    frame = pd.DataFrame(
        {
            "index_name": ["Nifty 500", "Nifty 500", "Nifty 50"],
            "symbol": ["AAA", "AAA", "AAA"],
            "valid_from": ["2020-01-01", "2020-06-01", "2020-01-01"],
            "valid_to": ["2020-06-01", None, None],
        }
    )
    result = normalize_nifty500(frame)
    assert result.to_dict("records") == [
        {"symbol": "AAA", "effective_from": pd.Timestamp("2020-01-01").date(), "effective_to": pd.Timestamp("2020-06-01").date()},
        {"symbol": "AAA", "effective_from": pd.Timestamp("2020-06-01").date(), "effective_to": None},
    ]


def test_normalize_nifty500_requires_columns():
    with pytest.raises(ValueError):
        normalize_nifty500(pd.DataFrame({"symbol": ["AAA"]}))
