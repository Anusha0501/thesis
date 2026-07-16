"""Robust SHAP artifact generation for trained grid-stress models.

The functions in this module are intentionally defensive: SHAP can fail for
specific model/library combinations (for example LightGBM additivity checks or
native-library crashes). A failure for one model is logged and does not stop the
rest of the explainability pipeline.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.models.train import FEATURES
from src.utils.config import load_config


LOGGER_NAME = "shap_analysis"
EXPERIMENT_NAMES = {"detection", "no_leakage", "forecasting", "forecasting_temporal"}
VOTING_ENSEMBLE_MESSAGE = "SHAP not implemented for Voting Ensemble."


def _configure_logger(log_file: Path) -> logging.Logger:
    """Create a file logger for SHAP failures without duplicating handlers."""

    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    has_log_handler = any(
        isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == log_file
        for handler in logger.handlers
    )
    if not has_log_handler:
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)

    return logger


def _available_feature_columns(df: pd.DataFrame) -> list[str]:
    """Return the training feature columns that are present in the data frame."""

    optional_features = [
        "battery_median_kwh",
        "energy_ratio_median",
        "daily_charging_freq",
        "daily_driving_dist_p50",
        "ecr_month_mean",
    ]
    return [column for column in FEATURES + optional_features if column in df.columns]


def _model_feature_columns(model: Any, df: pd.DataFrame) -> list[str]:
    """Return the feature columns expected by a persisted estimator."""

    feature_names = getattr(model, "feature_names_in_", None)
    if feature_names is None and hasattr(model, "named_steps"):
        feature_names = getattr(model.named_steps.get("model"), "feature_names_in_", None)
    if feature_names is not None:
        return [column for column in feature_names if column in df.columns]
    return _available_feature_columns(df)


def _experiment_from_model_path(model_dir: Path, model_path: Path) -> str:
    """Infer the experiment name from an experiment-specific model path."""

    relative_parent = model_path.parent.relative_to(model_dir)
    if relative_parent.parts and relative_parent.parts[0] in EXPERIMENT_NAMES:
        return relative_parent.parts[0]
    return "detection"


def _is_voting_ensemble(model_name: str, model: Any) -> bool:
    """Return True when the model is a sklearn voting ensemble."""

    estimator = model.named_steps.get("model", model) if hasattr(model, "named_steps") else model
    estimator_type = f"{estimator.__class__.__module__}.{estimator.__class__.__name__}".lower()
    return "voting_ensemble" in model_name.lower() or "votingclassifier" in estimator_type


def _unwrap_estimator_and_data(model: Any, X_sample: pd.DataFrame) -> tuple[Any, pd.DataFrame]:
    """Return the final estimator and data in the representation it receives.

    Trained models are often stored as sklearn pipelines. TreeExplainer should
    explain the tree estimator itself, so preprocessing steps before the final
    ``model`` step are applied to the sample first.
    """

    if not hasattr(model, "named_steps") or "model" not in model.named_steps:
        return model, X_sample

    estimator = model.named_steps["model"]
    preprocessor = model[:-1]
    if len(preprocessor.steps) == 0:
        return estimator, X_sample

    transformed = preprocessor.transform(X_sample)
    return estimator, pd.DataFrame(transformed, columns=X_sample.columns, index=X_sample.index)


def _is_lightgbm_estimator(estimator: Any, model_name: str) -> bool:
    """Detect LightGBM estimators without importing optional dependencies."""

    estimator_type = f"{estimator.__class__.__module__}.{estimator.__class__.__name__}".lower()
    return "lightgbm" in model_name.lower() or "lightgbm" in estimator_type or "lgbm" in estimator_type


def _positive_class_values(values: shap.Explanation) -> np.ndarray:
    """Extract a 2-D SHAP value matrix, preferring the positive class."""

    value_array = np.asarray(values.values)
    if value_array.ndim == 3:
        return value_array[:, :, 1] if value_array.shape[2] > 1 else value_array[:, :, 0]
    return value_array


def _build_tree_explanation(model_name: str, estimator: Any, X_tree: pd.DataFrame, background: pd.DataFrame) -> shap.Explanation:
    """Build a TreeExplainer explanation with crash-prone checks disabled."""

    explainer_kwargs: dict[str, Any] = {}
    if _is_lightgbm_estimator(estimator, model_name):
        explainer_kwargs.update({"data": background, "feature_perturbation": "interventional"})

    explainer = shap.TreeExplainer(estimator, **explainer_kwargs)
    return explainer(X_tree, check_additivity=False)


def _build_fallback_explanation(model: Any, X_sample: pd.DataFrame) -> shap.Explanation:
    """Build a model-agnostic SHAP explanation from the model prediction API."""

    def predict_positive_class(data: Any) -> np.ndarray:
        frame = pd.DataFrame(data, columns=X_sample.columns)
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(frame)
            return probabilities[:, 1] if probabilities.ndim == 2 and probabilities.shape[1] > 1 else probabilities.ravel()
        return np.asarray(model.predict(frame)).ravel()

    explainer = shap.Explainer(predict_positive_class, X_sample)
    return explainer(X_sample)


def _save_shap_artifacts(model_name: str, values: shap.Explanation, X_plot: pd.DataFrame, out_dir: Path, max_display: int) -> None:
    """Persist SHAP plots and mean-absolute feature importances."""

    out_dir.mkdir(parents=True, exist_ok=True)
    shap_values = _positive_class_values(values)

    shap.summary_plot(shap_values, X_plot, plot_type="dot", max_display=max_display, show=False)
    plt.savefig(out_dir / f"{model_name}_summary.png", dpi=200, bbox_inches="tight")
    plt.close()

    shap.summary_plot(shap_values, X_plot, plot_type="bar", max_display=max_display, show=False)
    plt.savefig(out_dir / f"{model_name}_bar.png", dpi=200, bbox_inches="tight")
    plt.close()

    importance = pd.DataFrame(
        {
            "feature": X_plot.columns,
            "mean_abs_shap": np.abs(shap_values).mean(axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False)
    importance.to_csv(out_dir / f"{model_name}_feature_importance.csv", index=False)

    dependence_dir = out_dir / "dependence"
    dependence_dir.mkdir(parents=True, exist_ok=True)
    for feature in importance.head(max_display)["feature"]:
        shap.dependence_plot(feature, shap_values, X_plot, show=False)
        plt.savefig(dependence_dir / f"{model_name}_{feature}_dependence.png", dpi=200, bbox_inches="tight")
        plt.close()


def generate_shap_artifacts(
    model_name: str = "random_forest",
    config_path: str = "configs/config.yaml",
    model_path: Path | None = None,
    experiment: str = "detection",
) -> dict[str, str]:
    """Generate SHAP artifacts for one model, logging failures instead of raising."""

    cfg = load_config(config_path)
    shap_root = Path(cfg["paths"]["figures"]) / "shap"
    out_dir = shap_root / experiment
    logger = _configure_logger(shap_root / "shap_errors.log")
    resolved_model_path = model_path or Path(cfg["paths"]["models"]) / f"{model_name}.joblib"

    try:
        model = joblib.load(resolved_model_path)
        if _is_voting_ensemble(model_name, model):
            logger.info("%s %s/%s", VOTING_ENSEMBLE_MESSAGE, experiment, model_name)
            return {
                "experiment": experiment,
                "model": model_name,
                "status": "skipped",
                "message": VOTING_ENSEMBLE_MESSAGE,
            }

        df = pd.read_csv(Path(cfg["paths"]["processed_data"]) / "interval_features.csv")
        feature_cols = _model_feature_columns(model, df)
        if not feature_cols:
            message = "No matching feature columns were found for the saved model."
            logger.error("%s %s/%s", message, experiment, model_name)
            return {
                "experiment": experiment,
                "model": model_name,
                "status": "failed",
                "message": message,
            }

        X = df[feature_cols].fillna(0)
        X_sample = X.sample(
            min(cfg["shap"]["n_samples_explanation"], len(X)),
            random_state=cfg["project"]["random_seed"],
        )
        background = X.sample(
            min(cfg["shap"].get("n_samples_background", 100), len(X)),
            random_state=cfg["project"]["random_seed"],
        )

        estimator, X_tree = _unwrap_estimator_and_data(model, X_sample)
        _, background_tree = _unwrap_estimator_and_data(model, background)

        try:
            values = _build_tree_explanation(model_name, estimator, X_tree, background_tree)
            X_plot = X_tree
        except Exception:
            logger.exception(
                "TreeExplainer failed for %s/%s; falling back to shap.Explainer(model.predict, X_sample).",
                experiment,
                model_name,
            )
            values = _build_fallback_explanation(model, X_sample)
            X_plot = X_sample

        _save_shap_artifacts(model_name, values, X_plot, out_dir, cfg["shap"].get("max_display", 20))
        return {
            "experiment": experiment,
            "model": model_name,
            "status": "generated",
            "message": "Artifacts generated.",
        }
    except Exception as exc:
        logger.exception("SHAP artifact generation failed for %s/%s.", experiment, model_name)
        return {
            "experiment": experiment,
            "model": model_name,
            "status": "failed",
            "message": str(exc),
        }


def _write_shap_generation_report(cfg: dict[str, Any], rows: list[dict[str, str]]) -> None:
    """Write a report from actual SHAP generation attempts."""

    reports_dir = Path(cfg["paths"].get("reports", "results/reports"))
    reports_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SHAP Generation Report",
        "",
        "This report is generated from actual SHAP generation attempts. It does not claim that artifacts exist unless the run reported them as generated.",
        "",
        "| Experiment | Model | Status | Message |",
        "| --- | --- | --- | --- |",
    ]
    if rows:
        for row in rows:
            lines.append(
                f"| {row['experiment']} | {row['model']} | {row['status']} | "
                f"{row['message'].replace('|', '/')} |"
            )
    else:
        lines.append("| n/a | n/a | not_run | No saved model artifacts were found. |")
    (reports_dir / "shap_generation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate_all_shap_artifacts(config_path: str = "configs/config.yaml") -> None:
    """Generate SHAP artifacts for every saved model and continue on failures."""

    cfg = load_config(config_path)
    model_dir = Path(cfg["paths"]["models"])
    results: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for model_path in sorted(model_dir.rglob("*.joblib")):
        experiment = _experiment_from_model_path(model_dir, model_path)
        model_name = model_path.stem
        key = (experiment, model_name)
        if key in seen:
            continue
        seen.add(key)
        results.append(generate_shap_artifacts(model_name, config_path, model_path, experiment))

    _write_shap_generation_report(cfg, results)


if __name__ == "__main__":
    generate_all_shap_artifacts()
