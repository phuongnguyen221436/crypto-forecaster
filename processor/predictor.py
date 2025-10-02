"""Runtime predictor utilities for serving model outputs."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

import joblib


class PriceDirectionPredictor:
    """Loads a trained model if available and falls back to heuristics."""

    def __init__(self, model_path: Path | None = None):
        self.model_path = model_path or Path("storage/models/btcusdt_1min_h1.joblib")
        self._model = None
        self._feature_cols: Tuple[str, ...] | None = None
        self._load_model()

    def _load_model(self) -> None:
        if self.model_path.exists():
            bundle = joblib.load(self.model_path)
            self._model = bundle.get("model")
            self._feature_cols = tuple(bundle.get("feature_cols", ()))
        else:
            self._model = None
            self._feature_cols = None

    def predict(self, event: Dict[str, float]) -> Tuple[float, float, str]:
        """Return (prob_up, prob_down, source)."""
        if self._model and self._feature_cols:
            features = [float(event.get(col, 0.0)) for col in self._feature_cols]
            prob = self._model.predict_proba([features])[0]
            return float(prob[1]), float(prob[0]), "model"

        # Fallback heuristic based on order-flow imbalance or trade side
        qty = float(event.get("qty", 0))
        side = event.get("side", "buy")
        ofi = float(event.get("ofi", 0))

        bias = ofi if ofi != 0 else (qty if side == "buy" else -qty)
        prob_up = max(0.0, min(1.0, 0.5 + bias * 0.05))
        prob_down = 1.0 - prob_up
        return prob_up, prob_down, "heuristic"

    def reload(self) -> None:
        self._load_model()
