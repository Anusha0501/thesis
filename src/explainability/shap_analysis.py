
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

"""SHAP artifact generation. Interpretations are intentionally not written."""
from pathlib import Path
import joblib
import pandas as pd
import shap
import matplotlib.pyplot as plt
from src.models.train import FEATURES
from src.utils.config import load_config


def generate_shap_artifacts(model_name: str = "random_forest", config_path: str = "configs/config.yaml") -> None:
    cfg = load_config(config_path)
    model = joblib.load(Path(cfg["paths"]["models"]) / f"{model_name}.joblib")
    df = pd.read_csv(Path(cfg["paths"]["processed_data"]) / "interval_features.csv")
    X = df[FEATURES].fillna(0).sample(min(cfg["shap"]["n_samples_explanation"], len(df)), random_state=cfg["project"]["random_seed"])
    estimator = model.named_steps.get("model", model)
    explainer = shap.TreeExplainer(estimator) if hasattr(estimator, "feature_importances_") else shap.Explainer(model.predict_proba, X)
    values = explainer(X)
    out = Path(cfg["paths"]["figures"]) / "shap"; out.mkdir(parents=True, exist_ok=True)
    shap.plots.bar(values, show=False); plt.savefig(out / f"{model_name}_bar.png", dpi=200, bbox_inches="tight"); plt.close()
    shap.plots.beeswarm(values, show=False); plt.savefig(out / f"{model_name}_summary.png", dpi=200, bbox_inches="tight"); plt.close()

if __name__ == "__main__":
    generate_shap_artifacts()
