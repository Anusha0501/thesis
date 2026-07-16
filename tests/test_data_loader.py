from pathlib import Path

import pytest

pd = pytest.importorskip("pandas")

from src.preprocessing.data_loader import DataLoader


DATA_FILE_KEYS = [
    "charging_load_file",
    "vehicle_count_file",
    "usage_pattern_file",
    "soc_file",
    "ecr_temp_file",
    "ecr_month_file",
    "clusters_file",
    "driving_dist_file",
    "battery_energy_file",
    "energy_ratio_file",
    "charging_freq_file",
    "charger_hist_car",
    "charger_hist_bus",
    "charger_hist_spv",
]


def _write_minimal_csv(path: Path) -> None:
    path.write_text("Unnamed: 0,value\n00:00,1\n00:05,2\n", encoding="utf-8")


def test_load_all_exposes_loaded_dataframes_as_attributes(tmp_path, monkeypatch):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    data_config = {"zenodo_zip": str(raw_dir / "13852045 (1).zip")}
    for key in DATA_FILE_KEYS:
        filename = f"{key}.csv"
        data_config[key] = filename
        _write_minimal_csv(raw_dir / filename)

    cfg = {
        "paths": {
            "raw_data": str(raw_dir),
            "processed_data": str(tmp_path / "processed"),
            "synthetic_data": str(tmp_path / "synthetic"),
            "models": str(tmp_path / "models"),
            "results": str(tmp_path / "metrics"),
            "figures": str(tmp_path / "figures"),
            "reports": str(tmp_path / "reports"),
        },
        "data": data_config,
    }
    monkeypatch.setattr(DataLoader, "extract", lambda self: None)

    store = DataLoader(cfg).load_all()

    assert store.battery_energy is not None
    assert store.energy_ratio is not None
    assert store.charging_freq is not None
    assert store.driving_dist is not None
    assert store["battery_energy"] is store.battery_energy
    assert "time_slot" in store.battery_energy.columns
