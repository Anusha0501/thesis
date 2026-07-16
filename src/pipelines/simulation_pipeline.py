
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.simulation.smart_charging import run_simulation

if __name__ == "__main__":
    run_simulation()
