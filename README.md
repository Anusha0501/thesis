# Analysis of EV Usage Patterns and Charging Behavior for Smart Energy Management

Research question: Can explainable ensemble machine learning identify high grid-stress EV charging intervals, and how can these predictions be used to design an adaptive smart charging strategy for reducing peak electricity demand?

## Integrity policy

This repository never hard-codes model results, SHAP findings, simulation conclusions, or publication claims. Reports generated before execution are templates or dataset audits only. The unit of analysis is a charging interval because the public Zenodo dataset contains aggregated 5-minute data, not individual sessions.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Commands

```bash
python src/preprocessing/audit_reports.py
python src/features/feature_engineering.py
python src/pipelines/train_pipeline.py
python src/pipelines/evaluation_pipeline.py
python src/pipelines/simulation_pipeline.py
python src/pipelines/run_all.py
```

## Expected output folders

- `data/raw/`: Zenodo zip and extracted CSVs.
- `data/processed/`: interval-level modelling table.
- `models/saved/`: trained model artifacts.
- `results/metrics/`: metrics, predictions, simulation outputs.
- `results/reports/`: audit, dictionary, feasibility, methodology, target definition, templates.
- `figures/`: EDA/evaluation/SHAP/simulation plots.

## Thesis writing checklist

- [ ] Confirm dataset audit findings.
- [ ] Report limitations before methods.
- [ ] Insert real metric tables only after execution.
- [ ] Leave conclusions blank until results are reviewed.

## Paper writing checklist

- [ ] Clearly state interval-level unit of analysis.
- [ ] Cite Muratori (2018), Richardson (2013), and Zhan et al. (2025) for target motivation.
- [ ] Separate verified contributions from hypotheses.

## Viva preparation checklist

- [ ] Explain why individual-session claims are unsupported.
- [ ] Defend the high-grid-stress target definition.
- [ ] Explain model comparison and class imbalance handling.
- [ ] Explain adaptive controller probability thresholds.
