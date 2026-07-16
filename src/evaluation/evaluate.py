
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

"""Evaluation figure generation without interpretation."""
from pathlib import Path
import json
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.calibration import CalibrationDisplay
from sklearn.metrics import PrecisionRecallDisplay, RocCurveDisplay
from src.utils.config import load_config


def generate_evaluation_artifacts(config_path: str = "configs/config.yaml") -> None:
    cfg = load_config(config_path)
    results = Path(cfg["paths"]["results"])
    figs = Path(cfg["paths"]["figures"]); figs.mkdir(parents=True, exist_ok=True)
    preds = pd.read_csv(results / "test_predictions.csv")
    y = preds["y_true"]
    for col in [c for c in preds.columns if c.endswith("_prob")]:
        name = col.removesuffix("_prob")
        RocCurveDisplay.from_predictions(y, preds[col]); plt.title(f"ROC: {name}"); plt.savefig(figs / f"roc_{name}.png", dpi=200); plt.close()
        PrecisionRecallDisplay.from_predictions(y, preds[col]); plt.title(f"PR: {name}"); plt.savefig(figs / f"pr_{name}.png", dpi=200); plt.close()
        CalibrationDisplay.from_predictions(y, preds[col]); plt.title(f"Calibration: {name}"); plt.savefig(figs / f"calibration_{name}.png", dpi=200); plt.close()
    (results / "evaluation_manifest.json").write_text(json.dumps({"generated_from": "test_predictions.csv"}, indent=2), encoding="utf-8")

if __name__ == "__main__":
    generate_evaluation_artifacts()
