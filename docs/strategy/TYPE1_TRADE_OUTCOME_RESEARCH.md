# Type 1 Trade Outcome Research

This layer converts the existing Type 1 setup into explicit research trade levels. It is not claimed to be the final MA44 execution specification.

## Research assumptions

For a triggered setup:

- Entry reference = setup candle high.
- Stop reference = setup candle low.
- Risk = entry - stop.
- Targets are expressed as 1R, 2R, and 3R research levels.
- A future bar is evaluated using its high and low.
- The first observed target or stop touch is recorded.

These assumptions are research parameters. The source does not define universal target, fill, gap, slippage, or same-bar priority semantics.

## Important limitation

The current first-touch primitive treats a bar touching the stop as a stop outcome before checking targets on that same bar. This is a conservative deterministic convention for research and must be reviewed before using results as a trading simulation.

No profitability conclusion is drawn from this layer by itself.
