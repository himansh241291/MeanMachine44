# Type 1 Execution Audit

This research audit measures daily-OHLC situations where the existing Type 1 trade model uses a fixed reference price but the trigger or exit bar opens beyond that reference.

It does not change strategy rules or backtest results.

## Entry gap

For a trigger bar, an entry gap is counted when the bar opens above the setup high used as the entry reference. The audit reports count, percentage, median gap, and 95th-percentile gap in basis points.

For gap-open trigger bars, the audit also reports whether the same bar touches the modeled stop or target, whether both are touched, and whether the open is already at or above the target. These cases matter because a long position is active from the open under a gap-aware entry model, while daily OHLC cannot determine stop-versus-target order when both levels are touched.

## Exit gap

For a STOP outcome, an exit gap is counted when the exit bar opens below the stop reference.

For a TARGET outcome, an exit gap is counted when the exit bar opens above the target reference.

The audit reports the size of the price gap through the reference in basis points.

## Unresolved and missing bars

Trades without a STOP or TARGET outcome are counted separately as unresolved trades and are not treated as missing exit bars.

A resolved trade with no matching exit-date bar is counted as a missing exit bar.

## Important boundary

The audit is diagnostic. A future execution model must explicitly choose fill semantics for these cases. Those choices are execution assumptions, not newly defined MA44 source rules.

## Command

Run from the repository root:

    python scripts/audit_type1_execution.py

Output:

    data/output/type1_execution_audit.csv

## Current audit checkpoint

Using the current historical Type 1 dataset, the six variant/target rows together report 2,475 trigger-gap bars touching the modeled stop, 2,368 touching the modeled target, 124 touching both, and 317 opening at or above the modeled target. These are descriptive audit counts, not execution results. Because daily OHLC does not establish intraday ordering when both levels are touched, the future execution layer must keep those cases explicit rather than silently assigning an order.
