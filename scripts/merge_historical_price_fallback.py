from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

KEYS = ["timestamp", "symbol", "timeframe"]
OHLC = ["open", "high", "low", "close"]
COLUMNS = KEYS + OHLC


def _load_market(path: str | Path, start: str, end: str) -> pd.DataFrame:
    frame = pd.read_csv(path)
    if not set(COLUMNS).issubset(frame.columns):
        missing = ", ".join(sorted(set(COLUMNS) - set(frame.columns)))
        raise ValueError(f"{path} is missing required market columns: {missing}")
    frame = frame[COLUMNS].copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], utc=True, errors="raise")
    frame["symbol"] = frame["symbol"].astype(str).str.strip()
    frame["timeframe"] = frame["timeframe"].astype(str).str.strip()
    for column in OHLC:
        frame[column] = pd.to_numeric(frame[column], errors="raise")
    start_at = pd.Timestamp(start, tz="UTC")
    end_at = pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
    frame = frame[(frame["timestamp"] >= start_at) & (frame["timestamp"] <= end_at)].copy()
    if frame.duplicated(KEYS).any():
        sample = frame.loc[frame.duplicated(KEYS, keep=False), KEYS].head(3).to_dict("records")
        raise ValueError(f"{path} contains duplicate market keys; examples: {sample}")
    return frame


def merge_missing_bars(
    primary: pd.DataFrame,
    fallback: pd.DataFrame,
    start: str = "2017-10-01",
    end: str = "2026-03-30",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = set(COLUMNS)
    if not required.issubset(primary.columns) or not required.issubset(fallback.columns):
        raise ValueError("both market frames must contain timestamp,symbol,timeframe,open,high,low,close")

    def normalize(frame: pd.DataFrame) -> pd.DataFrame:
        result = frame[COLUMNS].copy()
        result["timestamp"] = pd.to_datetime(result["timestamp"], utc=True, errors="raise")
        result["symbol"] = result["symbol"].astype(str).str.strip()
        result["timeframe"] = result["timeframe"].astype(str).str.strip()
        for column in OHLC:
            result[column] = pd.to_numeric(result[column], errors="raise")
        start_at = pd.Timestamp(start, tz="UTC")
        end_at = pd.Timestamp(end, tz="UTC") + pd.Timedelta(days=1) - pd.Timedelta(nanoseconds=1)
        result = result[(result["timestamp"] >= start_at) & (result["timestamp"] <= end_at)].copy()
        if result.duplicated(KEYS).any():
            raise ValueError("market frame contains duplicate timestamp,symbol,timeframe keys")
        return result

    primary = normalize(primary)
    fallback = normalize(fallback)
    primary_keys = pd.MultiIndex.from_frame(primary[KEYS])
    fallback_keys = pd.MultiIndex.from_frame(fallback[KEYS])
    missing_mask = ~fallback_keys.isin(primary_keys)
    additions = fallback.loc[missing_mask].copy()

    overlaps = fallback.loc[~missing_mask].merge(
        primary,
        on=KEYS,
        how="inner",
        suffixes=("_fallback", "_primary"),
    )
    mismatch = pd.Series(False, index=overlaps.index)
    for column in OHLC:
        mismatch |= (
            (overlaps[f"{column}_fallback"] - overlaps[f"{column}_primary"]).abs()
            > 1e-8
        )

    merged = pd.concat([primary, additions], ignore_index=True)
    merged = merged.sort_values(["symbol", "timestamp"]).reset_index(drop=True)

    all_symbols = sorted(set(primary["symbol"]) | set(fallback["symbol"]))
    audit_rows = []
    for symbol in all_symbols:
        p = primary[primary["symbol"] == symbol]
        f = fallback[fallback["symbol"] == symbol]
        ov = overlaps[overlaps["symbol"] == symbol]
        added = additions[additions["symbol"] == symbol]
        m = mismatch.loc[ov.index].sum() if not ov.empty else 0
        audit_rows.append(
            {
                "symbol": symbol,
                "primary_rows": len(p),
                "fallback_rows": len(f),
                "overlap_keys": len(ov),
                "overlap_ohlc_mismatch_keys": int(m),
                "fallback_rows_added": len(added),
                "merged_rows": len(p) + len(added),
            }
        )

    return merged[COLUMNS], pd.DataFrame(audit_rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Fill missing keys in the expanded historical-symbol dataset from the "
            "existing current-constituent dataset without overwriting primary bars."
        )
    )
    parser.add_argument("--primary", default="data/raw/nifty500_membership_daily_yfinance.csv")
    parser.add_argument("--fallback", default="data/raw/nifty500_daily.csv")
    parser.add_argument("--start", default="2017-10-01")
    parser.add_argument("--end", default="2026-03-30")
    parser.add_argument(
        "--output",
        default="data/raw/nifty500_membership_daily_merged.csv",
    )
    parser.add_argument(
        "--audit-output",
        default="data/output/historical_price_merge_audit.csv",
    )
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    primary = _load_market(root / args.primary, args.start, args.end)
    fallback = _load_market(root / args.fallback, args.start, args.end)
    merged, audit = merge_missing_bars(primary, fallback, args.start, args.end)

    output_path = root / args.output
    audit_path = root / args.audit_output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)
    audit.to_csv(audit_path, index=False)

    mismatch_count = int(audit["overlap_ohlc_mismatch_keys"].sum())
    print(f"primary_rows={len(primary)}")
    print(f"fallback_rows={len(fallback)}")
    print(f"overlap_keys={int(audit['overlap_keys'].sum())}")
    print(f"overlap_ohlc_mismatch_keys={mismatch_count}")
    print(f"fallback_rows_added={len(merged) - len(primary)}")
    print(f"merged_symbols={merged['symbol'].nunique()}")
    print(f"merged_rows={len(merged)}")
    print(f"data_output={output_path}")
    print(f"audit_output={audit_path}")
    print(
        "Policy: existing historical-download bars take precedence; the current-list "
        "dataset only fills missing timestamp/symbol/timeframe keys. OHLC mismatches "
        "are reported and do not overwrite primary bars."
    )


if __name__ == "__main__":
    main()
