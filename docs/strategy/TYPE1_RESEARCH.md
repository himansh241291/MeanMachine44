# Type 1 Research Definition

**Status:** `RESEARCH_PARAMETER`

The MA44 source describes Type 1 as rising MA44 + support. The source does not provide a machine definition of support, so this document defines a research candidate only.

## Candidate definition

A daily bar is considered a Type 1 support candidate when:

1. Daily SMA44 is rising for at least 3 completed periods.
2. The bar's low is below or equal to the daily SMA44.
3. The bar closes above the daily SMA44.
4. The bar is bullish (`close > open`).

This definition is intentionally simple and testable. It is **not** treated as the MA44 source rule.

## Not included

This candidate does not claim to identify structural support, horizontal support, swing lows, retests, double bottoms, or any other support pattern. Those remain separate research questions.

## Entry boundary

A qualifying candidate may later be paired with the existing pending-buy mechanic: entry above the trigger bar high and stop reference at the trigger bar low. Gap behavior and intrabar execution remain undefined.

## Research use

This definition is a baseline candidate for historical testing. It must be compared with alternative support definitions rather than accepted because it produces a favorable result.
