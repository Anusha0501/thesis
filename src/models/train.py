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
from sklearn.model_selection import RandomizedSearchCV, StratifiedKFold, TimeSeriesSplit, cross_validate, train_test_split
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

OPTIONAL_FEATURES = [
    "battery_median_kwh",
    "energy_ratio_median",
    "daily_charging_freq",
    "daily_driving_dist_p50",
    "ecr_month_mean",
]

LEAKAGE_PRONE_FEATURES = [
    "total_concurrent_load",
    "p3_concurrent_load",
    "power_level_encoded",
    "power_level_kw_min",
    "power_level_kw_max",
]

EXPERIMENTS = {
    "detection": {
        "label": "Experiment A: Detection Benchmark",
        "target": "high_grid_stress",
        "metrics_file": "metrics_detection.json",
        "predictions_file": "test_predictions_detection.csv",
        "remove_features": [],
        "forecasting": False,
        "temporal_validation": False,
    },
    "no_leakage": {
        "label": "Experiment B: No-Leakage Detection Benchmark",
        "target": "high_grid_stress",
        "metrics_file": "metrics_no_leakage.json",
        "predictions_file": "test_predictions_no_leakage.csv",
        "remove_features": LEAKAGE_PRONE_FEATURES,
        "forecasting": False,
        "temporal_validation": False,
    },
    "forecasting": {
        "label": "Experiment C: One-Interval-Ahead Forecasting",
        "target": "high_grid_stress_t_plus_1",
        "metrics_file": "metrics_forecasting.json",
        "predictions_file": "test_predictions_forecasting.csv",
        "remove_features": [],
        "forecasting": True,
        "temporal_validation": False,
    },
    "forecasting_temporal": {
        "label": "Experiment D: Temporal Forecasting Validation",
        "target": "high_grid_stress_t_plus_1",
        "metrics_file": "metrics_forecasting_temporal.json",
        "predictions_file": "test_predictions_forecasting_temporal.csv",
        "remove_features": [],
        "forecasting": True,
        "temporal_validation": True,
    },
}


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


def _json_safe(value: Any) -> Any:
    """Convert numpy scalars and non-finite floats into JSON-safe values."""

    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.generic):
        return _json_safe(value.item())
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _cv_scores_to_dict(cv_scores: dict[str, np.ndarray]) -> dict[str, list[Any]]:
    """Keep only test scores and make them JSON-safe."""

    return {
        key: _json_safe(list(values))
        for key, values in cv_scores.items()
        if key.startswith("test_")
    }


def _feature_columns(df: pd.DataFrame, remove_features: list[str] | None = None) -> list[str]:
    excluded = set(remove_features or [])
    return [column for column in FEATURES + OPTIONAL_FEATURES if column in df.columns and column not in excluded]


def _add_forecasting_target(df: pd.DataFrame) -> pd.DataFrame:
    """Add the next-interval target without moving future features into the row."""

    sort_columns = [
        column
        for column in ["series", "day_type", "vehicle_type", "power_level", "minute_of_day"]
        if column in df.columns
    ]
    work = df.sort_values(sort_columns).copy() if sort_columns else df.copy()
    group_columns = [
        column
        for column in ["series", "day_type", "vehicle_type", "power_level"]
        if column in work.columns
    ]
    if group_columns:
        shifted = work.groupby(group_columns, dropna=False)["high_grid_stress"].shift(-1)
    else:
        shifted = work["high_grid_stress"].shift(-1)
    work["high_grid_stress_t_plus_1"] = shifted
    return work.dropna(subset=["high_grid_stress_t_plus_1"]).copy()


