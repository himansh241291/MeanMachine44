# Historical Data

Historical market data is kept outside the repository unless explicitly added for research reproducibility.

## CSV schema

`timestamp,symbol,timeframe,open,high,low,close`

- `timestamp`: ISO-8601 timestamp
- `symbol`: market symbol
- `timeframe`: source timeframe such as `1d` or `1w`
- `open,high,low,close`: finite numeric OHLC values

The loader is `meanmachine44.market.load_csv()`.

No market dataset is assumed by V1. Data provenance, date range, timeframe, and timezone must be recorded for research runs.
