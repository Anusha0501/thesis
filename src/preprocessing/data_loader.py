"""Load, download, extract, and audit Zenodo record 13852045.

The public files are aggregated summary CSVs, not individual charging sessions.
Accordingly, downstream modelling uses charging intervals as the unit of analysis.
"""
from __future__ import annotations

import json
import logging
import urllib.request
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
    """Container for loaded CSV dataframes keyed by logical dataset name."""

    frames: dict[str, pd.DataFrame] = field(default_factory=dict)

    def __getitem__(self, name: str) -> pd.DataFrame:
        return self.frames[name]


class DataLoader:
    """Download, extract, load, and audit the Zenodo dataset."""

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
        self.zip_path = Path(config["data"]["zenodo_zip"])
        self.extract_dir = self.raw_dir / "zenodo_extracted"

    def download(self) -> None:
        """Download the first zip file listed by the Zenodo API if it is absent."""
        if self.zip_path.exists() and self.zip_path.stat().st_size > 0:
            LOGGER.info("Zenodo archive already present: %s", self.zip_path)
            return
        LOGGER.info("Fetching Zenodo metadata: %s", self.config["data"]["zenodo_url"])
        with urllib.request.urlopen(self.config["data"]["zenodo_url"], timeout=60) as response:
            record = json.loads(response.read().decode("utf-8"))
        candidates = [f for f in record.get("files", []) if f.get("key", "").endswith(".zip")]
        if not candidates:
            raise FileNotFoundError("No zip file found in Zenodo record metadata.")
        url = candidates[0]["links"].get("self") or candidates[0]["links"].get("download")
        LOGGER.info("Downloading %s to %s", url, self.zip_path)
        urllib.request.urlretrieve(url, self.zip_path)  # noqa: S310 - trusted DOI-configured source

    def extract(self) -> None:
        """Extract the Zenodo zip archive into data/raw/zenodo_extracted."""
        self.download()
        if self.extract_dir.exists() and any(self.extract_dir.iterdir()):
            LOGGER.info("Archive already extracted: %s", self.extract_dir)
            return
        self.extract_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(self.zip_path, "r") as archive:
            archive.extractall(self.extract_dir)
        LOGGER.info("Extracted %d files", len(list(self.extract_dir.glob("*.csv"))))

    def _path(self, filename: str) -> Path:
        path = self.extract_dir / filename
        if not path.exists():
            raise FileNotFoundError(f"Expected dataset file not found: {path}")
        return path

    def load_all(self) -> ZenodoDataStore:
        """Load all configured CSV files."""
        self.extract()
        frames: dict[str, pd.DataFrame] = {}
        for key in self.REQUIRED_FILE_KEYS:
            name = key.replace("_file", "").replace("charger_hist_", "charger_hist_")
            df = pd.read_csv(self._path(self.config["data"][key]))
            if "Unnamed: 0" in df.columns:
                df = df.rename(columns={"Unnamed: 0": "time_slot"})
            frames[name] = df
            LOGGER.info("Loaded %-24s shape=%s", name, df.shape)
        return ZenodoDataStore(frames)

    @staticmethod
    def audit(store: ZenodoDataStore) -> pd.DataFrame:
        """Return dataset-level shape, null, dtype, and column summaries."""
        rows = []
        for name, df in store.frames.items():
            rows.append({
                "dataset": name,
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
