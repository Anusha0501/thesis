# Methodology

## 1. Data Understanding
Audit all Zenodo CSV files and document the aggregate 5-minute interval unit of analysis.

## 2. Data Preprocessing
Download/extract the Zenodo archive, load configured CSVs, normalize index columns, and reshape load/count curves into interval records.

## 3. Feature Engineering
Create temporal, charging, vehicle, grid, and contextual features using observed aggregates and documented assumptions only.

## 4. Target Definition
Apply the fixed composite high-grid-stress definition and run percentile sensitivity analysis.

## 5. Model Development
Train Random Forest, XGBoost, LightGBM, and soft-voting ensemble models with stratified splitting, cross-validation, class weighting, optional SMOTE, RandomizedSearchCV, and optional Optuna extensions.

## 6. Explainability
Generate SHAP global and local artifacts only after models are trained. Interpretations remain blank until real outputs are reviewed.

## 7. Smart Charging Simulation
Evaluate Baseline, Delay_P3_Peak, Redistribute_Top25Pct, V2G_Peak_Shaving, and optional probability-based adaptive control.

## 8. Evaluation
Store metrics, ROC curves, PR curves, calibration curves, confusion matrices, predictions, and simulation metrics without interpretation.

## 9. Discussion Framework
Use discussion templates only until experiments are executed and validated.
