"""CLI to generate feature datasets from DuckDB trades."""
from __future__ import annotations

import argparse
from pathlib import Path

from .features import build_and_save_features


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate resampled feature set from trades")
    parser.add_argument("symbol", help="Trading pair symbol, e.g. BTCUSDT")
    parser.add_argument(
        "--output",
        type=Path,
        help="Destination Parquet file",
        default=None,
    )
    parser.add_argument("--start-ts", type=int, default=None, help="Start timestamp (ms)")
    parser.add_argument("--end-ts", type=int, default=None, help="End timestamp (ms)")
    parser.add_argument("--resample", default="1min", help="Pandas resample rule (default 1min)")
    parser.add_argument(
        "--rolling", nargs="*", type=int, default=[3, 5, 15], help="Rolling window lengths"
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("storage/trades.db"),
        help="Path to DuckDB database",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("storage/features"),
        help="Directory for generated features when --output omitted",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output = args.output
    if output is None:
        output = args.outdir / f"{args.symbol.lower()}_{args.resample}.parquet"

    path = build_and_save_features(
        symbol=args.symbol,
        output_path=output,
        start_ts=args.start_ts,
        end_ts=args.end_ts,
        resample=args.resample,
        rolling_windows=args.rolling,
        db_path=args.db,
    )
    print(f"✅ Features written to {path}")


if __name__ == "__main__":
    main()
