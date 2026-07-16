# Temporal CV Diagnostics

## Class distribution per fold

Temporal CV diagnostics have not been generated in this checkout because processed interval data is not present. Run `python -m src.models.train` after building `data/processed/interval_features.csv`; the training code will populate this report from actual TimeSeriesSplit folds without fabricating metrics.

## Skipped folds

Pending an actual temporal validation run. Folds with only one target class are recorded as `insufficient_class_variation`; ROC-AUC and Average Precision are skipped for those folds.

## Implications for temporal validation

Temporal folds with only one target class cannot support ROC-AUC or Average Precision because ranking metrics require both positive and negative examples. These folds must be reported as diagnostics rather than assigned fabricated metric values.
