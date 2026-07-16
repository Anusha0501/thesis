# Research Feasibility

Status: preliminary, to be verified after dataset audit execution.

The public Zenodo dataset is expected to support the research question at the charging-interval level because it provides aggregated 5-minute charging load and vehicle-count curves. It does not support individual charging-session or VIN-level analysis.

Required files:

- Fig3-2 charging load for interval load features and target construction.
- Fig3-1 vehicle count for concurrent-vehicle features.
- Vehicle distribution files for vehicle-type contextual features where joinable.

Limitations and assumptions must be finalized only after `python src/preprocessing/audit_reports.py` succeeds on the downloaded CSV files.
