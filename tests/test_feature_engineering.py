import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")

from src.features.feature_engineering import parse_series_column, minute_from_slot, _vehicle_summary


def test_parse_series_column_identifies_vehicle_power_and_day_type():
    assert parse_series_column("Private car P3 workday") == ("Private car", "P3", "workday")
    assert parse_series_column("SPV_P2_weekend") == ("SPV", "P2", "non_workday")


def test_minute_from_slot_parses_clock_and_fallback():
    assert minute_from_slot("07:35", 0) == 455
    assert minute_from_slot("slot", 3) == 15


def test_vehicle_summary_uses_real_numeric_column():
    df = pd.DataFrame({"vehicle_type": ["Bus", "Bus", "Taxi"], "battery_kwh": [100, 200, 50]})
    result = _vehicle_summary(df, ["battery"])
    assert np.isclose(result["Bus"], 150)
    assert np.isclose(result["Taxi"], 50)
