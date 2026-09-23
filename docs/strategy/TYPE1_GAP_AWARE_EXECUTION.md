# Type 1 Gap-Aware Execution Model

This research layer transforms the existing Type 1 trade file into a gap-aware execution representation. It does not change the MA44 setup, trigger condition, stop, target, or universe.

## Deterministic cases

- A trigger bar that opens above the setup-high entry reference uses the trigger open as the entry fill reference.
- If that gap-open trigger touches only the stop, the trade is resolved as STOP at the stop reference.
- If it touches only the target, the trade is resolved as TARGET at the target reference. If the trigger opens at or above the target, the open is used as the exit fill reference.
- On a later resolved exit bar, a stop gap through the stop uses the bar open; a target gap through the target uses the bar open. Otherwise the level reference is used.

## Ambiguous cases

If the trigger bar touches both stop and target after a gap-open, the trade is marked `AMBIGUOUS_TRIGGER` and excluded from resolved outcomes.

If the resolved exit bar touches both stop and target, the trade is marked `AMBIGUOUS_EXIT` and excluded from resolved outcomes.

Daily OHLC cannot establish intraday ordering in those cases. Excluding them avoids inventing information.

## Output

The transformed trade file keeps the baseline outcome/date and adds `entry_fill`, `exit_fill`, `execution_model`, and `execution_status` fields.

## Command

    python scripts/apply_type1_gap_aware.py

Output:

    data/output/type1_trades_gap_aware.csv

After generation, the existing daily portfolio and cost-sensitivity runners can consume this file because they honor the optional fill fields.

## Boundary

These are execution research assumptions, not additional MA44 source rules. The existing reference-price model remains the comparison baseline.
