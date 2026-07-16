import pandas as pd
import pytest

from src.simulation.smart_charging import (
    _assert_energy_conserved,
    _assert_no_negative_loads,
    _assert_peak_not_unrealistic,
    _redistribute_top_stress,
    _shift_load,
)


def _base_curve(value: float = 10.0) -> pd.Series:
    return pd.Series(value, index=range(0, 1440, 5), dtype=float)


def test_shift_load_subtracts_source_and_adds_destination_with_energy_conserved():
    base = _base_curve()

    shifted = _shift_load(base, source_minute=60, destination_minute=120, load_kw=4.5)

    assert shifted.loc[60] == pytest.approx(base.loc[60] - 4.5)
    assert shifted.loc[120] == pytest.approx(base.loc[120] + 4.5)
    _assert_energy_conserved(base, shifted, "unit_test_shift")


def test_redistribution_spreads_load_across_multiple_off_peak_intervals():
    base = _base_curve()
    df = pd.DataFrame(
        {
            "minute_of_day": [480, 485, 490, 495],
            "charging_load_kw": [2.0, 2.0, 2.0, 2.0],
            "high_grid_stress": [1, 1, 1, 1],
        }
    )

    redistributed, shifted, intervals, validation = _redistribute_top_stress(
        df,
        base,
        df["high_grid_stress"] == 1,
    )

    assert shifted == pytest.approx(8.0)
    assert intervals == 4
    assert validation["destination_minutes_used"] > 1
    _assert_energy_conserved(base, redistributed, "unit_test_redistribution")
    _assert_no_negative_loads(redistributed, "unit_test_redistribution")


def test_validation_rejects_unrealistic_peak_increase():
    base = pd.Series([100.0, 50.0, 50.0])
    simulated = pd.Series([130.0, 35.0, 35.0])

    with pytest.raises(AssertionError, match="unrealistically"):
        _assert_peak_not_unrealistic(base, simulated, "unit_test_peak", max_increase_factor=1.2)


def test_validation_rejects_negative_loads():
    simulated = pd.Series([1.0, -0.01, 2.0])

    with pytest.raises(AssertionError, match="negative loads"):
        _assert_no_negative_loads(simulated, "unit_test_negative", tolerance=1e-6)
