# Type 1 Cost Sensitivity

This research layer evaluates the existing daily Type 1 portfolio backtest under alternative execution-cost assumptions. It does not change the MA44 setup, trigger, stop, target, or universe rules.

## Scenarios

The bundled scenarios are analytical stress profiles:

- **zero**: no execution friction.
- **low_friction**: low bundled trading friction.
- **moderate_friction**: moderate bundled trading friction.
- **high_friction**: high bundled trading friction.

These profiles are illustrative research assumptions, not a broker tariff, statutory schedule, or claim about actual transaction costs.

Each profile varies brokerage, exchange charges, sell-side STT, buy-side stamp duty, SEBI charges, GST on modeled fees, spread, and slippage through the existing CostModel.

## Coverage

The default runner evaluates:

- MA-touch reclaim at 1R, 2R, and 3R.
- Local-low reclaim at 1R, 2R, and 3R.
- All four cost profiles.

The output includes final equity, return, CAGR, maximum drawdown, profit factor, expectancy in R, trade counts, capital utilization, and modeled costs.

## CAGR and expectancy

CAGR is annualized from the first to the last timestamp in the generated daily equity curve using 365.25 days.

Expectancy is the mean net_r of closed trades after modeled costs.

Profit factor is total positive net P&L divided by the absolute value of total negative net P&L.

## Command

Run from the repository root:

    python scripts/cost_sensitivity_type1_daily.py

To select profiles explicitly:

    python scripts/cost_sensitivity_type1_daily.py --scenarios zero,low_friction

Output defaults to:

    data/output/type1_cost_sensitivity.csv

## Interpretation

This is a friction-survival diagnostic. A result that remains positive under one bundled profile is not proof of profitability, robustness, or live-trading viability.

The current daily backtest still has known execution simplifications and uses the historically current NIFTY 500 membership, so survivorship bias remains.


## Cost attribution

Each closed trade now exposes the full modeled friction stack:

- **explicit_fees**: brokerage, exchange, SEBI charges, GST on modeled fees, and the configured buy stamp duty / sell STT.
- **spread_cost**: the economic impact of the modeled bid/ask spread.
- **slippage_cost**: the economic impact of modeled slippage.
- **total_costs**: explicit fees plus spread and slippage.
- **turnover**: entry-reference notional plus exit-reference notional.
- **effective_cost_bps**: total modeled friction divided by turnover.

Gross P&L is measured before all modeled friction, using the entry and exit reference prices. Net P&L is reconciled against gross P&L minus total modeled costs. This makes the cost sensitivity output auditable without changing the strategy or execution assumptions.

The spread and slippage values remain analytical stress assumptions and are not broker or statutory claims.
