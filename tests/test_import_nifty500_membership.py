import pandas as pd
import pytest

from scripts.import_nifty500_membership import normalize_nifty500


def source_frame():
    return pd.DataFrame(
        {
            "index_name": ["Nifty 500", "Nifty 500", "Nifty 50"],
            "symbol": ["AAA", "AAA", "AAA"],
            "valid_from": ["2020-01-01", "2020-06-01", "2020-01-01"],
            "valid_to": ["2020-06-01", None, None],
            "source": ["press_release", "snapshot", "press_release"],
            "source_url": ["url1", "url2", "url3"],
            "notes": ["note1", "note2", "note3"],
        }
    )


def test_normalize_nifty500():
    result = normalize_nifty500(source_frame(), cutoff="2026-03-30")
    assert result.to_dict("records") == [
        {
            "symbol": "AAA",
            "effective_from": pd.Timestamp("2020-01-01").date(),
            "effective_to": pd.Timestamp("2020-06-01").date(),
            "source": "press_release",
            "source_url": "url1",
            "notes": "note1",
        },
        {
            "symbol": "AAA",
            "effective_from": pd.Timestamp("2020-06-01").date(),
            "effective_to": None,
            "source": "snapshot",
            "source_url": "url2",
            "notes": "note2",
        },
    ]


def test_normalize_nifty500_cutoff_excludes_later_intervals():
    frame = source_frame()
    frame.loc[0, "valid_from"] = "2026-04-01"
    frame.loc[0, "valid_to"] = None
    result = normalize_nifty500(frame, cutoff="2026-03-30")
    assert result.empty


def test_normalize_nifty500_requires_columns():
    with pytest.raises(ValueError):
        normalize_nifty500(pd.DataFrame({"symbol": ["AAA"]}))


def test_normalize_nifty500_rejects_open_ended_interval_before_later_interval():
    frame = pd.DataFrame(
        {
            "index_name": ["Nifty 500", "Nifty 500"],
            "symbol": ["AAA", "AAA"],
            "valid_from": ["2020-01-01", "2020-06-01"],
            "valid_to": [None, None],
            "source": ["snapshot", "snapshot"],
            "source_url": ["u1", "u2"],
            "notes": ["n1", "n2"],
        }
    )
    with pytest.raises(ValueError):
        normalize_nifty500(frame)


def test_normalize_nifty500_keeps_interval_that_started_before_cutoff():
    frame = source_frame()
    frame.loc[1, "valid_from"] = "2026-03-30"
    frame.loc[1, "valid_to"] = "2026-05-12"
    result = normalize_nifty500(frame, cutoff="2026-03-30")
    assert result.iloc[-1]["effective_from"] == pd.Timestamp("2026-03-30").date()
