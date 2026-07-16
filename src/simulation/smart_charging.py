"""Interval-level smart charging simulation strategies."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.utils.config import load_config

OFF_PEAK_HOURS = {1, 2, 3, 4, 22, 23}
PEAK_INCREASE_TOLERANCE = 1.20
FLOAT_TOLERANCE = 1e-6


def _off_peak_minutes(index: pd.Index) -> list[int]:
    """Return off-peak minute labels from a five-minute load curve index."""

    return [int(minute) for minute in index if int(minute) // 60 in OFF_PEAK_HOURS]


def _metrics(base: pd.Series, sim: pd.Series, shifted: float, intervals: int) -> dict[str, float]:
    base_peak, sim_peak = float(base.max()), float(sim.max())
    off_peak = _off_peak_minutes(base.index)
    return {
        "peak_demand": sim_peak,
        "peak_load_reduction_pct": (base_peak - sim_peak) / base_peak * 100 if base_peak else 0.0,
        "load_factor_improvement": float(sim.mean() / sim_peak - base.mean() / base_peak) if base_peak and sim_peak else 0.0,
        "off_peak_load_increase": float(sim.loc[off_peak].sum() - base.loc[off_peak].sum()) if off_peak else 0.0,
        "grid_utilization": float(sim.mean() / sim_peak) if sim_peak else 0.0,
        "energy_shifted": float(shifted),
        "charging_intervals_redistributed": int(intervals),
    }


def _shift_load(load_curve: pd.Series, source_minute: int, destination_minute: int, load_kw: float) -> pd.Series:
    """Move load between intervals by subtracting old load and adding new load."""

    shifted = load_curve.copy()
    shifted.loc[source_minute] -= load_kw
    shifted.loc[destination_minute] += load_kw
    return shifted


def _assert_no_negative_loads(load_curve: pd.Series, strategy_name: str, tolerance: float = FLOAT_TOLERANCE) -> None:
    """Reject physically impossible negative interval loads."""

    min_load = float(load_curve.min())
    if min_load < -tolerance:
        raise AssertionError(f"{strategy_name} produced negative loads: minimum={min_load}")


def _assert_energy_conserved(
    before: pd.Series,
    after: pd.Series,
    strategy_name: str,
    tolerance: float = FLOAT_TOLERANCE,
) -> None:
    """Ensure shifted charging energy is conserved within floating point tolerance."""

    before_total = float(before.sum())
    after_total = float(after.sum())
    if not np.isclose(before_total, after_total, rtol=0.0, atol=tolerance):
        raise AssertionError(
            f"{strategy_name} did not conserve total load: before={before_total}, after={after_total}"
        )


def _assert_peak_not_unrealistic(
    before: pd.Series,
    after: pd.Series,
    strategy_name: str,
    max_increase_factor: float = PEAK_INCREASE_TOLERANCE,
) -> None:
    """Guard against pathological stacking that creates unrealistic new peaks."""

    base_peak = float(before.max())
    after_peak = float(after.max())
    if base_peak > 0 and after_peak > base_peak * max_increase_factor:
        raise AssertionError(
            f"{strategy_name} increased peak demand unrealistically: before={base_peak}, after={after_peak}"
        )


def _validate_shifted_strategy(base: pd.Series, simulated: pd.Series, strategy_name: str) -> dict[str, Any]:
    """Run physical-validity checks for load-shifting strategies."""

    _assert_energy_conserved(base, simulated, strategy_name)
    _assert_no_negative_loads(simulated, strategy_name)
    _assert_peak_not_unrealistic(base, simulated, strategy_name)
    return {
        "energy_before": float(base.sum()),
        "energy_after": float(simulated.sum()),
        "energy_conserved": True,
        "baseline_peak": float(base.max()),
        "simulated_peak": float(simulated.max()),
        "peak_increase_factor": float(simulated.max() / base.max()) if float(base.max()) else 0.0,
        "negative_loads": False,
    }


def _validate_v2g_strategy(base: pd.Series, simulated: pd.Series, strategy_name: str) -> dict[str, Any]:
    """Validate V2G peak shaving, where net grid energy may decrease by design."""

    _assert_no_negative_loads(simulated, strategy_name)
    _assert_peak_not_unrealistic(base, simulated, strategy_name)
    return {
        "energy_before": float(base.sum()),
        "energy_after": float(simulated.sum()),
        "energy_conserved": False,
        "energy_delta": float(simulated.sum() - base.sum()),
        "baseline_peak": float(base.max()),
        "simulated_peak": float(simulated.max()),
        "peak_increase_factor": float(simulated.max() / base.max()) if float(base.max()) else 0.0,
        "negative_loads": False,
    }


def _delay_p3_peak(df: pd.DataFrame, base: pd.Series) -> tuple[pd.Series, float, int, dict[str, Any]]:
    """Delay P3 charging in peak windows by two hours while conserving load."""

    delayed = base.copy()
    shifted = 0.0
    intervals = 0
    mask = (df["power_level"] == "P3") & (df["hour_of_day"].isin([7, 8, 9, 17, 18, 19, 20]))
    for _, row in df[mask].iterrows():
        source = int(row.minute_of_day)
        destination = int((row.minute_of_day + 120) % 1440)
        load_kw = float(row.charging_load_kw)
        delayed = _shift_load(delayed, source, destination, load_kw)
        shifted += load_kw
        intervals += 1
    validation = _validate_shifted_strategy(base, delayed, "Delay_P3_Peak")
    return delayed, shifted, intervals, validation


def _redistribute_top_stress(
    df: pd.DataFrame,
    base: pd.Series,
    stress_mask: pd.Series | np.ndarray,
) -> tuple[pd.Series, float, int, dict[str, Any]]:
    """Redistribute stressed intervals across the least-loaded off-peak slots."""

    redistributed = base.copy()
    shifted = 0.0
    intervals = 0
    off_peak_minutes = _off_peak_minutes(base.index)
    destination_counts = {minute: 0 for minute in off_peak_minutes}
    if not off_peak_minutes:
        validation = _validate_shifted_strategy(base, redistributed, "Redistribute_Top25Pct")
        validation["destination_minutes_used"] = 0
        return redistributed, shifted, intervals, validation

    rows = df[stress_mask].sort_values("charging_load_kw", ascending=False)
    for _, row in rows.iterrows():
        source = int(row.minute_of_day)
        load_kw = float(row.charging_load_kw)
        destination = min(
            off_peak_minutes,
            key=lambda minute: (float(redistributed.loc[minute]), destination_counts[minute], abs(minute - source)),
        )
        redistributed = _shift_load(redistributed, source, destination, load_kw)
        destination_counts[destination] += 1
        shifted += load_kw
        intervals += 1

    validation = _validate_shifted_strategy(base, redistributed, "Redistribute_Top25Pct")
    used_destinations = [minute for minute, count in destination_counts.items() if count > 0]
    validation.update(
        {
            "destination_minutes_used": len(used_destinations),
            "max_destination_assignments": max(destination_counts.values()) if destination_counts else 0,
            "off_peak_minutes_available": len(off_peak_minutes),
        }
    )
    return redistributed, shifted, intervals, validation


def _v2g_peak_shaving(df: pd.DataFrame, base: pd.Series) -> tuple[pd.Series, float, int, dict[str, Any]]:
    """Apply a bounded V2G peak-shaving discharge for buses and taxis."""

    v2g = base.copy()
    cutoff = np.percentile(base, 90)
    affected = base[base >= cutoff].index
    discharge = (
        df[(df["vehicle_type"].isin(["Bus", "Taxi"])) & (df["minute_of_day"].isin(affected))]
        .groupby("minute_of_day")["charging_load_kw"]
        .sum()
        * 0.15
    )
    discharge = discharge.clip(upper=v2g.loc[discharge.index])
    v2g.loc[discharge.index] -= discharge
    validation = _validate_v2g_strategy(base, v2g, "V2G_Peak_Shaving")
    return v2g, float(discharge.sum()), int(len(discharge)), validation


def _write_simulation_validation_report(cfg: dict[str, Any], validation: dict[str, dict[str, Any]]) -> None:
    """Write simulation validation details without inventing results."""

    reports = Path(cfg["paths"].get("reports", "results/reports"))
    reports.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Simulation Validation",
        "",
        "This report is generated from actual simulation validation checks.",
        "",
        "| Strategy | Energy before | Energy after | Energy conserved | Baseline peak | Simulated peak | Negative loads |",
        "| --- | ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for strategy, checks in validation.items():
        lines.append(
            f"| {strategy} | {checks.get('energy_before', 'n/a')} | {checks.get('energy_after', 'n/a')} | "
            f"{checks.get('energy_conserved', 'n/a')} | {checks.get('baseline_peak', 'n/a')} | "
            f"{checks.get('simulated_peak', 'n/a')} | {checks.get('negative_loads', 'n/a')} |"
        )
    lines.extend([
        "",
        "## Energy conservation checks",
        "",
        "The table above reports pre- and post-simulation aggregate load for each strategy. Load-shifting strategies must conserve total load within floating point tolerance.",
        "",
        "## Peak calculations",
        "",
        "The table above reports baseline and simulated peak demand. Validation raises an assertion if a strategy creates an unrealistic peak increase.",
        "",
        "## Load redistribution verification",
        "",
    ])
    redistribution = validation.get("Redistribute_Top25Pct")
    if redistribution:
        lines.extend(
            [
                f"- Off-peak intervals available: {redistribution.get('off_peak_minutes_available', 'n/a')}",
                f"- Destination intervals used: {redistribution.get('destination_minutes_used', 'n/a')}",
                f"- Maximum assignments to one destination interval: {redistribution.get('max_destination_assignments', 'n/a')}",
            ]
        )
    else:
        lines.append("Redistribution validation was not run.")
    (reports / "simulation_validation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_simulation(config_path: str = "configs/config.yaml", probability_mode: bool = True) -> None:
    cfg = load_config(config_path)
    df = pd.read_csv(Path(cfg["paths"]["processed_data"]) / "interval_features.csv")
    base = df.groupby("minute_of_day")["charging_load_kw"].sum().reindex(range(0, 1440, 5), fill_value=0)
    validation: dict[str, dict[str, Any]] = {"Baseline": _validate_shifted_strategy(base, base, "Baseline")}
    outputs = {"Baseline": _metrics(base, base, 0, 0)}

    delay, shifted, intervals, validation["Delay_P3_Peak"] = _delay_p3_peak(df, base)
    outputs["Delay_P3_Peak"] = _metrics(base, delay, shifted, intervals)

    pred_path = Path(cfg["paths"]["results"]) / "test_predictions.csv"
    stress_mask: pd.Series | np.ndarray = df["high_grid_stress"] == 1
    if probability_mode and pred_path.exists():
        probs = pd.read_csv(pred_path, index_col=0).filter(like="_prob").mean(axis=1)
        stress_mask = df.index.isin(probs[probs > 0.8].index)
    red, shifted, intervals, validation["Redistribute_Top25Pct"] = _redistribute_top_stress(df, base, stress_mask)
    outputs["Redistribute_Top25Pct"] = _metrics(base, red, shifted, intervals)

    v2g, shifted, intervals, validation["V2G_Peak_Shaving"] = _v2g_peak_shaving(df, base)
    outputs["V2G_Peak_Shaving"] = _metrics(base, v2g, shifted, intervals)

    out = Path(cfg["paths"]["results"])
    out.mkdir(parents=True, exist_ok=True)
    (out / "simulation_metrics.json").write_text(json.dumps(outputs, indent=2), encoding="utf-8")
    pd.DataFrame({"baseline": base, "delay_p3_peak": delay, "redistribute": red, "v2g": v2g}).to_csv(
        out / "simulation_load_curves.csv"
    )
    _write_simulation_validation_report(cfg, validation)


if __name__ == "__main__":
    run_simulation()
