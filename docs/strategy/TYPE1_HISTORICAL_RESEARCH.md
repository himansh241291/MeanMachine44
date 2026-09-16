# Type 1 Historical Research

**Status:** `RESEARCH`

## Baseline definition

The experiment uses the Type 1 candidate definition documented in `TYPE1_RESEARCH.md`:

- daily SMA44 rising for at least 3 completed periods;
- bar low <= daily SMA44;
- bar close > daily SMA44;
- bullish bar (`close > open`).

This is a research parameter, not a source rule.

## Entry model

For each qualifying setup bar, the first later bar whose high exceeds the setup high is recorded as the trigger. Entry is the setup high and the initial stop reference is the setup low.

Gap-through behavior, intrabar ordering, slippage and transaction costs remain `UNDEFINED`.

## Current baseline observations

Using the current NIFTY 500 dataset (2018-01-01 through 2026-09-16) produced 20,485 Type 1 candidate setup rows, of which 20,226 had a later trigger under the simple replay rule.

These counts demonstrate frequency, not profitability or edge. They should not be treated as evidence that the Type 1 definition is suitable for live trading.
