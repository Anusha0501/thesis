
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.models.train import train_models

if __name__ == "__main__":
    train_models()
