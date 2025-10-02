import pandas as pd
import pytest

from processor.features import compute_window_features
from processor.train_model import build_targets, train_baseline_classifier


def make_sample_trades():
    base_ts = 1700000000000
    prices = [100, 101, 102, 101.5, 100.5, 99.5, 100.2, 99.8, 100.4, 99.9]
    data = {
        "ts": [base_ts + i * 60_000 for i in range(len(prices))],
        "price": prices,
        "qty": [1 + (i % 3) * 0.1 for i in range(len(prices))],
        "side": ["buy" if i % 2 == 0 else "sell" for i in range(10)],
        "symbol": ["BTCUSDT"] * 10,
    }
    return pd.DataFrame(data)


def test_compute_window_features_returns_expected_columns():
    trades = make_sample_trades()
    features = compute_window_features(trades, resample="1min", rolling_windows=(3,))

    assert not features.empty
    expected_cols = {"price_close", "volume", "trade_count", "vwap", "return_1", "ma_3", "vol_3"}
    assert expected_cols.issubset(features.columns)


def test_train_baseline_classifier_produces_metrics():
    trades = make_sample_trades()
    features = compute_window_features(trades, resample="1min", rolling_windows=(2,))
    df = build_targets(features, horizon=1, threshold=0.0)

    feature_cols = tuple(col for col in df.columns if col not in {"label", "future_return"})
    assert feature_cols, "Expected at least one feature column"

    model, metrics = train_baseline_classifier(df, feature_cols)
    assert hasattr(model, "predict_proba")
    assert "accuracy" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0
