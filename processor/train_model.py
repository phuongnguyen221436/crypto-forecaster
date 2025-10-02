"""Baseline training script for price direction prediction."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split


FEATURE_DIR = Path("storage/features")
MODEL_DIR = Path("storage/models")


def load_features(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Feature file not found: {path}")
    return pd.read_parquet(path)


def build_targets(features: pd.DataFrame, horizon: int, threshold: float) -> pd.DataFrame:
    df = features.copy()
    df = df.sort_index()
    future_price = df["price_close"].shift(-horizon)
    df["future_return"] = (future_price - df["price_close"]) / df["price_close"]
    df["label"] = (df["future_return"] >= threshold).astype(int)
    df = df.dropna(subset=["future_return", "label"])
    return df


def split_dataset(df: pd.DataFrame, feature_cols: Tuple[str, ...]) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    X = df.loc[:, feature_cols].to_numpy()
    y = df["label"].to_numpy()
    return train_test_split(X, y, test_size=0.2, shuffle=False)


def train_baseline_classifier(
    df: pd.DataFrame,
    feature_cols: Tuple[str, ...],
    C: float = 1.0,
) -> Tuple[LogisticRegression, Dict[str, float]]:
    X_train, X_test, y_train, y_test = split_dataset(df, feature_cols)

    model = LogisticRegression(max_iter=500, C=C)
    model.fit(X_train, y_train)

    y_prob = model.predict_proba(X_test)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    metrics = {
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "accuracy": float((y_pred == y_test).mean()),
    }
    report = classification_report(y_test, y_pred, output_dict=True)
    if "1" in report:
        metrics["precision"] = float(report["1"].get("precision", 0.0))
        metrics["recall"] = float(report["1"].get("recall", 0.0))
        metrics["f1"] = float(report["1"].get("f1-score", 0.0))
    return model, metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train baseline price direction classifier")
    parser.add_argument("symbol", help="Trading pair symbol, e.g. BTCUSDT")
    parser.add_argument("--features", type=Path, help="Feature parquet path")
    parser.add_argument("--freq", default="1min", help="Feature frequency label")
    parser.add_argument("--horizon", type=int, default=1, help="Prediction horizon (steps)")
    parser.add_argument(
        "--threshold", type=float, default=0.001, help="Return threshold to label a trade as buy"
    )
    parser.add_argument(
        "--features-dir",
        type=Path,
        default=FEATURE_DIR,
        help="Directory to search for features when --features omitted",
    )
    parser.add_argument(
        "--model-dir",
        type=Path,
        default=MODEL_DIR,
        help="Directory to store trained models",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    feature_path = args.features
    if feature_path is None:
        feature_path = args.features_dir / f"{args.symbol.lower()}_{args.freq}.parquet"

    features = load_features(feature_path)

    dataset = build_targets(features, horizon=args.horizon, threshold=args.threshold)
    feature_cols = tuple(
        col
        for col in dataset.columns
        if col not in {"label", "future_return"}
        and pd.api.types.is_numeric_dtype(dataset[col])
    )

    model, metrics = train_baseline_classifier(dataset, feature_cols)

    args.model_dir.mkdir(parents=True, exist_ok=True)
    model_path = args.model_dir / f"{args.symbol.lower()}_{args.freq}_h{args.horizon}.joblib"
    meta_path = model_path.with_suffix(".json")

    joblib.dump({"model": model, "feature_cols": feature_cols}, model_path)

    meta = {
        "symbol": args.symbol,
        "feature_path": feature_path.as_posix(),
        "feature_cols": feature_cols,
        "horizon": args.horizon,
        "threshold": args.threshold,
        "metrics": metrics,
    }

    meta_path.write_text(json.dumps(meta, indent=2))
    print(f"✅ Model saved to {model_path}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
