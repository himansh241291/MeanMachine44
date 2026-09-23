from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.cost_sensitivity import run_cost_sensitivity, select_scenarios
from meanmachine44.daily_portfolio import DailyPortfolioConfig
from meanmachine44.market import load_csv


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trades", default="data/output/type1_trades.csv")
    parser.add_argument("--market", default="data/raw/nifty500_daily.csv")
    parser.add_argument(
        "--scenarios",
        default="zero,low_friction,moderate_friction,high_friction",
    )
    parser.add_argument("--initial-capital", type=float, default=1_000_000)
    parser.add_argument("--risk-per-trade", type=float, default=0.01)
    parser.add_argument("--max-open-positions", type=int, default=10)
    parser.add_argument("--max-position-pct", type=float, default=0.20)
    parser.add_argument("--output", default="data/output/type1_cost_sensitivity.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    trades = pd.read_csv(root / args.trades)
    bars = load_csv(root / args.market)

    config = DailyPortfolioConfig(
        initial_capital=args.initial_capital,
        risk_per_trade=args.risk_per_trade,
        max_open_positions=args.max_open_positions,
        max_position_pct=args.max_position_pct,
    )
    results = run_cost_sensitivity(
        trades.to_dict("records"),
        bars,
        config,
        select_scenarios(args.scenarios),
    )

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(output, index=False)

    print(f"rows={len(results)}")
    print(f"output={output}")


if __name__ == "__main__":
    main()
