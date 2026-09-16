# Type 1 Outcome Research

This experiment measures what happens after a qualifying Type 1 setup in historical data.

## What is measured

For each setup, the first later daily bar whose high is strictly above the setup candle high is recorded as a trigger.

Reported counts:

- `setups`: qualifying setup bars.
- `triggered`: setups with a later trigger.
- `untriggered`: setups without a later trigger in the available data.
- `trigger_rate_pct`: triggered / setups.
- Delay is measured in daily bars from setup to first trigger.

## Execution discipline

This is an outcome-labeling experiment, not a trading simulator. It does not assume an order-fill price, slippage, gap-fill behavior, target, position sizing, stop execution, or transaction costs.

The trigger remains strictly later than the setup candle. A setup candle cannot trigger itself.

## Variants

The current comparison uses two explicitly labeled research parameters:

1. `ma_touch_reclaim`: rising SMA44; low at or below SMA44; close above SMA44; bullish candle.
2. `local_low_reclaim`: rising SMA44; setup low at or below the minimum of the prior `N` lows; close above that local support; bullish candle.

`N=5` is a research parameter and is not an MA44 source rule.

## Interpretation

Trigger rate and delay are descriptive historical measurements only. They do not establish profitability or superiority. Different support definitions change the sample population and must be evaluated with the same downstream methodology.

The historical NIFTY 500 dataset uses the current constituent universe, so these results should not be interpreted as survivorship-bias-free historical index results.