def _chronologically_order_forecasting_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Order rows by observable interval position for temporal validation."""

    sort_columns = [
        column
        for column in ["minute_of_day", "day_type", "series", "vehicle_type", "power_level"]
        if column in df.columns
    ]
    return df.sort_values(sort_columns).copy() if sort_columns else df.copy()


def _model_pipeline(name: str, model: Any) -> Pipeline:
    if name == "random_forest":
        return Pipeline([("model", model)])
    return Pipeline([("scale", StandardScaler()), ("model", model)])


def _train_single_experiment(
    cfg: dict[str, Any],
    df: pd.DataFrame,
    experiment_name: str,
    experiment: dict[str, Any],
) -> dict[str, Any]:
    if experiment["forecasting"]:
        df = _add_forecasting_target(df)

    feature_cols = _feature_columns(df, experiment["remove_features"])
    X = df[feature_cols].fillna(0)
    y = df[experiment["target"]].astype(int)
    stratify = y if cfg["training"].get("stratify", True) and y.nunique() > 1 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=cfg["training"]["test_size"],
        random_state=cfg["project"]["random_seed"],
        stratify=stratify,
    )

    metrics: dict[str, Any] = {
        "experiment": experiment["label"],
        "target": experiment["target"],
        "features": feature_cols,
        "removed_features": experiment["remove_features"],
        "n_rows": int(len(df)),
        "positive_rate": float(y.mean()),
        "models": {},
    }
    predictions = pd.DataFrame({"y_true": y_test.to_numpy()}, index=y_test.index)
    model_dir = Path(cfg["paths"]["models"]) / experiment_name
    model_dir.mkdir(parents=True, exist_ok=True)
    result_dir = Path(cfg["paths"]["results"])
    result_dir.mkdir(parents=True, exist_ok=True)
    cv = StratifiedKFold(n_splits=cfg["training"]["cv_folds"], shuffle=True, random_state=cfg["project"]["random_seed"])

    for name, model in available_models(cfg).items():
        pipe = _model_pipeline(name, model)
        cv_scores = cross_validate(
            pipe,
            X_train,
            y_train,
            cv=cv,
            scoring=["roc_auc", "average_precision", "f1"],
            error_score="raise",
        )
        pipe.fit(X_train, y_train)
        prob = pipe.predict_proba(X_test)[:, 1]
        model_metrics = evaluate_predictions(y_test.to_numpy(), prob, cfg["evaluation"]["threshold"])
        model_metrics["cv"] = _cv_scores_to_dict(cv_scores)
        metrics["models"][name] = model_metrics
        predictions[f"{name}_prob"] = prob
        joblib.dump(pipe, model_dir / f"{name}.joblib")
        if experiment_name == "detection":
            joblib.dump(pipe, Path(cfg["paths"]["models"]) / f"{name}.joblib")

    predictions.to_csv(result_dir / experiment["predictions_file"], index=True)
    (result_dir / experiment["metrics_file"]).write_text(json.dumps(_json_safe(metrics), indent=2), encoding="utf-8")
    if experiment_name == "detection":
        predictions.to_csv(result_dir / "test_predictions.csv", index=True)
        (result_dir / "metrics.json").write_text(json.dumps(_json_safe(metrics["models"]), indent=2), encoding="utf-8")
    return metrics


def _train_temporal_forecasting_experiment(
    cfg: dict[str, Any],
    df: pd.DataFrame,
    experiment_name: str,
    experiment: dict[str, Any],
) -> dict[str, Any]:
    """Train one-interval-ahead forecasting models with chronological validation."""

    df = _chronologically_order_forecasting_rows(_add_forecasting_target(df))
    feature_cols = _feature_columns(df, experiment["remove_features"])
    X = df[feature_cols].fillna(0)
    y = df[experiment["target"]].astype(int)

    split_index = int(len(df) * 0.8)
    if split_index <= 0 or split_index >= len(df):
        raise ValueError("Temporal forecasting validation requires enough rows for an 80/20 split.")

    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
    result_dir = Path(cfg["paths"]["results"])
    result_dir.mkdir(parents=True, exist_ok=True)
    model_dir = Path(cfg["paths"]["models"]) / experiment_name
    model_dir.mkdir(parents=True, exist_ok=True)

    metrics: dict[str, Any] = {
        "experiment": experiment["label"],
        "target": experiment["target"],
        "features": feature_cols,
        "removed_features": experiment["remove_features"],
        "n_rows": int(len(df)),
        "positive_rate": float(y.mean()),
        "split": {
            "method": "chronological_80_20",
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
            "train_fraction": 0.8,
            "test_fraction": 0.2,
        },
        "time_series_cv": {"n_splits": 5},
        "models": {},
    }
    predictions = pd.DataFrame({"y_true": y_test.to_numpy()}, index=y_test.index)
    cv = TimeSeriesSplit(n_splits=5)

    for name, model in available_models(cfg).items():
        pipe = _model_pipeline(name, model)
        cv_scores = cross_validate(
            pipe,
            X_train,
            y_train,
            cv=cv,
            scoring=["roc_auc", "average_precision", "f1"],
            error_score=np.nan,
        )
        pipe.fit(X_train, y_train)
        prob = pipe.predict_proba(X_test)[:, 1]
        model_metrics = evaluate_predictions(y_test.to_numpy(), prob, cfg["evaluation"]["threshold"])
        model_metrics["cv"] = _cv_scores_to_dict(cv_scores)
        metrics["models"][name] = model_metrics
        predictions[f"{name}_prob"] = prob
        joblib.dump(pipe, model_dir / f"{name}.joblib")

    predictions.to_csv(result_dir / experiment["predictions_file"], index=True)
    (result_dir / experiment["metrics_file"]).write_text(json.dumps(_json_safe(metrics), indent=2), encoding="utf-8")
    return metrics


def _format_metric(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{float(value):.4f}"


def write_leakage_analysis_report(
    cfg: dict[str, Any],
    all_metrics: dict[str, dict[str, Any]] | None = None,
) -> None:
    """Write a leakage analysis report using only metrics that were actually produced."""

    results_dir = Path(cfg["paths"]["results"])
    reports_dir = Path(cfg["paths"].get("reports", "results/reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)

    metrics_by_name = all_metrics or {}
    for experiment_name, experiment in EXPERIMENTS.items():
        metrics_path = results_dir / experiment["metrics_file"]
        if experiment_name not in metrics_by_name and metrics_path.exists():
            metrics_by_name[experiment_name] = json.loads(metrics_path.read_text(encoding="utf-8"))

    lines = [
        "# Leakage Analysis",
        "",
        "## Why perfect metrics occurred",
        "",
        "Experiment A is a detection benchmark that intentionally uses the original feature set. The target `high_grid_stress` is defined from `total_concurrent_load` and `power_level`, while the model inputs include `total_concurrent_load`, `p3_concurrent_load`, `power_level_encoded`, `power_level_kw_min`, and `power_level_kw_max`. These columns make the target rule directly recoverable, so near-perfect or perfect metrics are expected for sufficiently expressive models.",
        "",
        "## Why this is not code leakage",
        "",
        "This is methodological leakage, not code leakage. The train/test split, cross-validation, and evaluation code do not copy labels into predictions. Instead, the experimental design includes predictors that are part of the target definition. The model is learning the label-construction rule rather than demonstrating out-of-sample forecasting capability from independent predictors.",
        "",
        "## Experiment definitions",
        "",
        "| Experiment | Purpose | Target | Removed features | Metrics file |",
        "| --- | --- | --- | --- | --- |",
    ]
    for experiment in EXPERIMENTS.values():
        removed = ", ".join(experiment["remove_features"]) if experiment["remove_features"] else "None"
        purpose = "Forecasts the next interval" if experiment["forecasting"] else "Detects the current interval"
        lines.append(
            f"| {experiment['label']} | {purpose} | `{experiment['target']}` | "
            f"{removed} | `{experiment['metrics_file']}` |"
        )

    lines.extend(["", "## Metrics comparison", ""])
    if metrics_by_name:
        lines.extend([
            "| Experiment | Model | Accuracy | Precision | Recall | F1 | ROC AUC | Average precision |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for experiment_name, metrics in metrics_by_name.items():
            for model_name, model_metrics in metrics.get("models", {}).items():
                lines.append(
                    f"| {metrics.get('experiment', experiment_name)} | {model_name} | "
                    f"{_format_metric(model_metrics.get('accuracy'))} | "
                    f"{_format_metric(model_metrics.get('precision'))} | "
                    f"{_format_metric(model_metrics.get('recall'))} | "
                    f"{_format_metric(model_metrics.get('f1'))} | "
                    f"{_format_metric(model_metrics.get('roc_auc'))} | "
                    f"{_format_metric(model_metrics.get('average_precision'))} |"
                )
    else:
        lines.append(
            "Metrics have not been generated yet. Run `python -m src.models.train` to train "
            "the experiments and populate the comparison table without fabricating results."
        )

    lines.extend([
        "",
        "## Interpretation guidance",
        "",
        "- Treat Experiment A as a detection benchmark only; it answers whether the engineered current-interval rule can be recovered.",
        "- Use Experiment B to evaluate detection after removing the features that directly encode the target definition.",
        "- Use Experiment C to evaluate one-interval-ahead forecasting with the shifted `high_grid_stress_t_plus_1` target and current-row predictors.",
        "- Use Experiment D to evaluate whether one-interval-ahead forecasting remains reliable under chronological validation.",
    ])
    (reports_dir / "leakage_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _best_model_rows(metrics: dict[str, Any] | None) -> list[str]:
    """Return compact metric rows for a report table."""

    if not metrics:
        return []
    rows = []
    for model_name, model_metrics in metrics.get("models", {}).items():
        rows.append(
            f"| {metrics.get('experiment', 'unknown')} | {model_name} | "
            f"{_format_metric(model_metrics.get('accuracy'))} | "
            f"{_format_metric(model_metrics.get('precision'))} | "
            f"{_format_metric(model_metrics.get('recall'))} | "
            f"{_format_metric(model_metrics.get('f1'))} | "
            f"{_format_metric(model_metrics.get('roc_auc'))} | "
            f"{_format_metric(model_metrics.get('average_precision'))} |"
        )
    return rows


def write_forecasting_temporal_validation_report(
    cfg: dict[str, Any],
    temporal_metrics: dict[str, Any] | None = None,
    random_split_metrics: dict[str, Any] | None = None,
) -> None:
    """Write the Experiment D report without inventing missing metrics."""

    results_dir = Path(cfg["paths"]["results"])
    reports_dir = Path(cfg["paths"].get("reports", "results/reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)

    if temporal_metrics is None:
        temporal_path = results_dir / "metrics_forecasting_temporal.json"
        if temporal_path.exists():
            temporal_metrics = json.loads(temporal_path.read_text(encoding="utf-8"))
    if random_split_metrics is None:
        random_path = results_dir / "metrics_forecasting.json"
        if random_path.exists():
            random_split_metrics = json.loads(random_path.read_text(encoding="utf-8"))

    lines = [
        "# Forecasting Temporal Validation",
        "",
        "## Methodology",
        "",
        "Experiment D reuses the one-interval-ahead forecasting dataset from Experiment C by creating `high_grid_stress_t_plus_1` from the current target shifted one interval forward. Models are evaluated with a chronological holdout: the first 80% of observations are used for training and the final 20% are reserved for testing. The experiment also computes `TimeSeriesSplit(n_splits=5)` cross-validation scores on the training window.",
        "",
        "## Comparison against random split forecasting",
        "",
    ]

    comparison_rows = _best_model_rows(random_split_metrics) + _best_model_rows(temporal_metrics)
    if comparison_rows:
        lines.extend([
            "| Experiment | Model | Accuracy | Precision | Recall | F1 | ROC AUC | Average precision |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
            *comparison_rows,
        ])
    else:
        lines.append(
            "Forecasting metrics have not been generated yet. Run `python -m src.models.train` "
            "to populate this comparison from actual `metrics_forecasting.json` and "
            "`metrics_forecasting_temporal.json` files."
        )

    lines.extend([
        "",
        "## Temporal leakage risk",
        "",
        "Random train/test splits can mix later observations into training folds while testing on earlier observations. For forecasting, this can overstate deployable performance if temporal ordering matters or if aggregate patterns drift over time. The chronological split is stricter because the test window occurs after all training rows.",
        "",
        "## Implications for real-world deployment",
        "",
        "Use Experiment D as the deployment-oriented forecasting validation. If temporal performance is materially lower than random-split forecasting, report the temporal result as the primary estimate and treat the random-split result as an optimistic diagnostic rather than a deployment metric.",
    ])
    (reports_dir / "forecasting_temporal_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def train_models(config_path: str = "configs/config.yaml", experiments: list[str] | None = None) -> None:
    cfg = load_config(config_path)
    df = pd.read_csv(Path(cfg["paths"]["processed_data"]) / "interval_features.csv")
    selected = experiments or list(EXPERIMENTS)
    metrics: dict[str, dict[str, Any]] = {}
    for experiment_name in selected:
        experiment = EXPERIMENTS[experiment_name]
        if experiment.get("temporal_validation", False):
            metrics[experiment_name] = _train_temporal_forecasting_experiment(cfg, df, experiment_name, experiment)
        else:
            metrics[experiment_name] = _train_single_experiment(cfg, df, experiment_name, experiment)
    write_leakage_analysis_report(cfg, metrics)
    write_forecasting_temporal_validation_report(cfg, metrics.get("forecasting_temporal"), metrics.get("forecasting"))


def randomized_search_example(config_path: str = "configs/config.yaml") -> None:
    """Run a minimal RandomizedSearchCV for Random Forest and save the estimator."""


    cfg = load_config(config_path)
    df = pd.read_csv(Path(cfg["paths"]["processed_data"]) / "interval_features.csv")
    feature_cols = _feature_columns(df)
    X, y = df[feature_cols].fillna(0), df["high_grid_stress"].astype(int)
    search = RandomizedSearchCV(
        RandomForestClassifier(class_weight="balanced", random_state=42),
        {"n_estimators": [100, 300], "max_depth": [8, 15, None]},
        n_iter=3,
        scoring="roc_auc",
        cv=3,
        random_state=42,
    )
    search.fit(X, y)
    joblib.dump(search.best_estimator_, Path(cfg["paths"]["models"]) / "random_forest_randomized_search.joblib")


if __name__ == "__main__":
    train_models()
