# Type 1 Backtest

This is a research backtest for the two current Type 1 support definitions. It is not the final MA44 execution specification.

## Trade construction

1. A Type 1 setup must qualify on a daily bar.
2. Entry occurs only after a later bar's high is strictly above the setup high.
3. Entry reference = setup high.
4. Stop reference = setup low.
5. Risk = entry - stop.
6. Research target levels = 1R, 2R, 3R.
7. The first later bar touching the stop or a target determines the labeled outcome.
8. The evaluation window ends at the configured horizon after the setup.

## Daily OHLC limitation

The trigger bar is the entry bar. Daily OHLC does not reveal the intraday order in which entry, stop, and target levels were reached. The current implementation therefore begins first-touch evaluation after the trigger bar rather than inventing an intraday sequence for that bar.

## Profit interpretation

A labeled 1R, 2R, or 3R outcome is a fixed research exit at that level. STOP is -1R. A trade with no first touch inside the horizon is reported separately and is not assigned a profit or loss.

No slippage, brokerage, taxes, spread, position sizing, compounding, or gap-fill assumptions are included.
