from __future__ import annotations

from cyberguard_ml.pipeline.generate_data import GeneratorConfig, build_dataset
from cyberguard_ml.pipeline.validate_data import validate_frame


def test_generated_data_passes_validation() -> None:
    frame = build_dataset(GeneratorConfig(rows=300, seed=7, attack_rate=0.3))

    result = validate_frame(frame)

    assert result.passed
    assert result.row_count == 300
    assert 0.15 < result.attack_rate < 0.45


def test_validation_detects_duplicate_flow_id() -> None:
    frame = build_dataset(GeneratorConfig(rows=50, seed=3, attack_rate=0.3))
    frame.loc[1, "flow_id"] = frame.loc[0, "flow_id"]

    result = validate_frame(frame)

    assert not result.passed
    assert any("Duplicate flow_id" in error for error in result.errors)
