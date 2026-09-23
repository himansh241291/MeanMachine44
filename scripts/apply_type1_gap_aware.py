from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.execution_model import apply_gap_aware_execution
from meanmachine44.market import load_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trades", default="data/output/type1_trades.csv")
    parser.add_argument("--market", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--output", default="data/output/type1_trades_gap_aware.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    trades = pd.read_csv(root / args.trades)
    bars = load_csv(root / args.market)
    frame = pd.DataFrame(apply_gap_aware_execution(trades.to_dict("records"), bars))

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output, index=False)

    print(f"rows={len(frame)}")
    print(f"output={output}")
    print("\nexecution_status")
    print(frame["execution_status"].value_counts(dropna=False).sort_index().to_string())
    print("\noutcome_changes")
    before = frame["baseline_outcome"].fillna("NONE")
    after = frame["outcome"].fillna("NONE")
    changes = frame.loc[before != after].copy()
    if changes.empty:
        print("none")
    else:
        print(pd.crosstab(changes["baseline_outcome"].fillna("NONE"), changes["outcome"].fillna("NONE")).to_string())


if __name__ == "__main__":
    main()
