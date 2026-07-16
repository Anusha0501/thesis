
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.preprocessing.audit_reports import generate_reports
from src.features.feature_engineering import build_interval_dataset
from src.models.train import train_models
from src.evaluation.evaluate import generate_evaluation_artifacts
from src.simulation.smart_charging import run_simulation

if __name__ == "__main__":
    generate_reports()
    build_interval_dataset()
    train_models()
    generate_evaluation_artifacts()
    run_simulation()
