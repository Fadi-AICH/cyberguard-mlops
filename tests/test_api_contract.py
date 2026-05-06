from __future__ import annotations

from cyberguard_ml.api.main import risk_level
from cyberguard_ml.schemas.prediction import NetworkFlow


def test_network_flow_defaults_are_valid() -> None:
    flow = NetworkFlow()

    assert flow.protocol_type == "tcp"
    assert flow.payload_entropy <= 8


def test_risk_level_thresholds() -> None:
    assert risk_level(0.1) == "low"
    assert risk_level(0.4) == "medium"
    assert risk_level(0.6) == "high"
    assert risk_level(0.9) == "critical"
