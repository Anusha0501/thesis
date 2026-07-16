"""Feature engineering for interval-level grid-stress classification.

Only features supported by local CSV contents are created.  Vehicle-level summary
features are populated from distribution/statistic CSVs when a vehicle-type column
and a numeric value column can be identified; otherwise the feature is omitted from
configuration and the modelling feature set rather than filled with placeholders.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import logging
import re
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.preprocessing.data_loader import DataLoader
from src.utils.config import load_config

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

VEHICLES = ["Private car", "Official car", "Rental car", "Taxi", "Bus", "SPV"]


def parse_series_column(column: str) -> tuple[str, str, str]:
    """Infer vehicle type, power level, and day type from an aggregate curve column."""
    normalized = re.sub(r"[^a-z0-9]", "", column.lower())
    power = next((p for p in ["P1", "P2", "P3"] if re.search(rf"(^|[^a-z0-9]){p}([^a-z0-9]|$)|_{p}|{p}_", column, re.I)), "P_unknown")
    aliases = {"Private car": ["privatecar", "private"], "Official car": ["officialcar", "official"], "Rental car": ["rentalcar", "rental"], "Taxi": ["taxi"], "Bus": ["bus"], "SPV": ["spv", "specialpurposevehicle"]}
    vehicle = next((v for v, pats in aliases.items() if any(p in normalized for p in pats)), "Unknown")
    lower = column.lower()
    day_type = "workday" if "work" in lower or "weekday" in lower else "non_workday" if "weekend" in lower or "holiday" in lower or "non" in lower else "all"
    return vehicle, power, day_type


def minute_from_slot(value: Any, fallback_idx: int) -> int:
    """Convert a time-slot label to minute-of-day; fallback assumes 5-minute rows."""
    text = str(value)
    match = re.search(r"(\d{1,2}):(\d{2})", text)
    if match:
        return (int(match.group(1)) * 60 + int(match.group(2))) % 1440
    return (fallback_idx * 5) % 1440


def _vehicle_column(df: pd.DataFrame) -> str | None:
    for col in df.columns:
        lower = str(col).lower()
        if "type" in lower or "vehicle" in lower:
            vals = " ".join(map(str, df[col].dropna().head(50))).lower()
            if any(v.lower().split()[0] in vals for v in VEHICLES):
                return col
    return None


def _numeric_value_column(df: pd.DataFrame, preferred: list[str] | None = None) -> str | None:
    numeric = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if not numeric:
        return None
    preferred = preferred or []
    for token in preferred:
        for col in numeric:
            if token.lower() in str(col).lower():
                return col
    return numeric[-1]


def _vehicle_summary(df: pd.DataFrame, preferred: list[str] | None = None) -> dict[str, float]:
    vcol = _vehicle_column(df)
    valcol = _numeric_value_column(df, preferred)
    if vcol is None or valcol is None:
        return {}
    tmp = df[[vcol, valcol]].dropna().copy()
    tmp[vcol] = tmp[vcol].astype(str).str.strip()
    return tmp.groupby(vcol)[valcol].median().to_dict()


def _map_vehicle_feature(df: pd.DataFrame, feature_name: str, values: dict[str, float]) -> pd.DataFrame:
    if values:
        df[feature_name] = df["vehicle_type"].map(values)
        LOGGER.info("Populated %s for %d vehicle labels", feature_name, df[feature_name].notna().sum())
    return df


def _add_supported_context_features(df: pd.DataFrame, store: Any) -> pd.DataFrame:
    """Populate context features from real CSVs where schema allows it."""
    df = _map_vehicle_feature(df, "battery_median_kwh", _vehicle_summary(store["battery_energy"], ["battery", "energy", "kwh"]))
    df = _map_vehicle_feature(df, "energy_ratio_median", _vehicle_summary(store["energy_ratio"], ["ratio", "energy"]))
    df = _map_vehicle_feature(df, "daily_charging_freq", _vehicle_summary(store["charging_freq"], ["charging", "event", "frequency", "number"]))
    df = _map_vehicle_feature(df, "daily_driving_dist_p50", _vehicle_summary(store["driving_dist"], ["distance", "km"]))
    ecr = store["ecr_month"]
    ecr_col = _numeric_value_column(ecr, ["ecr", "energy"])
    if ecr_col is not None:
        df["ecr_month_mean"] = float(pd.to_numeric(ecr[ecr_col], errors="coerce").mean())
    return df


def build_interval_dataset(config_path: str = "configs/config.yaml") -> pd.DataFrame:
    """Build and save interval-level ML table from aggregate load/count CSVs."""
    cfg = load_config(config_path)
    store = DataLoader(cfg).load_all()
    load = store["charging_load"].copy()
    count = store["vehicle_count"].copy()
    id_col = "time_slot" if "time_slot" in load.columns else load.columns[0]
    long_load = load.melt(id_vars=[id_col], var_name="series", value_name="charging_load_kw")
    long_count = count.melt(id_vars=[id_col], var_name="series", value_name="vehicle_count")
    df = long_load.merge(long_count, on=[id_col, "series"], how="left")
    df["charging_load_kw"] = pd.to_numeric(df["charging_load_kw"], errors="coerce").fillna(0)
    df["vehicle_count"] = pd.to_numeric(df["vehicle_count"], errors="coerce").fillna(0)

    parsed = df["series"].apply(parse_series_column).apply(pd.Series)
    parsed.columns = ["vehicle_type", "power_level", "day_type"]
    df = pd.concat([df, parsed], axis=1)
    df["minute_of_day"] = [minute_from_slot(v, i) for i, v in enumerate(df[id_col])]
    df["hour_of_day"] = (df["minute_of_day"] // 60).astype(int)
    df["hour_sin"] = np.sin(2 * np.pi * df["minute_of_day"] / 1440)
    df["hour_cos"] = np.cos(2 * np.pi * df["minute_of_day"] / 1440)
    df["is_peak_morning"] = df["hour_of_day"].between(7, 9).astype(int)
    df["is_peak_evening"] = df["hour_of_day"].between(17, 20).astype(int)
    df["is_daytime"] = df["hour_of_day"].between(6, 21).astype(int)
    df["is_night"] = ((df["hour_of_day"] >= 22) | (df["hour_of_day"] < 6)).astype(int)
    df["is_workday"] = (df["day_type"] == "workday").astype(int)
    df["vehicle_type_encoded"] = df["vehicle_type"].astype("category").cat.codes
    df["power_level_encoded"] = df["power_level"].map({"P1": 0, "P2": 1, "P3": 2}).fillna(-1).astype(int)
    df["is_service_vehicle"] = df["vehicle_type"].isin(["Taxi", "Bus", "Rental car", "SPV"]).astype(int)
    # Bounds are intentionally broad class definitions from the study configuration.
    bounds = {"P1": (0, 4), "P2": (4, 20), "P3": (20, 999)}
    df["power_level_kw_min"] = df["power_level"].map(lambda p: bounds.get(p, (np.nan, np.nan))[0])
    df["power_level_kw_max"] = df["power_level"].map(lambda p: bounds.get(p, (np.nan, np.nan))[1])
    group_cols = [id_col, "day_type"]
    totals = df.groupby(group_cols, dropna=False)["charging_load_kw"].transform("sum")
    p3_totals = df.assign(_p3=df["charging_load_kw"].where(df["power_level"] == "P3", 0)).groupby(group_cols, dropna=False)["_p3"].transform("sum")
    df["total_concurrent_load"] = totals
    df["p3_concurrent_load"] = p3_totals
    df["load_share"] = np.divide(df["charging_load_kw"], totals.replace(0, np.nan)).fillna(0)
    df = _add_supported_context_features(df, store)

    loads = df["total_concurrent_load"].dropna()
    p75 = np.percentile(loads, cfg["target"]["load_percentile_threshold"])
    p90 = np.percentile(loads, cfg["target"]["high_load_only_pct"])
    df["high_grid_stress"] = (((df["total_concurrent_load"] >= p75) & (df["power_level"] == "P3")) | (df["total_concurrent_load"] >= p90)).astype(int)
    sensitivity_rows = []
    for pct in cfg["target"].get("sensitivity_percentiles", []):
        cutoff = np.percentile(loads, pct)
        col = f"high_grid_stress_p{pct}"
        df[col] = (((df["total_concurrent_load"] >= cutoff) & (df["power_level"] == "P3")) | (df["total_concurrent_load"] >= p90)).astype(int)
        sensitivity_rows.append({"percentile": pct, "cutoff_total_concurrent_load": cutoff, "positive_intervals": int(df[col].sum()), "positive_rate": float(df[col].mean())})

    out = Path(cfg["paths"]["processed_data"]) / "interval_features.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    reports = Path(cfg["paths"].get("reports", "results/reports")); reports.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(sensitivity_rows).to_csv(reports / "target_sensitivity_analysis.csv", index=False)
    (reports / "target_sensitivity_analysis.md").write_text("# Target Sensitivity Analysis\n\n" + pd.DataFrame(sensitivity_rows).to_markdown(index=False) + "\n", encoding="utf-8")
    LOGGER.info("Saved %s shape=%s", out, df.shape)
    return df


if __name__ == "__main__":
    build_interval_dataset()
