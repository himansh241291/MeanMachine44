from __future__ import annotations

import argparse
import io
from pathlib import Path

import pandas as pd
import requests

SOURCE_URL = (
    "https://raw.githubusercontent.com/aditya-jha/"
    "nse-historical-membership/"
    "0e9f58c4d457faf0e7ad3db4f4c1449e697e23e0/"
    "index_history/data/index_membership_history.csv"
)


def load_source(url: str = SOURCE_URL) -> pd.DataFrame:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return pd.read_csv(io.BytesIO(response.content))


def normalize_nifty500(
    frame: pd.DataFrame,
    cutoff: str = "2026-03-30",
) -> pd.DataFrame:
    required = {"index_name", "symbol", "valid_from", "valid_to", "source", "source_url", "notes"}
    if not required.issubset(frame.columns):
        raise ValueError("source must contain index_name,symbol,valid_from,valid_to")
    result = frame.loc[
        frame["index_name"].astype(str).str.strip().str.casefold() == "nifty 500",
        ["symbol", "valid_from", "valid_to", "source", "source_url", "notes"],
    ].copy()
    if result.empty:
        raise ValueError("source contains no Nifty 500 membership rows")
    result["symbol"] = result["symbol"].astype(str).str.strip()
    cutoff_date = pd.Timestamp(cutoff).date()
    result["effective_from"] = pd.to_datetime(
        result["valid_from"], errors="raise"
    ).dt.date
    result["effective_to"] = pd.to_datetime(
        result["valid_to"], errors="coerce"
    ).dt.date.map(lambda value: value if pd.notna(value) else None)
    result = result[result["effective_from"] <= cutoff_date].copy()
    result = result[
        ["symbol", "effective_from", "effective_to", "source", "source_url", "notes"]
    ]
    result = result.drop_duplicates().sort_values(["symbol", "effective_from"])
    for symbol, part in result.groupby("symbol", sort=False):
        previous_end = None
        for _, row in part.iterrows():
            if previous_end is None and row["effective_from"] > part.iloc[0]["effective_from"]:
                raise ValueError(f"open-ended membership interval before {symbol}")
            if previous_end is not None and row["effective_from"] < previous_end:
                raise ValueError(f"overlapping membership intervals for {symbol}")
            previous_end = row["effective_to"]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cutoff", default="2026-03-30")
    parser.add_argument("--output", default="data/raw/nifty500_membership.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)

    frame = normalize_nifty500(load_source(), cutoff=args.cutoff)
    frame.to_csv(output, index=False)
    print(f"rows={len(frame)}")
    print(f"symbols={frame['symbol'].nunique()}")
    print(f"effective_from={frame['effective_from'].min()}")
    print(f"effective_to={frame['effective_to'].dropna().max()}")
    print(f"source_cutoff={args.cutoff}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
