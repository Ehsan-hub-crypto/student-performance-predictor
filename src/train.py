"""Train Random Forest + Linear Regression, evaluate on a held-out test set, save the best.

Usage:  python -m src.train
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.config import DATA_PATH, MODEL_PATH, RANDOM_STATE, TEST_PATH, TRAIN_PATH
from src.generate_data import generate
from src.preprocess import FEATURES, TARGET, clean_dataset, load_dataset, split_data


def train(data_path=DATA_PATH, model_path=MODEL_PATH, train_path=TRAIN_PATH, test_path=TEST_PATH) -> dict:
    data_path, model_path = Path(data_path), Path(model_path)
    if not data_path.exists():
        data_path.parent.mkdir(parents=True, exist_ok=True)
        generate().to_csv(data_path, index=False)
        print(f"No dataset found - generated synthetic data at {data_path}")

    df = clean_dataset(load_dataset(data_path))
    train_df, test_df = split_data(df)
    # Keep training and testing data in separate files.
    Path(train_path).parent.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    candidates = {
        "Random Forest": RandomForestRegressor(
            n_estimators=200, max_depth=12, min_samples_leaf=5, random_state=RANDOM_STATE, n_jobs=-1
        ),
        "Linear Regression": LinearRegression(),
    }
    metrics, fitted = {}, {}
    for name, model in candidates.items():
        model.fit(train_df[FEATURES], train_df[TARGET])
        pred = model.predict(test_df[FEATURES])  # test data only used here, for scoring
        metrics[name] = {
            "mae": float(mean_absolute_error(test_df[TARGET], pred)),
            "rmse": float(np.sqrt(mean_squared_error(test_df[TARGET], pred))),
            "r2": float(r2_score(test_df[TARGET], pred)),
        }
        fitted[name] = model

    rf = fitted["Random Forest"]
    bundle = {
        "model": rf,
        "model_name": "Random Forest Regressor",
        "features": FEATURES,
        "metrics": metrics,
        "feature_importances": dict(zip(FEATURES, map(float, rf.feature_importances_))),
        "feature_ranges": {f: (float(train_df[f].min()), float(train_df[f].max())) for f in FEATURES},
        "n_train": len(train_df),
        "n_test": len(test_df),
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_file": data_path.name,
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    bundle["baseline_mae"] = float(np.abs(test_df[TARGET] - train_df[TARGET].mean()).mean())
    card = data_path.with_name("data_card.json")
    if card.exists():
        bundle["data_source"] = json.loads(card.read_text()).get("source", "unknown")
    summary = {k: v for k, v in bundle.items() if k not in ("model", "feature_ranges")}
    joblib.dump(bundle, model_path, compress=3)
    model_path.with_name("metrics.json").write_text(json.dumps(summary, indent=2))
    return bundle


if __name__ == "__main__":
    b = train()
    print(f"Trained on {b['n_train']} rows, tested on {b['n_test']} held-out rows.")
    for name, m in b["metrics"].items():
        print(f"  {name:18s} MAE = {m['mae']:.2f}   R2 = {m['r2']:.3f}")
    print(f"Saved model to {MODEL_PATH}")
