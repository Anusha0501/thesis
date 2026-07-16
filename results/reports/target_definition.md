# Target Definition

High Grid Stress is defined exactly as: `(total_concurrent_load >= 75th percentile AND power_level == P3) OR (total_concurrent_load >= 90th percentile)`. Sensitivity analysis is implemented for 70%, 75%, 80%, 85%, and 90%. The definition is motivated by high-power charging/grid-congestion literature (Muratori 2018; Richardson 2013) and the dataset context of Zhan et al. (2025). No alternative target is introduced.
