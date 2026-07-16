# Forecasting Temporal Validation

## Methodology

Experiment D reuses the one-interval-ahead forecasting dataset from Experiment C by creating `high_grid_stress_t_plus_1` from the current target shifted one interval forward. Models are evaluated with a chronological holdout: the first 80% of observations are used for training and the final 20% are reserved for testing. The experiment also computes `TimeSeriesSplit(n_splits=5)` cross-validation scores on the training window.

## Comparison against random split forecasting

| Experiment | Model | Accuracy | Precision | Recall | F1 | ROC AUC | Average precision |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Experiment C: One-Interval-Ahead Forecasting | random_forest | 0.9716 | 0.8684 | 0.9550 | 0.9096 | 0.9971 | 0.9848 |
| Experiment C: One-Interval-Ahead Forecasting | xgboost | 0.9932 | 0.9775 | 0.9775 | 0.9775 | 0.9997 | 0.9982 |
| Experiment C: One-Interval-Ahead Forecasting | lightgbm | 0.9961 | 0.9903 | 0.9839 | 0.9871 | 0.9998 | 0.9991 |
| Experiment C: One-Interval-Ahead Forecasting | voting_ensemble | 0.9937 | 0.9776 | 0.9807 | 0.9791 | 0.9994 | 0.9970 |
| Experiment D: Temporal Forecasting Validation | random_forest | 0.7324 | 0.9787 | 0.1426 | 0.2490 | 0.9528 | 0.8768 |
| Experiment D: Temporal Forecasting Validation | xgboost | 0.8983 | 0.9677 | 0.6961 | 0.8097 | 0.9708 | 0.9447 |
| Experiment D: Temporal Forecasting Validation | lightgbm | 0.9065 | 0.9669 | 0.7240 | 0.8280 | 0.9546 | 0.9277 |
| Experiment D: Temporal Forecasting Validation | voting_ensemble | 0.8973 | 0.9737 | 0.6884 | 0.8065 | 0.9693 | 0.9402 |

## Temporal leakage risk

Random train/test splits can mix later observations into training folds while testing on earlier observations. For forecasting, this can overstate deployable performance if temporal ordering matters or if aggregate patterns drift over time. The chronological split is stricter because the test window occurs after all training rows.

## Implications for real-world deployment

Use Experiment D as the deployment-oriented forecasting validation. If temporal performance is materially lower than random-split forecasting, report the temporal result as the primary estimate and treat the random-split result as an optimistic diagnostic rather than a deployment metric.
