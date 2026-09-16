# Historical Data Contract

V1 accepts historical market bars through CSV.

Required columns:

```text
timestamp,symbol,timeframe,open,high,low,close
```

Rules:

- `timestamp` is parsed with Python ISO-8601 datetime parsing.
- `symbol` and `timeframe` are required strings.
- `open`, `high`, `low`, and `close` are numeric OHLC values.
- OHLC validity follows the V1 `Candle` model.
- Rows are loaded in file order; the loader does not sort or resample data.
- No adjustment, interpolation, gap filling, timeframe alignment, or corporate-action handling is performed by the loader.
- Historical data used for research must be kept outside the strategy logic so the source rules remain unchanged.

Example:

```csv
timestamp,symbol,timeframe,open,high,low,close
2026-09-15T00:00:00+00:00,TEST,1d,100,105,99,104
```

The loader is intentionally small. Any later normalization or research methodology must be defined separately before implementation.
