# Historical Universe Contract

The research engine supports date-effective universe membership separately from market-data and strategy logic.

## Membership CSV

Required columns:

```text
symbol,effective_from,effective_to
```

- `symbol`: instrument symbol.
- `effective_from`: ISO date, inclusive.
- `effective_to`: ISO date, exclusive; blank means membership remains active until the end of the supplied history.
- A symbol must not have overlapping membership intervals.
- Adjacent intervals are allowed.

Example:

```csv
symbol,effective_from,effective_to
AAA,2020-01-01,2020-06-01
AAA,2020-06-01,2021-01-01
BBB,2020-03-01,
```

## Research rule

Historical backtests must not silently use present-day constituent membership as a proxy for historical membership.

A historical universe file is an explicit research input. If it is unavailable, the backtest may still run on the supplied market dataset, but that run must remain identified as potentially survivorship-biased.

## Backtest application

For strategy backtests, membership is applied to the **setup date**, not by deleting non-member price bars.

This preserves continuous price history needed for SMA44 warm-up and for positions that remain open after an index removal. The backtest accepts the membership file directly:

```bash
python scripts/backtest_type1.py \
  --input data/raw/nifty500_daily.csv \
  --membership data/raw/nifty500_membership.csv \
  --end 2026-05-15 \
  --output data/output/type1_trades_pit.csv
```

A symbol is eligible for a setup only when it is a member on that setup date.

The existing `filter_historical_universe.py` command remains available for datasets that genuinely require bar-level universe filtering, but it should not be used as the input transformation for the MA44 strategy backtest.

## Filtering

Use:

```bash
python scripts/filter_historical_universe.py \
  --input data/raw/nifty500_daily.csv \
  --membership data/raw/nifty500_membership.csv \
  --output data/raw/nifty500_historical_universe_daily.csv
```

The filter performs no resampling, adjustment, interpolation, gap filling, or strategy logic. It only retains bars whose symbol is a member on the bar's calendar date.

The membership source, coverage dates, methodology, and any known gaps should be recorded with each research dataset.

## Provenance

The current point-in-time NIFTY 500 research source is the public `aditya-jha/nse-historical-membership` dataset, pinned by the MeanMachine44 importer to commit `0e9f58c4d457faf0e7ad3db4f4c1449e697e23e0`.

Its documentation states that index membership is derived from public NSE Indices press releases/circulars, with high-confidence coverage from 2017 onward and clean cardinality from 2018 onward. It also documents pre-2018 walk-back drift and inferred snapshot records.

For the first PIT experiment, MeanMachine44 uses a conservative source cutoff of **2026-03-30**. Records beginning after that date are excluded so inferred snapshot records beginning 2026-03-31 cannot overlap the press-release interval ending 2026-05-12 for symbols such as GSPL.

The imported membership file retains the source, source URL, and notes fields for auditability. This dataset is used only to model the historical NIFTY 500 universe; it does not define any MA44 strategy rule.


## Research cutoff

The daily portfolio and cost-sensitivity CLIs accept optional `--start` and `--end` UTC timestamps. Use the same cutoff as the universe-history coverage so the equity curve does not extend beyond the point-in-time membership experiment.
