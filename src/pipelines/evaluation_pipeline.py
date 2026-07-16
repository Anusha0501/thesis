
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.evaluation.evaluate import generate_evaluation_artifacts

if __name__ == "__main__":
    generate_evaluation_artifacts()
