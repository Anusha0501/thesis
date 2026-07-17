# Analysis of EV Usage Patterns and Charging Behavior for Smart Energy Management

This thesis analyzes public EV charging data at the charging-interval level to identify high grid-stress periods, evaluate how much standard model selection can overstate performance, and test whether smart-charging policies can reduce peak demand in a physically meaningful way. The underlying data are aggregated 5-minute intervals, so the repository intentionally avoids individual-session claims.

> I built an explainable machine learning framework to identify high grid-stress EV charging intervals and tested whether models that look strong under standard evaluation remain reliable when predicting future unseen intervals.

## At a Glance

| Item | Value |
| --- | --- |
| Unit of analysis | Charging interval |
| Dataset type | Aggregated 5-minute EV charging data |
| Main research concern | Temporal robustness and leakage-aware validation |
| Core supervised tasks | Detection, no-leakage detection, one-step-ahead forecasting, temporal validation |
| Main thesis finding | Random splits can look much stronger than honest chronological validation |
| Best simulation reduction | 7.34% peak reduction with V2G_Peak_Shaving |

## Contents

- [Project Scope](#project-scope)
- [Research Story](#research-story)
- [Thesis Contributions](#thesis-contributions)
- [Repository Layout](#repository-layout)
- [Data Summary](#data-summary)
- [Target Definition](#target-definition)
- [Experiment Summary](#experiment-summary)
- [Setup](#setup)
- [Reproduce](#reproduce)
- [Results Summary](#results-summary)
- [Figures and Artifacts](#figures-and-artifacts)
- [Methodology Notes](#methodology-notes)
- [Limits](#limits)

## Project Scope

The workflow in this repository covers five stages:

1. Audit the source CSVs and document what is available.
2. Build an interval-level modelling table from the aggregated public data.
3. Train explainable ensemble classifiers for high-grid-stress detection and forecasting.
4. Generate evaluation, SHAP, and calibration artifacts.
5. Simulate smart-charging policies against the reconstructed load curves.

## Research Story

The project starts from a practical grid question: EV charging creates demand peaks, and grid operators need to know when those peaks are likely to occur. The initial hypothesis was that explainable ensemble models could identify high-stress charging periods well enough to support adaptive charging control.

The dataset audit changed the shape of the thesis. The Zenodo data are aggregated intervals, not individual sessions, so the correct unit of analysis is a charging interval. That reframing is a strength, not a limitation, because it makes the modelling assumptions explicit and prevents unsupported session-level claims.

The second major insight is methodological: random-split evaluation can make models look much better than they really are for deployment. Under random splits, models can exploit temporal similarity between train and test data, which hides overfitting. Under honest chronological validation, the picture changes materially, especially for Random Forest.

The final step is operational. Rather than stopping at prediction, the thesis tests smart-charging policies and checks whether the simulated load changes are physically plausible, energy-consistent, and able to reduce peak demand.

## Thesis Contributions

- A scientifically justified reframing from session-level claims to interval-level grid-stress prediction.
- A leakage-aware modelling pipeline that separates honest features from target-defining variables.
- A direct comparison between random-split and chronological validation for deployment realism.
- SHAP-based interpretation for tree models to support global and local explanation.
- A validated smart-charging simulation that conserves energy for load-shifting strategies and quantifies peak reduction.
- A reproducible codebase with audit reports, tests, metrics, and saved figures.

## Repository Layout

- `data/raw/zenodo_extracted/`: extracted public CSVs used for auditing and feature construction.
- `data/processed/`: interval-level modelling table.
- `models/saved/`: serialized model artifacts.
- `results/metrics/`: metrics, predictions, simulation outputs, and evaluation manifests.
- `results/reports/`: dataset audit, data dictionary, methodology, feasibility, target definition, validation notes, and templates.
- `figures/`: ROC, PR, calibration, SHAP, and simulation figures.

## Data Summary

The verified data inventory includes aggregated inputs for charging load, vehicle counts, usage patterns, state-of-charge summaries, energy-consumption-rate context, cluster summaries, and vehicle distribution statistics. The most important modelling inputs are the charging-load and vehicle-count curves, which support interval-level feature engineering and target creation.

The repository’s environment verification report also documents missing external documents in this workspace. Those files are not required to interpret the saved metrics and figures already committed here, but they are relevant if you want to fully reproduce the original data-ingestion workflow.

## Target Definition

High grid stress is defined exactly as:

`(total_concurrent_load >= 75th percentile AND power_level == P3) OR (total_concurrent_load >= 90th percentile)`

The saved reports also include sensitivity checks at the 70%, 75%, 80%, 85%, and 90% thresholds.

## Experiment Summary

| Experiment | Purpose | Main result |
| --- | --- | --- |
| Raw detection | Baseline classification with all available features | Apparent perfect performance, but the setup contains leakage because the target uses the same grid-load variables as the features |
| Leakage-free detection | Remove target-defining variables and re-evaluate | Strong but more realistic performance; XGBoost remains the strongest model |
| Random-split forecasting | Predict the next interval under standard split assumptions | Strong scores, especially for boosted trees, but still optimistic for deployment |
| Chronological forecasting | Train on past intervals and test on future intervals | Random Forest drops sharply; boosted trees remain substantially more robust |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Reproduce

Run the stages individually:

```bash
python src/preprocessing/audit_reports.py
python src/features/feature_engineering.py
python src/pipelines/train_pipeline.py
python src/pipelines/evaluation_pipeline.py
python src/pipelines/simulation_pipeline.py
```

Run the full pipeline end to end:

```bash
python src/pipelines/run_all.py
```

## Results Summary

### Detection benchmark

The main detection experiment uses 10,404 interval rows and a positive rate of 15.05%. The held-out test split contains 2,081 rows, and all four models achieve perfect classification on that split.

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC | Avg. Precision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Random Forest | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| XGBoost | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| LightGBM | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Voting Ensemble | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

The confusion matrix for each model is 1,768 true negatives and 313 true positives, with zero false positives and zero false negatives.

### No-leakage benchmark

When leakage-prone interval features are removed, performance remains strong. The best no-leakage model is XGBoost with accuracy 0.9678, precision 0.9241, recall 0.8562, F1 0.8889, and ROC-AUC 0.9906.

### One-interval-ahead forecasting

For the one-step-ahead target, LightGBM is the strongest overall model with accuracy 0.9961, precision 0.9903, recall 0.9839, F1 0.9871, ROC-AUC 0.9998, and average precision 0.9991. XGBoost and the voting ensemble are close behind.

### Temporal validation

The chronological validation uses an 80/20 split and 5-fold time-series diagnostics. One fold has only a single target class and is marked as insufficient for ROC-AUC / average precision, which is recorded explicitly instead of being filled with fabricated values. In this regime, Random Forest drops sharply, while XGBoost and LightGBM remain much more robust.

The strongest temporal-validation scores in the saved outputs are XGBoost with F1 0.8097 and LightGBM with F1 0.8981. The main point is not the ranking alone, but the gap between standard random-split evaluation and honest chronological testing.

### Smart-charging simulation

The simulation baseline peak demand is 223,420.61. Redistributing high-stress demand and testing a V2G proxy both reduce peak demand, while a simple P3 delay strategy conserves energy but does not lower the peak in this configuration.

| Strategy | Peak demand | Peak reduction | Energy shifted | Intervals redistributed |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 223420.61 | 0.00% | 0.00 | 0 |
| Delay_P3_Peak | 223420.61 | 0.00% | 7235161.84 | 1008 |
| Redistribute_Top25Pct | 211012.62 | 5.55% | 2338606.36 | 313 |
| V2G_Peak_Shaving | 207018.58 | 7.34% | 551803.54 | 29 |

The validation report confirms energy conservation for the load-shifting strategies and documents the expected non-conservation behavior of the V2G proxy.

## Figures and Artifacts

The repository already contains the main generated artifacts:

- ROC curves: `figures/roc_lightgbm.png`, `figures/roc_random_forest.png`, `figures/roc_voting_ensemble.png`, `figures/roc_xgboost.png`
- Precision-recall curves: `figures/pr_lightgbm.png`, `figures/pr_random_forest.png`, `figures/pr_voting_ensemble.png`, `figures/pr_xgboost.png`
- Calibration plots: `figures/calibration_lightgbm.png`, `figures/calibration_random_forest.png`, `figures/calibration_voting_ensemble.png`, `figures/calibration_xgboost.png`
- SHAP summaries and feature rankings: `figures/shap/random_forest_summary.png`, `figures/shap/lightgbm_summary.png`, `figures/shap/xgboost_summary.png`, plus the corresponding bar charts and feature-importance CSVs
- SHAP dependence plots: `figures/shap/dependence/`
- Experiment-specific SHAP folders: `figures/shap/detection/`, `figures/shap/forecasting/`, `figures/shap/forecasting_temporal/`, `figures/shap/no_leakage/`

Key result files are stored in `results/metrics/`, including:

- `results/metrics/metrics.json`
- `results/metrics/metrics_detection.json`
- `results/metrics/metrics_forecasting.json`
- `results/metrics/metrics_forecasting_temporal.json`
- `results/metrics/metrics_no_leakage.json`
- `results/metrics/simulation_metrics.json`
- `results/metrics/simulation_load_curves.csv`

## Methodology Notes

- The target definition is fixed and documented in `results/reports/target_definition.md`.
- Feature engineering is restricted to observed aggregates and documented context variables.
- SHAP artifacts are generated only for supported tree-based models; the voting ensemble is skipped because SHAP is not implemented for it in this workflow.
- Discussion and conclusion templates are intentionally left as templates until the final narrative is written from the verified outputs.

## Limits

- The repository supports interval-level analysis, not individual-session analysis.
- Some source documents referenced by the environment verification report are missing from this workspace.
- Simulation results are policy proxies and should be interpreted as load-redistribution experiments rather than operational charger-control claims.
