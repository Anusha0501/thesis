from pathlib import Path


def test_fixed_target_definition_configured():
    text = Path("configs/config.yaml").read_text(encoding="utf-8")
    assert 'method: "composite"' in text
    assert "load_percentile_threshold: 75" in text
    assert "high_load_only_pct: 90" in text
    assert "sensitivity_percentiles: [70, 75, 80, 85, 90]" in text
