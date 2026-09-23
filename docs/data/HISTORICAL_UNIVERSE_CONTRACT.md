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
