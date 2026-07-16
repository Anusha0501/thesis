# Simulation Validation

Simulation validation has not been run in this checkout because processed interval data is not present. Run `python -m src.simulation.smart_charging` after generating `data/processed/interval_features.csv`; the simulation code will populate this report from actual checks without fabricating results.

## Energy conservation checks

Pending an actual simulation run. Load-shifting strategies assert that aggregate load before and after shifting is conserved within floating point tolerance.

## Peak calculations

Pending an actual simulation run. The simulation records baseline and simulated peak demand and raises an assertion if a strategy creates an unrealistic peak increase.

## Load redistribution verification

Pending an actual simulation run. The redistribution strategy records how many off-peak intervals are available and how many are used, ensuring shifted charging is spread instead of stacked into one slot.
