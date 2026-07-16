# Research Feasibility

## Feasibility decision

The dataset supports the research question at the **charging-interval** level because it contains aggregated 5-minute charging load and vehicle-count curves by vehicle/power categories. It does not support individual-session or vehicle-trajectory claims.

## Required files

- Fig3-2 charging load: target/load features.
- Fig3-1 vehicle counts: concurrent-count features.
- Vehicle distribution files (Fig1b, Fig1e, Fig1f-1, Fig1f-2): vehicle-type context features where joinable.

## Limitations

- No VIN/session records.
- Simulation operates on interval load redistribution, not real charger dispatch.
- Conclusions must remain empty until pipelines are executed and outputs reviewed.
