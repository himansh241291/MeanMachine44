from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from meanmachine44.market import load_csv
from meanmachine44.portfolio import CostModel
from meanmachine44.daily_portfolio import DailyPortfolioConfig, simulate_daily


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trades", default="data/output/type1_trades.csv")
    parser.add_argument("--market", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--variant", choices=("ma_touch_reclaim", "local_low_reclaim"), default="ma_touch_reclaim")
    parser.add_argument("--target", type=int, choices=(1, 2, 3), default=1)
    parser.add_argument("--initial-capital", type=float, default=1_000_000)
    parser.add_argument("--risk-per-trade", type=float, default=0.01)
    parser.add_argument("--max-open-positions", type=int, default=10)
    parser.add_argument("--max-position-pct", type=float, default=0.20)
    parser.add_argument("--start")
    parser.add_argument("--end")
    parser.add_argument("--brokerage-bps", type=float, default=0.0)
    parser.add_argument("--exchange-bps", type=float, default=0.0)
    parser.add_argument("--stt-sell-bps", type=float, default=0.0)
    parser.add_argument("--stamp-buy-bps", type=float, default=0.0)
    parser.add_argument("--sebi-bps", type=float, default=0.0)
    parser.add_argument("--gst-rate", type=float, default=0.0)
    parser.add_argument("--spread-bps", type=float, default=0.0)
    parser.add_argument("--slippage-bps", type=float, default=0.0)
    parser.add_argument("--output", default="data/output/type1_daily_equity.csv")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    trades = pd.read_csv(root / args.trades)
    part = trades[
        (trades["variant"] == args.variant)
        & (trades["target_multiple"] == args.target)
    ].copy()
    rows = part.to_dict("records")
    bars = load_csv(root / args.market)
    if args.start or args.end:
        start = pd.Timestamp(args.start, tz="UTC") if args.start else None
        end = pd.Timestamp(args.end, tz="UTC") if args.end else None
        bars = [
            bar for bar in bars
            if (start is None or bar.timestamp >= start)
            and (end is None or bar.timestamp <= end)
        ]
    result = simulate_daily(
        rows,
        bars,
        DailyPortfolioConfig(
            initial_capital=args.initial_capital,
            risk_per_trade=args.risk_per_trade,
            max_open_positions=args.max_open_positions,
            max_position_pct=args.max_position_pct,
        ),
        CostModel(
            brokerage_bps=args.brokerage_bps,
            exchange_bps=args.exchange_bps,
            stt_sell_bps=args.stt_sell_bps,
            stamp_buy_bps=args.stamp_buy_bps,
            sebi_bps=args.sebi_bps,
            gst_rate=args.gst_rate,
            spread_bps=args.spread_bps,
            slippage_bps=args.slippage_bps,
        ),
    )

    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(result["equity_curve"]).to_csv(output, index=False)

    print(f"variant={args.variant} target={args.target}R")
    for key in (
        "initial_capital",
        "final_equity",
        "net_pnl",
        "return_pct",
        "max_drawdown_pct",
        "closed_trades",
        "open_trades",
        "unresolved_trades",
        "skipped_entries",
        "peak_open_positions",
        "peak_capital_utilization_pct",
        "total_costs",
    ):
        print(f"{key}={result[key]}")


if __name__ == "__main__":
    main()
