# Leakage Analysis

## Why perfect metrics occurred

Experiment A is a detection benchmark that intentionally uses the original feature set. The target `high_grid_stress` is defined from `total_concurrent_load` and `power_level`, while the model inputs include `total_concurrent_load`, `p3_concurrent_load`, `power_level_encoded`, `power_level_kw_min`, and `power_level_kw_max`. These columns make the target rule directly recoverable, so near-perfect or perfect metrics are expected for sufficiently expressive models.

## Why this is not code leakage

This is methodological leakage, not code leakage. The train/test split, cross-validation, and evaluation code do not copy labels into predictions. Instead, the experimental design includes predictors that are part of the target definition. The model is learning the label-construction rule rather than demonstrating out-of-sample forecasting capability from independent predictors.

## Experiment definitions

| Experiment | Purpose | Target | Removed features | Metrics file |
| --- | --- | --- | --- | --- |
| Experiment A: Detection Benchmark | Detects the current interval | `high_grid_stress` | None | `metrics_detection.json` |
| Experiment B: No-Leakage Detection Benchmark | Detects the current interval | `high_grid_stress` | total_concurrent_load, p3_concurrent_load, power_level_encoded, power_level_kw_min, power_level_kw_max | `metrics_no_leakage.json` |
| Experiment C: One-Interval-Ahead Forecasting | Forecasts the next interval | `high_grid_stress_t_plus_1` | None | `metrics_forecasting.json` |
| Experiment D: Temporal Forecasting Validation | Forecasts the next interval | `high_grid_stress_t_plus_1` | None | `metrics_forecasting_temporal.json` |

## Metrics comparison

| Experiment | Model | Accuracy | Precision | Recall | F1 | ROC AUC | Average precision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Experiment A: Detection Benchmark | random_forest | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Experiment A: Detection Benchmark | xgboost | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Experiment A: Detection Benchmark | lightgbm | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Experiment A: Detection Benchmark | voting_ensemble | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Experiment B: No-Leakage Detection Benchmark | random_forest | 0.9625 | 0.8386 | 0.9297 | 0.8818 | 0.9880 | 0.9596 |
| Experiment B: No-Leakage Detection Benchmark | xgboost | 0.9678 | 0.9241 | 0.8562 | 0.8889 | 0.9906 | 0.9645 |
| Experiment B: No-Leakage Detection Benchmark | lightgbm | 0.9683 | 0.8687 | 0.9297 | 0.8981 | 0.9895 | 0.9615 |
| Experiment B: No-Leakage Detection Benchmark | voting_ensemble | 0.9692 | 0.8784 | 0.9233 | 0.9003 | 0.9896 | 0.9657 |
| Experiment C: One-Interval-Ahead Forecasting | random_forest | 0.9716 | 0.8684 | 0.9550 | 0.9096 | 0.9971 | 0.9848 |
| Experiment C: One-Interval-Ahead Forecasting | xgboost | 0.9932 | 0.9775 | 0.9775 | 0.9775 | 0.9997 | 0.9982 |
| Experiment C: One-Interval-Ahead Forecasting | lightgbm | 0.9961 | 0.9903 | 0.9839 | 0.9871 | 0.9998 | 0.9991 |
| Experiment C: One-Interval-Ahead Forecasting | voting_ensemble | 0.9937 | 0.9776 | 0.9807 | 0.9791 | 0.9994 | 0.9970 |
| Experiment D: Temporal Forecasting Validation | random_forest | 0.7324 | 0.9787 | 0.1426 | 0.2490 | 0.9528 | 0.8768 |
| Experiment D: Temporal Forecasting Validation | xgboost | 0.8983 | 0.9677 | 0.6961 | 0.8097 | 0.9708 | 0.9447 |
| Experiment D: Temporal Forecasting Validation | lightgbm | 0.9065 | 0.9669 | 0.7240 | 0.8280 | 0.9546 | 0.9277 |
| Experiment D: Temporal Forecasting Validation | voting_ensemble | 0.8973 | 0.9737 | 0.6884 | 0.8065 | 0.9693 | 0.9402 |

## Interpretation guidance

- Treat Experiment A as a detection benchmark only; it answers whether the engineered current-interval rule can be recovered.
- Use Experiment B to evaluate detection after removing the features that directly encode the target definition.
- Use Experiment C to evaluate one-interval-ahead forecasting with the shifted `high_grid_stress_t_plus_1` target and current-row predictors.
- Use Experiment D to evaluate whether one-interval-ahead forecasting remains reliable under chronological validation.
