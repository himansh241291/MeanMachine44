from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def analyze(path: str | Path) -> pd.DataFrame:
    frame = pd.read_csv(path)
    required = {"setup_date", "variant", "target_multiple", "outcome", "executed_r"}
    if not required.issubset(frame.columns):
        missing = ", ".join(sorted(required - set(frame.columns)))
        raise ValueError(f"trade file missing required columns: {missing}")

    frame["setup_date"] = pd.to_datetime(frame["setup_date"], utc=True)
    frame["year"] = frame["setup_date"].dt.year
    frame["executed_r"] = pd.to_numeric(frame["executed_r"], errors="coerce")
    closed = frame[frame["outcome"].isin(["STOP", "TARGET"])].copy()
    result = (
        closed.groupby(["year", "variant", "target_multiple"])
        .agg(
            trades=("outcome", "size"),
            wins=("outcome", lambda value: (value == "TARGET").sum()),
            total_executed_r=("executed_r", "sum"),
            avg_executed_r=("executed_r", "mean"),
        )
        .reset_index()
    )
    result["win_rate_pct"] = result["wins"] / result["trades"] * 100
    return result[
        [
            "year",
            "variant",
            "target_multiple",
            "trades",
            "wins",
            "win_rate_pct",
            "total_executed_r",
            "avg_executed_r",
        ]
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trades",
        default="data/output/type1_trades_pit_gap_aware.csv",
    )
    parser.add_argument(
        "--output",
        default="data/output/type1_pit_gap_yearly.csv",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    result = analyze(root / args.trades)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output, index=False)
    print(result.to_string(index=False))
    print(f"output={output}")


if __name__ == "__main__":
    main()
