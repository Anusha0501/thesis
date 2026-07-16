"""Generate dataset audit, data dictionary, feasibility, target, and methodology reports."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.preprocessing.data_loader import DataLoader
from src.utils.config import load_config

FILE_ROLES = {
    "charging_load": "Required for interval load features, total concurrent load, P3 load, and target creation.",
    "vehicle_count": "Required for interval vehicle-count features.",
    "usage_pattern": "Contextual EDA only; supports temporal behavior description.",
    "soc": "Optional context for charging behavior; not used as a leakage-prone interval feature unless alignable.",
    "ecr_temp": "Optional contextual EDA for energy-consumption sensitivity.",
    "ecr_month": "Used as seasonal proxy if month-level values are available.",
    "clusters": "Used as spatial/temporal cluster context where joinable to interval records.",
    "driving_dist": "Used to derive vehicle-type median driving-distance features.",
    "battery_energy": "Used to derive vehicle-type median battery-capacity features.",
    "energy_ratio": "Used to derive vehicle-type median daily energy-ratio features.",
    "charging_freq": "Used to derive vehicle-type charging-frequency features.",
    "charger_hist_car": "Reference for car power-level distributions and EDA.",
    "charger_hist_bus": "Reference for bus power-level distributions and EDA.",
    "charger_hist_spv": "Reference for SPV power-level distributions and EDA.",
}


def _column_profile(df: pd.DataFrame, dataset: str) -> list[dict[str, Any]]:
    profiles = []
    for col in df.columns:
        s = df[col]
        profiles.append({
            "dataset": dataset,
            "column": str(col),
            "dtype": str(s.dtype),
            "non_null": int(s.notna().sum()),
            "nulls": int(s.isna().sum()),
            "unique_values": int(s.nunique(dropna=True)),
            "min": s.min() if pd.api.types.is_numeric_dtype(s) else "",
            "max": s.max() if pd.api.types.is_numeric_dtype(s) else "",
            "meaning": _infer_column_meaning(str(col)),
        })
    return profiles


def _infer_column_meaning(column: str) -> str:
    lower = column.lower()
    if lower in {"time_slot", "time", "hour"} or "time" in lower:
        return "Temporal index or time-of-day field from the aggregated public dataset."
    if "p1" in lower or "p2" in lower or "p3" in lower or "power" in lower:
        return "Charging power-level or delivered-power aggregate/statistic."
    if "count" in lower or "vehicle" in lower:
        return "Vehicle category/count/statistic field."
    if "load" in lower or "kw" in lower:
        return "Charging load or power quantity."
    if "soc" in lower:
        return "State-of-charge statistic before or after charging."
    if "ecr" in lower or "temperature" in lower or "month" in lower:
        return "Energy-consumption-rate contextual variable."
    if "cdf" in lower or "percentile" in lower:
        return "Distribution percentile/CDF support field."
    return "Dataset-provided aggregate column; inspect values before modelling."


def generate_reports(config_path: str = "configs/config.yaml") -> None:
    cfg = load_config(config_path)
    reports = Path(cfg["paths"]["reports"])
    reports.mkdir(parents=True, exist_ok=True)
    loader = DataLoader(cfg)
    store = loader.load_all()
    audit = loader.audit(store)
    audit.to_csv(reports / "dataset_audit.csv", index=False)

    dictionary = []
    for name, df in store.frames.items():
        dictionary.extend(_column_profile(df, name))
    pd.DataFrame(dictionary).to_csv(reports / "data_dictionary.csv", index=False)

    with (reports / "dataset_audit.md").open("w", encoding="utf-8") as fh:
        fh.write("# Dataset Audit\n\n")
        fh.write("This audit is generated from the downloaded Zenodo CSV files. No results are fabricated.\n\n")
        fh.write(audit.to_markdown(index=False))
        fh.write("\n\n## File roles and requirement assessment\n\n")
        for name in audit["dataset"]:
            fh.write(f"- **{name}**: {FILE_ROLES.get(name, 'Supporting dataset file.')}\n")
        fh.write("\n## Assumptions\n\n- Public data are aggregated; the unit of analysis is a charging interval, not an individual session.\n- Any field engineering must be traceable to CSV columns or documented configuration.\n")

    dd = pd.DataFrame(dictionary)
    with (reports / "data_dictionary.md").open("w", encoding="utf-8") as fh:
        fh.write("# Data Dictionary\n\nEvery CSV column is profiled below using actual loaded files.\n\n")
        for dataset, sub in dd.groupby("dataset", sort=False):
            fh.write(f"## {dataset}\n\n")
            fh.write(sub.drop(columns=["dataset"]).to_markdown(index=False))
            fh.write("\n\n")

    with (reports / "research_feasibility.md").open("w", encoding="utf-8") as fh:
        fh.write("# Research Feasibility\n\n")
        fh.write("## Feasibility decision\n\nThe dataset supports the research question at the **charging-interval** level because it contains aggregated 5-minute charging load and vehicle-count curves by vehicle/power categories. It does not support individual-session or vehicle-trajectory claims.\n\n")
        fh.write("## Required files\n\n- Fig3-2 charging load: target/load features.\n- Fig3-1 vehicle counts: concurrent-count features.\n- Vehicle distribution files (Fig1b, Fig1e, Fig1f-1, Fig1f-2): vehicle-type context features where joinable.\n\n")
        fh.write("## Limitations\n\n- No VIN/session records.\n- Simulation operates on interval load redistribution, not real charger dispatch.\n- Conclusions must remain empty until pipelines are executed and outputs reviewed.\n")

    (reports / "target_definition.md").write_text(
        "# Target Definition\n\nHigh Grid Stress is defined exactly as: `(total_concurrent_load >= 75th percentile AND power_level == P3) OR (total_concurrent_load >= 90th percentile)`. Sensitivity analysis is implemented for 70%, 75%, 80%, 85%, and 90%. The definition is motivated by high-power charging/grid-congestion literature (Muratori 2018; Richardson 2013) and the dataset context of Zhan et al. (2025). No alternative target is introduced.\n",
        encoding="utf-8",
    )
    (reports / "methodology.md").write_text(
        "# Methodology\n\n## 1. Data Understanding\nAudit all Zenodo CSV files and document limitations.\n\n## 2. Data Preprocessing\nLoad aggregated interval data, normalize column names, reshape wide curves to interval records, and preserve provenance.\n\n## 3. Feature Engineering\nCreate temporal, charging, vehicle, grid, and contextual features from observed aggregates only.\n\n## 4. Target Definition\nApply the fixed composite high-grid-stress definition and percentile sensitivity checks.\n\n## 5. Model Development\nTrain Random Forest, XGBoost, LightGBM, and soft-voting ensemble using stratified splits, CV, class weighting, optional SMOTE, RandomizedSearchCV, and optional Optuna.\n\n## 6. Explainability\nGenerate SHAP artifacts after trained models exist; interpretation templates remain blank until results are reviewed.\n\n## 7. Smart Charging Simulation\nEvaluate baseline, P3 delay, predicted high-stress redistribution, V2G proxy, and optional probability-based adaptive control.\n\n## 8. Evaluation\nStore metrics, ROC/PR/calibration curves, confusion matrices, and simulation metrics without interpretation.\n\n## 9. Discussion Framework\nPopulate discussion only after experiments are executed on real data.\n",
        encoding="utf-8",
    )
    (reports / "conclusion_template.md").write_text("# Conclusion Template\n\n(To be completed after experiments.)\n", encoding="utf-8")


if __name__ == "__main__":
    generate_reports()
