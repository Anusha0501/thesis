"""Feature engineering for interval-level grid-stress classification."""
from __future__ import annotations

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


def parse_series_column(column: str) -> tuple[str, str, str]:
    """Infer vehicle type, power level, and day type from an aggregate curve column."""
    power = next((p for p in ["P1", "P2", "P3"] if re.search(rf"\b{p}\b|_{p}|{p}_", column, re.I)), "P_unknown")
    lower = column.lower()
    vehicles = ["Private car", "Official car", "Rental car", "Taxi", "Bus", "SPV"]
    vehicle = next((v for v in vehicles if v.lower().replace(" ", "") in lower.replace(" ", "")), "Unknown")
    day_type = "workday" if "work" in lower or "weekday" in lower else "non_workday" if "week" in lower or "holiday" in lower else "all"
    return vehicle, power, day_type


def minute_from_slot(value: Any, fallback_idx: int) -> int:
    """Convert a time-slot label to minute-of-day; fallback assumes 5-minute rows."""
    text = str(value)
    match = re.search(r"(\d{1,2}):(\d{2})", text)
    if match:
        return int(match.group(1)) * 60 + int(match.group(2))
    return (fallback_idx * 5) % 1440


def build_interval_dataset(config_path: str = "configs/config.yaml") -> pd.DataFrame:
    """Build and save interval-level ML table from aggregate load/count CSVs."""
    cfg = load_config(config_path)
    loader = DataLoader(cfg)
    store = loader.load_all()
    load = store["charging_load"].copy()
    count = store["vehicle_count"].copy()
    id_col = "time_slot" if "time_slot" in load.columns else load.columns[0]
    long_load = load.melt(id_vars=[id_col], var_name="series", value_name="charging_load_kw")
    long_count = count.melt(id_vars=[id_col], var_name="series", value_name="vehicle_count")
    df = long_load.merge(long_count, on=[id_col, "series"], how="left")
    parsed = df["series"].apply(parse_series_column).apply(pd.Series)
    parsed.columns = ["vehicle_type", "power_level", "day_type"]
    df = pd.concat([df, parsed], axis=1)
    df["minute_of_day"] = [minute_from_slot(v, i) for i, v in enumerate(df[id_col])]
    df["hour_of_day"] = (df["minute_of_day"] // 60).astype(int)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour_of_day"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour_of_day"] / 24)
    df["is_peak_morning"] = df["hour_of_day"].between(7, 9).astype(int)
    df["is_peak_evening"] = df["hour_of_day"].between(17, 20).astype(int)
    df["is_daytime"] = df["hour_of_day"].between(6, 21).astype(int)
    df["is_night"] = ((df["hour_of_day"] >= 22) | (df["hour_of_day"] < 6)).astype(int)
    df["is_workday"] = (df["day_type"] == "workday").astype(int)
    df["vehicle_type_encoded"] = df["vehicle_type"].astype("category").cat.codes
    df["power_level_encoded"] = df["power_level"].map({"P1": 0, "P2": 1, "P3": 2}).fillna(-1).astype(int)
    df["is_service_vehicle"] = df["vehicle_type"].isin(["Taxi", "Bus", "Rental car", "SPV"]).astype(int)
    bounds = {"P1": (0, 4), "P2": (4, 20), "P3": (20, 999)}
    df["power_level_kw_min"] = df["power_level"].map(lambda p: bounds.get(p, (np.nan, np.nan))[0])
    df["power_level_kw_max"] = df["power_level"].map(lambda p: bounds.get(p, (np.nan, np.nan))[1])
    group_cols = [id_col, "day_type"]
    totals = df.groupby(group_cols, dropna=False)["charging_load_kw"].transform("sum")
    p3_totals = df.assign(_p3=df["charging_load_kw"].where(df["power_level"] == "P3", 0)).groupby(group_cols, dropna=False)["_p3"].transform("sum")
    df["total_concurrent_load"] = totals
    df["p3_concurrent_load"] = p3_totals
    df["load_share"] = np.divide(df["charging_load_kw"], totals.replace(0, np.nan)).fillna(0)
    df["cluster_id"] = 0
    df["battery_median_kwh"] = np.nan
    df["energy_ratio_median"] = np.nan
    df["daily_charging_freq"] = np.nan
    df["daily_driving_dist_p50"] = np.nan
    df["ecr_month_mean"] = np.nan
    p75 = np.percentile(df["total_concurrent_load"].dropna(), cfg["target"]["load_percentile_threshold"])
    p90 = np.percentile(df["total_concurrent_load"].dropna(), cfg["target"]["high_load_only_pct"])
    df["high_grid_stress"] = (((df["total_concurrent_load"] >= p75) & (df["power_level"] == "P3")) | (df["total_concurrent_load"] >= p90)).astype(int)
    for pct in cfg["target"].get("sensitivity_percentiles", []):
        cutoff = np.percentile(df["total_concurrent_load"].dropna(), pct)
        df[f"high_grid_stress_p{pct}"] = (((df["total_concurrent_load"] >= cutoff) & (df["power_level"] == "P3")) | (df["total_concurrent_load"] >= p90)).astype(int)
    out = Path(cfg["paths"]["processed_data"]) / "interval_features.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    LOGGER.info("Saved %s shape=%s", out, df.shape)
    return df


if __name__ == "__main__":
    build_interval_dataset()
