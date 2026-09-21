# Type 1 Daily Portfolio Backtest

This is the daily mark-to-market extension of the Type 1 portfolio research layer. It does not alter the MA44 setup, trigger, stop, or target construction.

## What is added

Each trading day is processed chronologically. Open positions are valued using the latest observed daily close for that symbol. Exit events use the previously determined research exit reference on the exit date.

The equity curve contains:

- Cash
- Marked market value of open positions
- Total equity
- Open position count
- Capital utilization

Drawdown is calculated from this daily equity series.

## Position sizing

The research defaults remain:

- Initial capital: 1,000,000.
- Risk budget: 1% of current marked equity per trade.
- Maximum open positions: 10.
- Maximum position value: 20% of current marked equity.

These are research assumptions, not MA44 source rules.

## Limitations

The trade layer still determines stop/target dates from the future daily bars. This daily portfolio layer therefore does not replace the event-driven execution model.

The entry remains a research reference at the setup high when a later bar exceeds it. Gap handling and intraday sequencing are still undefined.

Unresolved trades are excluded because no timeout exit policy has been defined.

The current dataset uses current NIFTY 500 constituents historically and therefore remains subject to survivorship bias.

## Interpretation

A daily equity curve is a stronger diagnostic than realized-only equity, but it is still not a profitability conclusion. Costs, execution assumptions, survivorship bias, overlapping positions, and parameter robustness must be addressed before drawing conclusions.
