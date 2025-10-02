"""Feature engineering utilities for trade data."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import duckdb
import pandas as pd

DEFAULT_DB_PATH = Path("storage/trades.db")


def load_trades(
    symbol: str,
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None,
    db_path: Path = DEFAULT_DB_PATH,
) -> pd.DataFrame:
    """Load raw trades from DuckDB into a DataFrame.

    Parameters
    ----------
    symbol : str
        Trading pair symbol, e.g. "BTCUSDT".
    start_ts : Optional[int]
        Inclusive timestamp (ms) lower bound.
    end_ts : Optional[int]
        Inclusive timestamp (ms) upper bound.
    db_path : Path
        Location of the DuckDB file.
    """
    if not db_path.exists():
        raise FileNotFoundError(f"DuckDB database not found at {db_path}")

    params: list[object] = []
    filters = []

    if start_ts is not None:
        filters.append("ts >= ?")
        params.append(start_ts)
    if end_ts is not None:
        filters.append("ts <= ?")
        params.append(end_ts)

    with duckdb.connect(db_path.as_posix(), read_only=True) as con:
        columns = {
            row[1] for row in con.execute("PRAGMA table_info('trades')").fetchall()
        }

        query_filters = filters.copy()
        if "symbol" in columns:
            query_filters.insert(0, "symbol = ?")
            params.insert(0, symbol)

        where_clause = f"WHERE {' AND '.join(query_filters)}" if query_filters else ""
        query = f"SELECT ts, price, qty, side{', symbol' if 'symbol' in columns else ''} FROM trades {where_clause} ORDER BY ts"
        df = con.execute(query, params).fetch_df()

    return df


def compute_window_features(
    trades: pd.DataFrame,
    resample: str = "1min",
    rolling_windows: Iterable[int] = (3, 5, 15),
) -> pd.DataFrame:
    """Aggregate trades into time-based features.

    Returns a DataFrame indexed by timestamp with columns such as
    price_close, volume, trade_count, rolling statistics, and returns.
    """
    if trades.empty:
        return pd.DataFrame()

    df = trades.copy()
    df["timestamp"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df = df.set_index("timestamp")

    price = df["price"].astype(float)
    volume = df["qty"].astype(float)

    agg = pd.DataFrame()
    agg["price_close"] = price.resample(resample).last().ffill()
    agg["price_open"] = price.resample(resample).first().fillna(method="ffill")
    agg["price_high"] = price.resample(resample).max().fillna(method="ffill")
    agg["price_low"] = price.resample(resample).min().fillna(method="ffill")
    agg["volume"] = volume.resample(resample).sum().fillna(0)
    agg["trade_count"] = price.resample(resample).count().fillna(0)

    vwap_num = (price * volume).resample(resample).sum()
    agg["vwap"] = (vwap_num / agg["volume"].replace({0: pd.NA})).fillna(method="ffill").fillna(agg["price_close"])

    agg["return_1"] = agg["price_close"].pct_change().fillna(0)

    for window in rolling_windows:
        col_suffix = f"{window}"
        agg[f"ma_{col_suffix}"] = agg["price_close"].rolling(window=window, min_periods=1).mean()
        agg[f"vol_{col_suffix}"] = agg["return_1"].rolling(window=window, min_periods=1).std().fillna(0)
        agg[f"volumema_{col_suffix}"] = agg["volume"].rolling(window=window, min_periods=1).mean()

    agg = agg.dropna()
    if "symbol" in trades:
        symbol_value = trades["symbol"].iloc[0]
    else:
        symbol_value = trades.attrs.get("symbol", "UNKNOWN")
    agg["symbol"] = symbol_value
    return agg


def save_features(df: pd.DataFrame, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path)
    return output_path


def build_and_save_features(
    symbol: str,
    output_path: Path,
    start_ts: Optional[int] = None,
    end_ts: Optional[int] = None,
    resample: str = "1min",
    rolling_windows: Iterable[int] = (3, 5, 15),
    db_path: Path = DEFAULT_DB_PATH,
) -> Path:
    trades = load_trades(symbol, start_ts=start_ts, end_ts=end_ts, db_path=db_path)
    trades["symbol"] = symbol
    features = compute_window_features(trades, resample=resample, rolling_windows=rolling_windows)
    if features.empty:
        raise ValueError("No features generated; check trade availability or time window")
    return save_features(features, output_path)
