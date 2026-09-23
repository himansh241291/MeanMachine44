# Historical Data

Historical market data is kept outside the repository unless explicitly added for research reproducibility.

## CSV schema

`timestamp,symbol,timeframe,open,high,low,close`

- `timestamp`: ISO-8601 timestamp
- `symbol`: market symbol
- `timeframe`: source timeframe such as `1d` or `1w`
- `open,high,low,close`: finite numeric OHLC values

The loader is `meanmachine44.market.load_csv()`.

## Historical universe

Date-effective membership is a separate input:

`symbol,effective_from,effective_to`

The membership contract is documented in `docs/data/HISTORICAL_UNIVERSE_CONTRACT.md`.

No present-day constituent list should be silently treated as historical membership. Data provenance, date range, timeframe, timezone, universe source, and universe coverage must be recorded for research runs.

No market dataset is assumed by V1. 

## NIFTY 500 point-in-time membership

Use `scripts/import_nifty500_membership.py` to obtain the pinned historical membership table. The source is an external research dataset derived from public NSE Indices publications. The imported output is local research data and is not committed by default.

The importer is pinned to source commit `0e9f58c4d457faf0e7ad3db4f4c1449e697e23e0` for reproducibility.
