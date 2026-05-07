"""Reusable analytics for the Streamlit SOC analyst interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

import pandas as pd

from cyberguard_ml.settings import (
    DATA_PROCESSED,
    FEATURES,
    METRICS_PATH,
    MODEL_CARD_PATH,
    REPORTS_DIR,
)

SEVERITY_ORDER = ["critical", "high", "medium", "low"]
SEVERITY_WEIGHT = {"critical": 4, "high": 3, "medium": 2, "low": 1}


def load_dataset(path: Path = DATA_PROCESSED) -> pd.DataFrame:
    """Load the validated CICIoT2023 sample for analyst exploration."""

    if not path.exists():
        raise FileNotFoundError(f"Validated dataset not found at {path}")
    frame = pd.read_csv(path)
    frame["severity_rank"] = frame["severity"].map(SEVERITY_WEIGHT).fillna(0).astype(int)
    return frame


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON artifact and return an empty payload if it is absent."""

    if not path.exists():
        return {}
    return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))


def load_model_metrics(path: Path = METRICS_PATH) -> pd.DataFrame:
    """Load model comparison metrics as a dataframe."""

    payload = load_json(path)
    if not payload:
        return pd.DataFrame()
    return pd.DataFrame(payload).sort_values("f1", ascending=False)


def summarize_dataset(frame: pd.DataFrame) -> dict[str, float | int | str]:
    """Return headline SOC and dataset KPIs."""

    attack_rows = int(frame["is_attack"].sum())
    top_country = str(frame["source_country"].value_counts().idxmax())
    top_server = str(frame["destination_server"].value_counts().idxmax())
    top_attack_class = str(
        frame.loc[frame["is_attack"] == 1, "attack_class"].value_counts().idxmax()
    )
    return {
        "rows": int(len(frame)),
        "attack_rows": attack_rows,
        "attack_rate": round(float(frame["is_attack"].mean()), 4),
        "countries": int(frame["source_country"].nunique()),
        "servers": int(frame["destination_server"].nunique()),
        "top_country": top_country,
        "top_server": top_server,
        "top_attack_class": top_attack_class,
    }


def filter_events(
    frame: pd.DataFrame,
    countries: list[str] | None = None,
    severities: list[str] | None = None,
    servers: list[str] | None = None,
    only_attacks: bool = True,
) -> pd.DataFrame:
    """Filter events for the analyst queue."""

    filtered = frame.copy()
    if only_attacks:
        filtered = filtered[filtered["is_attack"] == 1]
    if countries:
        filtered = filtered[filtered["source_country"].isin(countries)]
    if severities:
        filtered = filtered[filtered["severity"].isin(severities)]
    if servers:
        filtered = filtered[filtered["destination_server"].isin(servers)]
    return filtered.sort_values(["severity_rank", "rate"], ascending=[False, False])


def severity_distribution(frame: pd.DataFrame) -> pd.DataFrame:
    """Count attack events by severity in stable display order."""

    attacks = frame[frame["is_attack"] == 1]
    counts = attacks["severity"].value_counts().reindex(SEVERITY_ORDER, fill_value=0)
    return counts.rename_axis("severity").reset_index(name="count")


def top_sources(frame: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Return the top attacker countries."""

    attacks = frame[frame["is_attack"] == 1]
    return (
        attacks["source_country"]
        .value_counts()
        .head(limit)
        .rename_axis("source_country")
        .reset_index(name="attack_count")
    )


def flow_matrix(frame: pd.DataFrame, limit: int = 15) -> pd.DataFrame:
    """Aggregate country-to-server attack flows for tables and diagrams."""

    attacks = frame[frame["is_attack"] == 1]
    return (
        attacks.groupby(["source_country", "destination_server", "severity"])
        .size()
        .reset_index(name="count")
        .sort_values(["count", "severity"], ascending=[False, True])
        .head(limit)
    )


def selected_payload(row: pd.Series) -> dict[str, Any]:
    """Build a FastAPI prediction payload from a selected dataset row."""

    fields = [*FEATURES, "source_country", "destination_server", "source_ip"]
    return cast(dict[str, Any], row[fields].to_dict())


def incident_markdown(row: pd.Series, prediction: dict[str, Any] | None = None) -> str:
    """Create a downloadable incident note for the selected flow."""

    lines = [
        "# CyberGuard SOC Incident Note",
        "",
        f"- Flow ID: `{row.get('flow_id', 'unknown')}`",
        f"- Source: `{row.get('source_ip', 'unknown')}` / {row.get('source_country', 'unknown')}",
        f"- Destination server: `{row.get('destination_server', 'unknown')}`",
        f"- Dataset attack class: `{row.get('attack_class', 'unknown')}`",
        f"- Dataset severity: `{row.get('severity', 'unknown')}`",
        f"- Packet rate: `{row.get('rate', 0):.4f}`",
        f"- Protocol type: `{row.get('protocol_type', 'unknown')}`",
    ]
    if prediction:
        lines.extend(
            [
                "",
                "## Model Scoring",
                f"- Predicted attack: `{prediction.get('is_attack')}`",
                f"- Attack probability: `{prediction.get('attack_probability')}`",
                f"- Risk level: `{prediction.get('risk_level')}`",
                f"- Model version: `{prediction.get('model_version')}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Analyst Decision",
            "- Review correlated telemetry in Grafana.",
            "- Escalate if risk is high or critical.",
            "- Use this note as report evidence for the feedback/governance phase.",
        ]
    )
    return "\n".join(lines)


def artifact_summary() -> dict[str, Any]:
    """Load key report artifacts for the evidence panel."""

    return {
        "model_card": load_json(MODEL_CARD_PATH),
        "metrics": load_json(METRICS_PATH),
        "validation": load_json(REPORTS_DIR / "data_validation.json"),
        "drift": load_json(REPORTS_DIR / "drift_report.json"),
        "great_expectations": load_json(REPORTS_DIR / "great_expectations_validation.json"),
    }
