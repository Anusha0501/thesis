# Methodology

## 1. Data Understanding
Audit all Zenodo CSV files and document limitations.

## 2. Data Preprocessing
Load aggregated interval data, normalize column names, reshape wide curves to interval records, and preserve provenance.

## 3. Feature Engineering
Create temporal, charging, vehicle, grid, and contextual features from observed aggregates only.

## 4. Target Definition
Apply the fixed composite high-grid-stress definition and percentile sensitivity checks.

## 5. Model Development
Train Random Forest, XGBoost, LightGBM, and soft-voting ensemble using stratified splits, CV, class weighting, optional SMOTE, RandomizedSearchCV, and optional Optuna.

## 6. Explainability
Generate SHAP artifacts after trained models exist; interpretation templates remain blank until results are reviewed.

## 7. Smart Charging Simulation
Evaluate baseline, P3 delay, predicted high-stress redistribution, V2G proxy, and optional probability-based adaptive control.

## 8. Evaluation
Store metrics, ROC/PR/calibration curves, confusion matrices, and simulation metrics without interpretation.

## 9. Discussion Framework
Populate discussion only after experiments are executed on real data.
