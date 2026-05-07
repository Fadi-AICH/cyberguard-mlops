from __future__ import annotations

from cyberguard_ml.pipeline.validate_data import validate_frame
from cyberguard_ml.settings import FEATURES


def _valid_frame_rows() -> list[dict[str, object]]:
    base = {feature: 0.0 for feature in FEATURES}
    base.update(
        {
            "header_length": 54.0,
            "protocol_type": 6,
            "time_to_live": 64.0,
            "rate": 120.0,
            "tot_sum": 567.0,
            "min_packet_size": 54.0,
            "max_packet_size": 60.0,
            "avg_packet_size": 56.7,
            "tot_size": 56.7,
            "iat": 0.00004,
            "packet_number": 9.5,
            "variance": 0.01,
        }
    )
    rows = []
    for index in range(20):
        row = dict(base)
        row.update(
            {
                "flow_id": f"flow-{index}",
                "attack_type": "BenignTraffic" if index % 2 == 0 else "DDoS-ICMP_Flood",
                "attack_class": "Benign" if index % 2 == 0 else "DDoS",
                "severity": "low" if index % 2 == 0 else "critical",
                "source_country": "Morocco" if index % 2 == 0 else "China",
                "source_ip": f"10.0.0.{index}",
                "destination_server": "edge-gateway-01",
                "is_attack": index % 2,
            }
        )
        rows.append(row)
    return rows


def test_generated_data_passes_validation() -> None:
    import pandas as pd

    frame = pd.DataFrame(_valid_frame_rows())

    result = validate_frame(frame)

    assert result.passed
    assert result.row_count == 20
    assert result.attack_rate == 0.5


def test_validation_detects_duplicate_flow_id() -> None:
    import pandas as pd

    frame = pd.DataFrame(_valid_frame_rows())
    frame.loc[1, "flow_id"] = frame.loc[0, "flow_id"]

    result = validate_frame(frame)

    assert not result.passed
    assert any("Duplicate flow_id" in error for error in result.errors)
