"""Local loading, extraction, and audit utilities for Zenodo record 13852045.

The thesis workflow must use local repository files only.  This loader therefore never
contacts Zenodo; it searches ``data/raw`` for the configured archive, common local
archive variants such as ``13852045 (1).zip``, or already-extracted CSV files.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


import logging
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd

from src.utils.config import ensure_directories, load_config

LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


@dataclass
class ZenodoDataStore:
    """Container for all loaded Zenodo CSV dataframes.

    The ``frames`` dictionary supports programmatic access, while explicit
    attributes preserve the original project API used by notebooks and scripts
    (for example ``store.battery_energy``).
    """

    frames: dict[str, pd.DataFrame] = field(default_factory=dict)
    source_paths: dict[str, Path] = field(default_factory=dict)
    charging_load: pd.DataFrame | None = None
    vehicle_count: pd.DataFrame | None = None
    usage_pattern: pd.DataFrame | None = None
    soc: pd.DataFrame | None = None
    ecr_temp: pd.DataFrame | None = None
    ecr_month: pd.DataFrame | None = None
    clusters: pd.DataFrame | None = None
    driving_dist: pd.DataFrame | None = None
    battery_energy: pd.DataFrame | None = None
    energy_ratio: pd.DataFrame | None = None
    charging_freq: pd.DataFrame | None = None
    charger_hist_car: pd.DataFrame | None = None
    charger_hist_bus: pd.DataFrame | None = None
    charger_hist_spv: pd.DataFrame | None = None

    def __post_init__(self) -> None:
        """Populate explicit dataframe attributes from ``frames`` when present."""
        for name, frame in self.frames.items():
            if hasattr(self, name):
                setattr(self, name, frame)

    def __getitem__(self, name: str) -> pd.DataFrame:
        return self.frames[name]

    def set_frame(self, name: str, frame: pd.DataFrame, source_path: Path) -> None:
        """Store a dataframe in both dictionary and attribute form."""
        self.frames[name] = frame
        self.source_paths[name] = source_path
        if hasattr(self, name):
            setattr(self, name, frame)


class DataLoader:
    """Extract, discover, load, and audit the local Zenodo dataset files."""

    REQUIRED_FILE_KEYS = [
        "charging_load_file", "vehicle_count_file", "usage_pattern_file", "soc_file",
        "ecr_temp_file", "ecr_month_file", "clusters_file", "driving_dist_file",
        "battery_energy_file", "energy_ratio_file", "charging_freq_file", "charger_hist_car",
        "charger_hist_bus", "charger_hist_spv",
    ]

    def __init__(self, config: dict[str, Any]):
        self.config = config
        ensure_directories(config)
        self.raw_dir = Path(config["paths"]["raw_data"])
        self.zip_path = Path(config["data"].get("zenodo_zip", "data/raw/13852045 (1).zip"))
        self.extract_dir = self.raw_dir / "zenodo_extracted"

    def _candidate_archives(self) -> list[Path]:
        configured = self.zip_path
        candidates = [configured]
        candidates.extend(sorted(self.raw_dir.glob("13852045*.zip")))
        candidates.extend(sorted(self.raw_dir.glob("*.zip")))
        seen: set[Path] = set()
        return [p for p in candidates if not (p in seen or seen.add(p))]

    def _resolve_archive(self) -> Path | None:
        for path in self._candidate_archives():
            if path.exists() and path.stat().st_size > 0:
                return path
        return None

    def extract(self) -> None:
        """Extract the local archive if present; otherwise use existing CSV files."""
        if self.extract_dir.exists() and any(self.extract_dir.glob("**/*.csv")):
            LOGGER.info("Using already extracted CSV files under %s", self.extract_dir)
            return
        archive_path = self._resolve_archive()
        if archive_path is None:
            if any(self.raw_dir.glob("**/*.csv")):
                LOGGER.info("No archive found; using CSV files already present under %s", self.raw_dir)
                return
            raise FileNotFoundError(
                "No local Zenodo archive or extracted CSV files found. Expected a file like "
                "data/raw/13852045 (1).zip or extracted CSVs under data/raw/."
            )
        self.extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(self.extract_dir)
        LOGGER.info("Extracted %s to %s (%d CSV files)", archive_path, self.extract_dir, len(list(self.extract_dir.glob("**/*.csv"))))

    def _path(self, filename: str) -> Path:
        search_roots = [self.extract_dir, self.raw_dir]
        for root in search_roots:
            direct = root / filename
            if direct.exists():
                return direct
            matches = list(root.glob(f"**/{filename}"))
            if matches:
                return matches[0]
        raise FileNotFoundError(f"Expected dataset file not found locally: {filename}")

    def load_all(self) -> ZenodoDataStore:
        """Load all configured CSV files from local storage."""
        self.extract()
        store = ZenodoDataStore()
        for key in self.REQUIRED_FILE_KEYS:
            name = key.replace("_file", "")
            path = self._path(self.config["data"][key])
            df = pd.read_csv(path)
            if "Unnamed: 0" in df.columns:
                df = df.rename(columns={"Unnamed: 0": "time_slot"})
            store.set_frame(name, df, path)
            LOGGER.info("Loaded %-24s shape=%s from %s", name, df.shape, path)
        return store

    @staticmethod
    def audit(store: ZenodoDataStore) -> pd.DataFrame:
        """Return dataset-level shape, null, dtype, and column summaries."""
        rows = []
        for name, df in store.frames.items():
            rows.append({
                "dataset": name,
                "source_path": str(store.source_paths.get(name, "")),
                "rows": df.shape[0],
                "columns": df.shape[1],
                "null_cells": int(df.isna().sum().sum()),
                "null_pct": round(float(df.isna().mean().mean() * 100), 4),
                "column_names": "; ".join(map(str, df.columns)),
                "dtypes": "; ".join(f"{c}:{t}" for c, t in df.dtypes.items()),
            })
        return pd.DataFrame(rows)


if __name__ == "__main__":
    cfg = load_config()
    loader = DataLoader(cfg)
    data = loader.load_all()
    print(loader.audit(data).to_string(index=False))
