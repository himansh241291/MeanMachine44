# Type 1 Research Comparison

Status: RESEARCH ONLY. These candidate definitions are experimental parameterizations, not MA44 source rules.

## Current baseline

`ma_touch_reclaim` requires:

- Daily SMA44 rising for at least 3 periods.
- Candle low at or below SMA44.
- Candle closes above SMA44.
- Bullish candle (`close > open`).

This produced 20,485 setup rows on the current NIFTY 500 daily dataset.

## Candidate variant

`local_low_reclaim` uses a 5-bar prior-low reference:

- Daily SMA44 rising for at least 3 periods.
- Current candle low at or below the minimum low of the prior 5 bars.
- Candle closes above that prior-low reference.
- Bullish candle.

This produced 18,717 setup rows on the same dataset.

## Interpretation

The local-low condition is more selective in this baseline experiment. The count difference alone does not establish that one definition is better. The next research step is to compare the variants using identical, explicitly defined outcome measurements and separate in-sample/out-of-sample periods.

## Dataset caveat

The historical file uses the current NIFTY 500 constituent universe retrospectively. Historical results therefore do not represent a survivorship-bias-free reconstruction of historical NIFTY 500 membership.
