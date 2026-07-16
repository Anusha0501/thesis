# Target Definition

High Grid Stress is defined exactly as:

```text
(total_concurrent_load >= 75th percentile AND power_level == P3)
OR
(total_concurrent_load >= 90th percentile)
```

Sensitivity analysis must be run for 70%, 75%, 80%, 85%, and 90% load-percentile thresholds.

Scientific motivation: the definition links high total concurrent load with high-power P3 charging and top-decile load intervals, consistent with the literature motivation from Muratori (2018), Richardson (2013), and Zhan et al. (2025). This file contains target-design justification only; it contains no performance results or conclusions.
