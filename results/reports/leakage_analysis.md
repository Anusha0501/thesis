# Leakage Analysis

## Why perfect metrics occurred

Experiment A is a detection benchmark that intentionally keeps the original feature set. The target `high_grid_stress` is defined from `total_concurrent_load` and `power_level`, while the model inputs include `total_concurrent_load`, `p3_concurrent_load`, `power_level_encoded`, `power_level_kw_min`, and `power_level_kw_max`. These columns make the target rule directly recoverable, so near-perfect or perfect metrics are expected for sufficiently expressive models.

## Why this is not code leakage

This is methodological leakage, not code leakage. The train/test split, cross-validation, and evaluation code do not copy labels into predictions. Instead, the experimental design includes predictors that are part of the target definition. The model is learning the label-construction rule rather than demonstrating out-of-sample forecasting capability from independent predictors.

## Experiment definitions

| Experiment | Purpose | Target | Removed features | Metrics file |
| --- | --- | --- | --- | --- |
| Experiment A: Detection Benchmark | Detects the current interval with the original feature set | `high_grid_stress` | None | `metrics_detection.json` |
| Experiment B: No-Leakage Detection Benchmark | Detects the current interval after removing target-definition variables | `high_grid_stress` | `total_concurrent_load`, `p3_concurrent_load`, `power_level_encoded`, `power_level_kw_min`, `power_level_kw_max` | `metrics_no_leakage.json` |
| Experiment C: One-Interval-Ahead Forecasting | Forecasts the next interval using current-row information | `high_grid_stress_t_plus_1` | None | `metrics_forecasting.json` |

## Metrics comparison

Metrics have not been generated in this checkout because the processed training table and trained artifacts are not present. Run `python -m src.models.train` after building `data/processed/interval_features.csv`; the training code will populate this section from the actual metrics files without fabricating results.

## Interpretation guidance

- Treat Experiment A as a detection benchmark only; it answers whether the engineered current-interval rule can be recovered.
- Use Experiment B to evaluate detection after removing the features that directly encode the target definition.
- Use Experiment C to evaluate one-interval-ahead forecasting with the shifted `high_grid_stress_t_plus_1` target and current-row predictors.
