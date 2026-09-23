from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.execution_audit import audit_execution
from meanmachine44.market import load_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trades", default="data/output/type1_trades.csv")
    parser.add_argument("--market", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--output", default="data/output/type1_execution_audit.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    trades = pd.read_csv(root / args.trades)
    bars = load_csv(root / args.market)
    results = audit_execution(trades.to_dict("records"), bars)

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(output, index=False)

    print(f"rows={len(results)}")
    print(f"output={output}")
    print(pd.DataFrame(results).to_string(index=False))
    if results:
        print("\ntrigger-gap interaction totals")
        frame = pd.DataFrame(results)
        cols = ["trigger_gap_stop_touch_count", "trigger_gap_target_touch_count", "trigger_gap_both_count", "entry_gap_cross_target_count"]
        print(frame[cols].sum().to_string())


if __name__ == "__main__":
    main()
