"""Model training utilities for grid-stress classification."""
from __future__ import annotations

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score, accuracy_score, confusion_matrix
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

try:
    from xgboost import XGBClassifier
except ImportError:  # optional dependency
    XGBClassifier = None
try:
    from lightgbm import LGBMClassifier
except ImportError:  # optional dependency
    LGBMClassifier = None

from src.utils.config import load_config

FEATURES = [
    "hour_of_day", "minute_of_day", "hour_sin", "hour_cos", "is_peak_morning", "is_peak_evening",
    "is_daytime", "is_night", "power_level_encoded", "power_level_kw_min", "power_level_kw_max",
    "vehicle_count", "charging_load_kw", "vehicle_type_encoded", "is_service_vehicle", "total_concurrent_load",
    "p3_concurrent_load", "load_share", "is_workday",
]


def available_models(cfg: dict[str, Any]) -> dict[str, Any]:
    models = {"random_forest": RandomForestClassifier(**cfg["models"]["random_forest"])}
    if XGBClassifier:
        params = {k: v for k, v in cfg["models"]["xgboost"].items() if v != "auto"}
        models["xgboost"] = XGBClassifier(**params)
    if LGBMClassifier:
        models["lightgbm"] = LGBMClassifier(**cfg["models"]["lightgbm"])
    if len(models) >= 2:
        models["voting_ensemble"] = VotingClassifier(estimators=list(models.items()), voting="soft")
    return models


def evaluate_predictions(y_true: np.ndarray, prob: np.ndarray, threshold: float = 0.5) -> dict[str, Any]:
    pred = (prob >= threshold).astype(int)
    return {
        "accuracy": accuracy_score(y_true, pred),
        "precision": precision_score(y_true, pred, zero_division=0),
        "recall": recall_score(y_true, pred, zero_division=0),
        "f1": f1_score(y_true, pred, zero_division=0),
        "roc_auc": roc_auc_score(y_true, prob) if len(np.unique(y_true)) > 1 else None,
        "average_precision": average_precision_score(y_true, prob) if len(np.unique(y_true)) > 1 else None,
        "confusion_matrix": confusion_matrix(y_true, pred).tolist(),
    }


def train_models(config_path: str = "configs/config.yaml") -> None:
    cfg = load_config(config_path)
    df = pd.read_csv(Path(cfg["paths"]["processed_data"]) / "interval_features.csv")
    feature_cols = [c for c in FEATURES + ["battery_median_kwh", "energy_ratio_median", "daily_charging_freq", "daily_driving_dist_p50", "ecr_month_mean"] if c in df.columns]
    X = df[feature_cols].fillna(0)
    y = df["high_grid_stress"].astype(int)
    stratify = y if cfg["training"].get("stratify", True) and y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=cfg["training"]["test_size"], random_state=cfg["project"]["random_seed"], stratify=stratify)
    metrics = {}
    predictions = pd.DataFrame({"y_true": y_test.to_numpy()}, index=y_test.index)
    model_dir = Path(cfg["paths"]["models"]); model_dir.mkdir(parents=True, exist_ok=True)
    result_dir = Path(cfg["paths"]["results"]); result_dir.mkdir(parents=True, exist_ok=True)
    cv = StratifiedKFold(n_splits=cfg["training"]["cv_folds"], shuffle=True, random_state=cfg["project"]["random_seed"])
    for name, model in available_models(cfg).items():
        pipe = Pipeline([("scale", StandardScaler()), ("model", model)]) if name != "random_forest" else Pipeline([("model", model)])
        cv_scores = cross_validate(pipe, X_train, y_train, cv=cv, scoring=["roc_auc", "average_precision", "f1"], error_score="raise")
        pipe.fit(X_train, y_train)
        prob = pipe.predict_proba(X_test)[:, 1]
        metrics[name] = evaluate_predictions(y_test.to_numpy(), prob, cfg["evaluation"]["threshold"])
        metrics[name]["cv"] = {k: list(map(float, v)) for k, v in cv_scores.items() if k.startswith("test_")}
        predictions[f"{name}_prob"] = prob
        joblib.dump(pipe, model_dir / f"{name}.joblib")
    predictions.to_csv(result_dir / "test_predictions.csv", index=True)
    (result_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")


def randomized_search_example(config_path: str = "configs/config.yaml") -> None:
    """Run a minimal RandomizedSearchCV for Random Forest and save the estimator."""


    cfg = load_config(config_path)
    df = pd.read_csv(Path(cfg["paths"]["processed_data"]) / "interval_features.csv")
    feature_cols = [c for c in FEATURES + ["battery_median_kwh", "energy_ratio_median", "daily_charging_freq", "daily_driving_dist_p50", "ecr_month_mean"] if c in df.columns]
    X, y = df[feature_cols].fillna(0), df["high_grid_stress"].astype(int)
    search = RandomizedSearchCV(RandomForestClassifier(class_weight="balanced", random_state=42), {"n_estimators": [100, 300], "max_depth": [8, 15, None]}, n_iter=3, scoring="roc_auc", cv=3, random_state=42)
    search.fit(X, y)
    joblib.dump(search.best_estimator_, Path(cfg["paths"]["models"]) / "random_forest_randomized_search.joblib")


if __name__ == "__main__":
    train_models()
