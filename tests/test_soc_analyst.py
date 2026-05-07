from __future__ import annotations

import pandas as pd

from cyberguard_ml.settings import FEATURES
from cyberguard_ml.ui.soc_analyst import (
    filter_events,
    flow_matrix,
    incident_markdown,
    selected_payload,
    severity_distribution,
    summarize_dataset,
    top_sources,
)


def _row(
    index: int, severity: str, country: str, server: str, attack: int = 1
) -> dict[str, object]:
    payload: dict[str, object] = {feature: 1.0 for feature in FEATURES}
    payload.update(
        {
            "flow_id": f"flow-{index}",
            "attack_type": "DDoS-HTTP_Flood" if attack else "BenignTraffic",
            "attack_class": "DDoS" if attack else "Benign",
            "severity": severity,
            "source_country": country,
            "source_ip": f"10.0.0.{index}",
            "destination_server": server,
            "is_attack": attack,
            "rate": 100.0 + index,
            "severity_rank": {"critical": 4, "high": 3, "medium": 2, "low": 1}[severity],
        }
    )
    return payload


def test_soc_summary_and_distributions() -> None:
    frame = pd.DataFrame(
        [
            _row(1, "critical", "Russia", "edge"),
            _row(2, "high", "China", "api"),
            _row(3, "low", "Morocco", "hub", attack=0),
        ]
    )

    summary = summarize_dataset(frame)
    severity = severity_distribution(frame)
    sources = top_sources(frame)

    assert summary["rows"] == 3
    assert summary["attack_rows"] == 2
    assert summary["top_attack_class"] == "DDoS"
    assert severity.set_index("severity").loc["critical", "count"] == 1
    assert sources.iloc[0]["attack_count"] == 1


def test_queue_payload_flow_matrix_and_incident_note() -> None:
    frame = pd.DataFrame(
        [
            _row(1, "critical", "Russia", "edge"),
            _row(2, "high", "China", "api"),
            _row(3, "low", "Morocco", "hub", attack=0),
        ]
    )

    filtered = filter_events(frame, severities=["critical"], only_attacks=True)
    matrix = flow_matrix(frame)
    payload = selected_payload(filtered.iloc[0])
    note = incident_markdown(filtered.iloc[0], {"risk_level": "critical", "is_attack": True})

    assert filtered["flow_id"].tolist() == ["flow-1"]
    assert matrix.iloc[0]["count"] == 1
    assert set(FEATURES).issubset(payload)
    assert "flow-1" in note
    assert "critical" in note
