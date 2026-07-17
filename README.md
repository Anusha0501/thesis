# Temporal Robustness of Explainable Ensemble Machine Learning for High Grid-Stress EV Charging Prediction and Smart Charging Simulation

This repository contains the code, metrics, figures, and reports for a B.Tech thesis on interval-level EV charging analysis. The work identifies high grid-stress charging intervals, compares standard random-split evaluation with chronological validation, and simulates smart-charging policies to test whether prediction-guided intervention can reduce peak demand in a physically meaningful way.

The central contribution is methodological: the thesis shows that standard random-split evaluation can substantially overestimate performance by masking temporal overfitting, while chronological validation reveals which models are robust enough for future deployment.

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

The thesis begins with a grid-operation question: EV charging does not only consume energy, it can also concentrate demand into short time windows and create high-stress periods for the electricity system. The goal is therefore not simply to predict load, but to identify intervals where charging conditions indicate elevated grid stress and to test whether those predictions can support smarter charging decisions.

The data audit clarified an important scope decision. The available Zenodo data are aggregated 5-minute intervals rather than individual charging sessions, so the correct unit of analysis is a charging interval. This is a methodological boundary, not a weakness. It keeps the claims aligned with the data and avoids overstating session-level conclusions.

The thesis then tests four progressively more realistic evaluation settings. Experiment A provides a leakage-prone benchmark, Experiment B removes target-defining variables, Experiment C forecasts the next interval under a random split, and Experiment D uses chronological validation. The comparison between Experiments C and D is the main novelty: it shows that a model can look excellent under conventional evaluation but degrade sharply when tested the way it would be used in deployment.

The final stage moves from prediction to intervention. The simulation uses the predicted stress structure to test load-shifting policies and checks whether the resulting load curves are physically plausible, energy-consistent, and capable of reducing peak demand.

## Problem Statement

High EV charging demand can create grid stress when many vehicles charge at the same time or when charging load concentrates during already busy periods. In practical terms, utilities need to answer a simple question: which intervals are likely to be stressed, and can those intervals be shifted or controlled before the peak occurs?

The thesis addresses that question using supervised learning and simulation. The operational target, called high grid stress, is defined from the aggregated dataset using a percentile-based rule documented in `results/reports/target_definition.md`. The definition is not a universal law; it is an operational threshold motivated by literature and the available data.

## Why Temporal Robustness Matters

Temporal robustness means that a model should remain useful when it is asked to predict future unseen intervals, not just shuffled historical data. This matters because real grid deployment is chronological: the model is trained on past data and then used on later data.

The thesis demonstrates that random splits can hide this issue. They mix similar past and future patterns into both train and test sets, which can make the model appear stronger than it really is. Chronological validation is therefore a more honest test of deployment readiness.

## Thesis Contributions

- A scientifically justified reframing from session-level claims to interval-level grid-stress prediction.
- A leakage-aware modelling pipeline that separates honest features from target-defining variables.
- A direct comparison between random-split and chronological validation for deployment realism.
- SHAP-based interpretation for tree models to support global and local explanation.
- A validated smart-charging simulation that conserves energy for load-shifting strategies and quantifies peak reduction.
- A reproducible codebase with audit reports, tests, metrics, and saved figures.

## What the Four Experiments Show

| Experiment | Question | Interpretation |
| --- | --- | --- |
| Experiment A: Detection benchmark | Can the models identify high grid stress when all features are available? | All models achieve perfect scores because the feature set includes variables that are directly tied to the target definition, so the result is not a fair estimate of deployment performance. |
| Experiment B: No-leakage detection | What happens when target-defining variables are removed? | Performance drops, but remains strong. The best F1 score is 0.9003 for the voting ensemble, and XGBoost remains highly competitive with F1 0.8889. |
| Experiment C: Random-split forecasting | Can the models predict the next interval under standard random splitting? | Scores remain very strong, with LightGBM achieving the best F1 at 0.9871. This setting is useful as a benchmark, but it is still optimistic for future deployment. |
| Experiment D: Chronological forecasting | Can the models predict future intervals under honest temporal validation? | Temporal overfitting becomes visible. Random Forest falls to F1 0.2490, while XGBoost and LightGBM remain much more robust at F1 0.8097 and 0.9871, respectively. |

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

This is an operational definition used to create a supervised target from aggregated interval data. It is not arbitrary: the thesis motivates it from the literature and supports it with sensitivity analysis.

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

The confusion matrix for each model is 1,768 true negatives and 313 true positives, with zero false positives and zero false negatives. This is a methodological leakage benchmark, not the final deployment result.

### No-leakage benchmark

When leakage-prone interval features are removed, performance remains strong. The best no-leakage model is the voting ensemble with F1 0.9003, followed closely by LightGBM with F1 0.8981 and XGBoost with F1 0.8889.

### One-interval-ahead forecasting

For the one-step-ahead target, LightGBM is the strongest overall model under random splitting with accuracy 0.9961, precision 0.9903, recall 0.9839, F1 0.9871, ROC-AUC 0.9998, and average precision 0.9991. XGBoost and the voting ensemble are close behind.

### Temporal validation

The chronological validation uses an 80/20 split and 5-fold time-series diagnostics. One fold has only a single target class and is marked as insufficient for ROC-AUC / average precision, which is recorded explicitly instead of being filled with fabricated values. In this regime, Random Forest drops sharply to F1 0.2490, while XGBoost remains at F1 0.8097 and LightGBM remains strong at F1 0.9871 on the saved hold-out output.

The strongest temporal-validation scores in the saved outputs are XGBoost with F1 0.8097 and LightGBM with F1 0.9871. The main point is not the ranking alone, but the gap between standard random-split evaluation and honest chronological testing.

### Smart-charging simulation

The simulation baseline peak demand is 223,420.61. Redistributing high-stress demand and testing a V2G proxy both reduce peak demand, while a simple P3 delay strategy conserves energy but does not lower the peak in this configuration.

| Strategy | Peak demand | Peak reduction | Energy shifted | Intervals redistributed |
| --- | ---: | ---: | ---: | ---: |
| Baseline | 223420.61 | 0.00% | 0.00 | 0 |
| Delay_P3_Peak | 223420.61 | 0.00% | 7235161.84 | 1008 |
| Redistribute_Top25Pct | 211012.62 | 5.55% | 2338606.36 | 313 |
| V2G_Peak_Shaving | 207018.58 | 7.34% | 551803.54 | 29 |

The validation report confirms energy conservation for the load-shifting strategies and documents the expected non-conservation behavior of the V2G proxy. The best strategy reduces peak demand by 7.34%, which is the clearest bridge from prediction to operational impact in the thesis.

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
- The current thesis does not report repeated-run uncertainty or confidence intervals for all experiments.
