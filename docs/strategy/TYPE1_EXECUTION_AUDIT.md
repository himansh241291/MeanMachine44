# Type 1 Execution Audit

This research audit measures daily-OHLC situations where the existing Type 1 trade model uses a fixed reference price but the trigger or exit bar opens beyond that reference.

It does not change strategy rules or backtest results.

## Entry gap

For a trigger bar, an entry gap is counted when the bar opens above the setup high used as the entry reference. The audit reports count, percentage, median gap, and 95th-percentile gap in basis points.

This identifies cases where a stop-style entry at the setup high could not be assumed to fill at that exact price on a daily bar.

## Exit gap

For a STOP outcome, an exit gap is counted when the exit bar opens below the stop reference.

For a TARGET outcome, an exit gap is counted when the exit bar opens above the target reference.

The audit reports the size of the price gap through the reference in basis points.

## Missing bars

Missing trigger or exit bars are reported rather than silently inferred.

## Important boundary

The audit is diagnostic. A future execution model must explicitly choose fill semantics for these cases. Those choices are execution assumptions, not newly defined MA44 source rules.

## Command

Run from the repository root:

    python scripts/audit_type1_execution.py

Output:

    data/output/type1_execution_audit.csv
