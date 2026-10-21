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


## Critical price-history coverage limitation

The historical membership CSV does **not** by itself make a backtest fully point-in-time. The current `scripts/download_nifty500.py` gets the symbol list from the current NIFTY 500 constituents endpoint and downloads daily history only for that list. Applying historical membership to those bars cannot restore history for removed, merged, or delisted companies whose symbols are absent from the OHLC file. Results from this combination therefore retain universe survivorship/coverage bias and must not be described as a complete point-in-time NIFTY 500 backtest.

Audit coverage before interpreting the PIT results:

```bash
python scripts/audit_pit_price_coverage.py \
  --market data/raw/nifty500_daily.csv \
  --membership data/raw/nifty500_membership.csv \
  --start 2018-01-01 \
  --end 2026-03-30 \
  --output data/output/pit_price_coverage.csv
```

The audit reports, per year, how many membership-history symbols were active, how many had price bars in that period, and how many lack price data entirely in the supplied file. It uses exact symbol matches only; it does not resolve aliases, corporate actions, or price adjustments.

The next data requirement is a historical OHLC source that includes the actual constituents throughout the evaluation period, including constituents no longer in today's index, with documented delisting/renaming and corporate-action handling. Do not rerun or optimize the MA44 strategy until this coverage issue has been measured and a data-source plan is recorded.


## Historical-symbol OHLC recovery attempt

The current-member downloader does not request history for symbols that are no longer current constituents. A separate first-pass downloader can request each distinct symbol in the historical membership file from Yahoo Finance:

```bash
python scripts/download_historical_membership_prices.py \
  --membership data/raw/nifty500_membership.csv \
  --start 2017-10-01 \
  --end 2026-03-31 \
  --output data/raw/nifty500_membership_daily_yfinance.csv \
  --audit-output data/output/historical_membership_download_audit.csv
```

The end date is exclusive, so `2026-03-31` includes daily bars through March 30. The output is separate from the existing market file. The audit manifest records per-symbol success/no-data/chunk-error status and first/last available dates.

This is only a coverage-recovery attempt. Yahoo Finance may not retain delisted securities or old symbol aliases, and the downloader does not adjust for corporate actions. Re-run `scripts/audit_pit_price_coverage.py` against the candidate file and inspect remaining missing symbols. If material gaps remain, use a licensed historical EOD source that covers discontinued securities; NSE provides an official paid EOD/historical-data channel (see https://www.nseindia.com/static/market-data/eod-historical-data-subscription). The strategy must not be re-evaluated on the candidate file until its coverage and adjustment limitations are reviewed.
