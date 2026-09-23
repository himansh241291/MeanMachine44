from __future__ import annotations

import argparse
import csv
from pathlib import Path

from meanmachine44.market import load_csv
from meanmachine44.universe import filter_bars, load_membership_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--membership", required=True)
    parser.add_argument("--output", default="data/raw/nifty500_historical_universe_daily.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    bars = load_csv(root / args.input)
    universe = load_membership_csv(root / args.membership)
    filtered = filter_bars(bars, universe)

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["timestamp", "symbol", "timeframe", "open", "high", "low", "close"]
        )
        for bar in filtered:
            writer.writerow(
                [
                    bar.timestamp.isoformat(),
                    bar.symbol,
                    bar.timeframe,
                    bar.open,
                    bar.high,
                    bar.low,
                    bar.close,
                ]
            )

    print(f"input_rows={len(bars)}")
    print(f"output_rows={len(filtered)}")
    print(f"input_symbols={len({bar.symbol for bar in bars})}")
    print(f"output_symbols={len({bar.symbol for bar in filtered})}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
