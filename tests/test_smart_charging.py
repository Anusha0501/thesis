import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline

from src.models.train import _temporal_cv_fold_diagnostics, _time_series_cv_scores
from src.simulation.smart_charging import (
    _assert_energy_conserved,
    _assert_no_negative_loads,
    _assert_peak_not_unrealistic,
    _delay_p3_peak,
    _redistribute_top_stress,
    _shift_load,
)


def _base_curve(value: float = 10.0) -> pd.Series:
    return pd.Series(value, index=range(0, 1440, 5), dtype=float)




def _peaked_curve() -> pd.Series:
    curve = pd.Series(5.0, index=range(0, 1440, 5), dtype=float)
    for minute in [480, 485, 490, 495]:
        curve.loc[minute] = 20.0
    return curve


def test_shift_load_subtracts_source_and_adds_destination_with_energy_conserved():
    base = _base_curve()

    shifted = _shift_load(base, source_minute=60, destination_minute=120, load_kw=4.5)

    assert shifted.loc[60] == pytest.approx(base.loc[60] - 4.5)
    assert shifted.loc[120] == pytest.approx(base.loc[120] + 4.5)
    _assert_energy_conserved(base, shifted, "unit_test_shift")


def test_redistribution_spreads_load_across_multiple_off_peak_intervals():
    base = _peaked_curve()
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


def test_temporal_cv_diagnostics_flags_one_class_folds():
    y = pd.Series([0, 0, 0, 0, 1, 1, 1, 1])
    diagnostics = _temporal_cv_fold_diagnostics(y, TimeSeriesSplit(n_splits=3))

    assert any(fold["status"] == "insufficient_class_variation" for fold in diagnostics)
    assert all("test_class_distribution" in fold for fold in diagnostics)


def test_time_series_cv_scores_skip_one_class_metric_folds():
    X = pd.DataFrame({"x": range(12)})
    y = pd.Series([0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1])
    estimator = Pipeline([("model", RandomForestClassifier(n_estimators=5, random_state=0))])

    scores, fold_results = _time_series_cv_scores(estimator, X, y, TimeSeriesSplit(n_splits=3))

    skipped = [fold for fold in fold_results if fold["status"] == "insufficient_class_variation"]
    assert skipped
    assert any(value is None for value in scores["test_roc_auc"])
    assert any(value is None for value in scores["test_average_precision"])


def test_delay_p3_peak_does_not_exceed_baseline_peak_and_conserves_energy():
    base = _peaked_curve()
    df = pd.DataFrame(
        {
            "minute_of_day": [480, 485, 490, 495],
            "hour_of_day": [8, 8, 8, 8],
            "power_level": ["P3", "P3", "P3", "P3"],
            "charging_load_kw": [5.0, 5.0, 5.0, 5.0],
        }
    )

    delayed, _, _, validation = _delay_p3_peak(df, base)

    assert delayed.max() <= base.max()
    _assert_energy_conserved(base, delayed, "unit_test_delay")
    _assert_no_negative_loads(delayed, "unit_test_delay")
    assert validation["destination_minutes_used"] > 1


def test_redistribute_top_stress_does_not_exceed_baseline_peak_and_spreads_load():
    base = _peaked_curve()
    df = pd.DataFrame(
        {
            "minute_of_day": [480, 485, 490, 495],
            "charging_load_kw": [5.0, 5.0, 5.0, 5.0],
            "high_grid_stress": [1, 1, 1, 1],
        }
    )

    redistributed, _, _, validation = _redistribute_top_stress(df, base, df["high_grid_stress"] == 1)

    assert redistributed.max() <= base.max()
    _assert_energy_conserved(base, redistributed, "unit_test_redistribution_peak")
    _assert_no_negative_loads(redistributed, "unit_test_redistribution_peak")
    assert validation["destination_minutes_used"] > 1
