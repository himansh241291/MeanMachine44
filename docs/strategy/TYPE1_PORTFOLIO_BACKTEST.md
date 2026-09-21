# Type 1 Portfolio Backtest

This layer converts the resolved Type 1 trade outcomes into a portfolio-level research simulation. It does not change the MA44 setup or entry rules.

## Research parameters

The current CLI defaults are deliberately assumptions rather than MA44 source rules:

- Initial capital: 1,000,000.
- Risk budget: 1% of available cash per trade.
- Maximum open positions: 10.
- Maximum position value: 20% of available cash.
- Unresolved trades are excluded because the current trade layer does not define a timeout exit price.

These defaults can and should be changed for sensitivity testing.

## Position sizing

Quantity is based on risk budget divided by the entry reference minus the stop reference, then capped by available cash and maximum position value.

The portfolio model uses integer shares.

## Execution and costs

The entry and exit references come from the existing Type 1 trade layer. The portfolio model can apply configurable research parameters for brokerage, exchange charges, STT, stamp duty, SEBI charges, GST, spread, and slippage.

All cost defaults are zero. They are not assertions about current Indian broker or statutory rates.

The named cost components are represented as configurable bps/rates and are therefore a simplified research model, not a broker tax calculator.

## Portfolio behavior

Entries are processed chronologically. Positions exit before entries on the same date. A new position is skipped when the maximum number of open positions is reached or the same symbol is already open.

Drawdown is calculated on realized portfolio equity after closed trades. Open positions are not marked to market between exit events, so this is not yet a full daily equity-curve simulation.

## Interpretation

net_pnl is expressed in the configured account currency units. It is a research result under the selected portfolio and cost assumptions.

Results must not be interpreted as evidence of future profitability. The next robustness layers should address daily mark-to-market equity, survivorship bias, portfolio overlap, execution/gap behavior, and parameter sensitivity.
