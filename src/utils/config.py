"""Configuration helpers."""
from pathlib import Path
from typing import Any
import yaml


def load_config(config_path: str | Path = "configs/config.yaml") -> dict[str, Any]:
    """Load YAML project configuration."""
    with Path(config_path).open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def ensure_directories(config: dict[str, Any]) -> None:
    """Create configured output directories."""
    for key in ["raw_data", "processed_data", "synthetic_data", "models", "results", "figures", "reports"]:
        Path(config["paths"][key]).mkdir(parents=True, exist_ok=True)
