"""Interval-level smart charging simulation strategies."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pathlib import Path
import json
import numpy as np
import pandas as pd
from src.utils.config import load_config


def _metrics(base: pd.Series, sim: pd.Series, shifted: float, intervals: int) -> dict[str, float]:
    base_peak, sim_peak = float(base.max()), float(sim.max())
    return {
        "peak_demand": sim_peak,
        "peak_load_reduction_pct": (base_peak - sim_peak) / base_peak * 100 if base_peak else 0.0,
        "load_factor_improvement": float(sim.mean() / sim_peak - base.mean() / base_peak) if base_peak and sim_peak else 0.0,
        "off_peak_load_increase": float(sim.iloc[[i for i in range(len(sim)) if (i//12 in [1,2,3,4,22,23])]].sum() - base.iloc[[i for i in range(len(base)) if (i//12 in [1,2,3,4,22,23])]].sum()),
        "grid_utilization": float(sim.mean() / sim_peak) if sim_peak else 0.0,
        "energy_shifted": float(shifted),
        "charging_intervals_redistributed": int(intervals),
    }


def run_simulation(config_path: str = "configs/config.yaml", probability_mode: bool = True) -> None:
    cfg = load_config(config_path)
    df = pd.read_csv(Path(cfg["paths"]["processed_data"]) / "interval_features.csv")
    base = df.groupby("minute_of_day")["charging_load_kw"].sum().reindex(range(0, 1440, 5), fill_value=0)
    outputs = {"Baseline": _metrics(base, base, 0, 0)}
    delay = base.copy(); shifted = intervals = 0
    mask = (df["power_level"] == "P3") & (df["hour_of_day"].isin([7,8,9,17,18,19,20]))
    for _, r in df[mask].iterrows():
        src, dst, val = int(r.minute_of_day), int((r.minute_of_day + 120) % 1440), float(r.charging_load_kw)
        delay.loc[src] -= val; delay.loc[dst] += val; shifted += val; intervals += 1
    outputs["Delay_P3_Peak"] = _metrics(base, delay, shifted, intervals)
    red = base.copy(); shifted = intervals = 0
    pred_path = Path(cfg["paths"]["results"]) / "test_predictions.csv"
    stress_mask = df["high_grid_stress"] == 1
    if probability_mode and pred_path.exists():
        probs = pd.read_csv(pred_path, index_col=0).filter(like="_prob").mean(axis=1)
        stress_mask = df.index.isin(probs[probs > 0.8].index)
    off_peak_minutes = [m for m in base.index if m // 60 in [1,2,3,4,22,23]]
    for _, r in df[stress_mask].iterrows():
        src = int(r.minute_of_day); dst = min(off_peak_minutes, key=lambda m: abs(m - src)); val = float(r.charging_load_kw)
        red.loc[src] -= val; red.loc[dst] += val; shifted += val; intervals += 1
    outputs["Redistribute_Top25Pct"] = _metrics(base, red, shifted, intervals)
    v2g = base.copy(); cutoff = np.percentile(base, 90); affected = base[base >= cutoff].index
    discharge = df[(df["vehicle_type"].isin(["Bus", "Taxi"])) & (df["minute_of_day"].isin(affected))].groupby("minute_of_day")["charging_load_kw"].sum() * 0.15
    v2g.loc[discharge.index] -= discharge
    outputs["V2G_Peak_Shaving"] = _metrics(base, v2g, float(discharge.sum()), int(len(discharge)))
    out = Path(cfg["paths"]["results"]); out.mkdir(parents=True, exist_ok=True)
    (out / "simulation_metrics.json").write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    pd.DataFrame({"baseline": base, "delay_p3_peak": delay, "redistribute": red, "v2g": v2g}).to_csv(out / "simulation_load_curves.csv")

if __name__ == "__main__":
    run_simulation()
