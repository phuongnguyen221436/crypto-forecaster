# Machine Learning Pipeline Overview

This repository now includes a minimal feature and modeling workflow. The goal is to bootstrap experimentation quickly while keeping the pieces modular.

## 1. Generate Features

```bash
python3 -m processor.build_features BTCUSDT --resample 1min
```

- Reads trades from `storage/trades.db`.
- Produces a Parquet file under `storage/features/` with resampled candles, volume metrics, and rolling statistics.
- Adjust the window by passing `--start-ts` / `--end-ts` in epoch milliseconds or a custom `--output` path.

## 2. Train Baseline Model

```bash
python3 -m processor.train_model BTCUSDT --freq 1min --horizon 1 --threshold 0.001
```

- Loads the previously generated feature file.
- Builds a binary label: future return over the next `horizon` steps exceeding `threshold`.
- Fits a logistic-regression classifier and saves artifacts under `storage/models/`:
  - `<symbol>_<freq>_h<horizon>.joblib` containing the model + feature list.
  - Matching `.json` metadata with metrics and training configuration.

## 3. Serve Predictions

`forecast/service.py` instantiates `processor.predictor.PriceDirectionPredictor`. When a trained model exists the service will use it; otherwise it falls back to the simple heuristic (based on trade side / quantity) used previously.

Reload the FastAPI service after deploying a new model so the predictor picks up the latest artifact.

## 4. Next Steps

- Schedule `processor.build_features` to run periodically so the training set grows.
- Add richer features (depth, cross-asset correlations) by extending `processor/features.py`.
- Replace the heuristic fallback in `processor/predictor.py` with real-time feature computation that mirrors the training dataset.
- Add backtests before trading live: simulate the strategy using the stored features + labels and verify risk-adjusted performance.
