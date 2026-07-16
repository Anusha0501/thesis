# Temporal CV Diagnostics

## Class distribution per fold

| Fold | Train rows | Test rows | Train class distribution | Test class distribution | Status |
| ---: | ---: | ---: | --- | --- | --- |
| 1 | 1384 | 1382 | {'0': 1055, '1': 329} | {'0': 1369, '1': 13} | ok |
| 2 | 2766 | 1382 | {'0': 2424, '1': 342} | {'0': 1342, '1': 40} | ok |
| 3 | 4148 | 1382 | {'0': 3766, '1': 382} | {'0': 882, '1': 500} | ok |
| 4 | 5530 | 1382 | {'0': 4648, '1': 882} | {'0': 1352, '1': 30} | ok |
| 5 | 6912 | 1382 | {'0': 6000, '1': 912} | {'0': 1382} | insufficient_class_variation |

## Skipped folds

- Fold 5: insufficient_class_variation

## Implications for temporal validation

Temporal folds with only one target class cannot support ROC-AUC or Average Precision because ranking metrics require both positive and negative examples. These folds are recorded as `insufficient_class_variation` rather than assigned fabricated metric values.
