# Forecasting Temporal Validation

## Methodology

Experiment D reuses the one-interval-ahead forecasting dataset from Experiment C by creating `high_grid_stress_t_plus_1` from the current target shifted one interval forward. Models are evaluated with a chronological holdout: the first 80% of observations are used for training and the final 20% are reserved for testing. The experiment also computes `TimeSeriesSplit(n_splits=5)` cross-validation scores on the training window.

## Comparison against random split forecasting

Forecasting metrics have not been generated in this checkout because the processed training table and trained artifacts are not present. Run `python -m src.models.train` after building `data/processed/interval_features.csv`; the training code will populate this section from actual `metrics_forecasting.json` and `metrics_forecasting_temporal.json` files without fabricating results.

## Temporal leakage risk

Random train/test splits can mix later observations into training folds while testing on earlier observations. For forecasting, this can overstate deployable performance if temporal ordering matters or if aggregate patterns drift over time. The chronological split is stricter because the test window occurs after all training rows.

## Implications for real-world deployment

Use Experiment D as the deployment-oriented forecasting validation. If temporal performance is materially lower than random-split forecasting, report the temporal result as the primary estimate and treat the random-split result as an optimistic diagnostic rather than a deployment metric.
