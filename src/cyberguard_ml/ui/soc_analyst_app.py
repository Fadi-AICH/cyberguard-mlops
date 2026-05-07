"""Streamlit SOC analyst interface for CyberGuard."""

from __future__ import annotations

import json
from typing import Any, cast

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from cyberguard_ml.ui.soc_analyst import (
    artifact_summary,
    filter_events,
    flow_matrix,
    incident_markdown,
    load_dataset,
    load_model_metrics,
    selected_payload,
    severity_distribution,
    summarize_dataset,
    top_sources,
)

DEFAULT_API_URL = "http://localhost:8000"
SEVERITY_COLORS = {
    "critical": "#ef4444",
    "high": "#f59e0b",
    "medium": "#3b82f6",
    "low": "#22c55e",
}


@st.cache_data(show_spinner=False)
def cached_dataset() -> pd.DataFrame:
    """Cache the validated dataset between Streamlit reruns."""

    return load_dataset()


@st.cache_data(show_spinner=False)
def cached_metrics() -> pd.DataFrame:
    """Cache model metrics between Streamlit reruns."""

    return load_model_metrics()


@st.cache_data(show_spinner=False)
def cached_artifacts() -> dict[str, Any]:
    """Cache report artifacts between Streamlit reruns."""

    return artifact_summary()


def api_health(api_url: str) -> dict[str, Any]:
    """Return API health information for the sidebar."""

    try:
        response = requests.get(f"{api_url.rstrip('/')}/health", timeout=4)
        response.raise_for_status()
        return {"ok": True, **cast(dict[str, Any], response.json())}
    except requests.RequestException as exc:
        return {"ok": False, "error": str(exc)}


def score_payload(api_url: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Score a selected flow through the deployed FastAPI model."""

    response = requests.post(f"{api_url.rstrip('/')}/predict", json=payload, timeout=30)
    response.raise_for_status()
    return cast(dict[str, Any], response.json())


def apply_theme() -> None:
    """Apply a compact SOC-style visual layer."""

    st.set_page_config(page_title="CyberGuard SOC Analyst", page_icon="CG", layout="wide")
    st.markdown(
        """
        <style>
        .stApp { background: #090d14; color: #e5eefb; }
        [data-testid="stSidebar"] { background: #0f1724; border-right: 1px solid #1f2a3a; }
        h1, h2, h3 { letter-spacing: 0; }
        div[data-testid="stMetric"] {
            background: #111827;
            border: 1px solid #223047;
            padding: 14px 16px;
            border-radius: 8px;
        }
        div[data-testid="stMetricValue"] { color: #34d399; }
        .status-ok { color: #22c55e; font-weight: 700; }
        .status-down { color: #ef4444; font-weight: 700; }
        .small-note { color: #9ca3af; font-size: 0.9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def sankey_figure(matrix: pd.DataFrame) -> go.Figure:
    """Build a country-to-server flow diagram."""

    sources = matrix["source_country"].astype(str).tolist()
    servers = matrix["destination_server"].astype(str).tolist()
    nodes = list(dict.fromkeys([*sources, *servers]))
    index = {node: pos for pos, node in enumerate(nodes)}
    fig = go.Figure(
        data=[
            go.Sankey(
                node={"label": nodes, "pad": 12, "thickness": 14, "color": "#1f2937"},
                link={
                    "source": [index[item] for item in sources],
                    "target": [index[item] for item in servers],
                    "value": matrix["count"].tolist(),
                    "color": "rgba(59, 130, 246, 0.35)",
                },
            )
        ]
    )
    fig.update_layout(
        height=360,
        margin={"l": 10, "r": 10, "t": 18, "b": 10},
        paper_bgcolor="#090d14",
        font={"color": "#e5eefb"},
    )
    return fig


def render_overview(frame: pd.DataFrame) -> None:
    """Render overview charts."""

    sev = severity_distribution(frame)
    countries = top_sources(frame, 12)
    matrix = flow_matrix(frame, 16)

    left, middle, right = st.columns([0.9, 1.1, 1.15])
    with left:
        st.plotly_chart(
            px.pie(
                sev,
                names="severity",
                values="count",
                hole=0.55,
                color="severity",
                color_discrete_map=SEVERITY_COLORS,
                title="Severity Levels",
            ).update_layout(paper_bgcolor="#090d14", plot_bgcolor="#090d14", font_color="#e5eefb"),
            use_container_width=True,
        )
    with middle:
        st.plotly_chart(
            px.bar(
                countries,
                x="attack_count",
                y="source_country",
                orientation="h",
                title="Top Attacker Source Countries",
                color="attack_count",
                color_continuous_scale=["#2563eb", "#f59e0b", "#ef4444"],
            )
            .update_layout(
                paper_bgcolor="#090d14",
                plot_bgcolor="#090d14",
                font_color="#e5eefb",
                yaxis={"categoryorder": "total ascending"},
            )
            .update_coloraxes(showscale=False),
            use_container_width=True,
        )
    with right:
        st.plotly_chart(
            px.choropleth(
                countries,
                locations="source_country",
                locationmode="country names",
                color="attack_count",
                color_continuous_scale=["#1d4ed8", "#f59e0b", "#ef4444"],
                title="World Attack Map",
            )
            .update_layout(
                paper_bgcolor="#090d14",
                geo_bgcolor="#090d14",
                font_color="#e5eefb",
                margin={"l": 0, "r": 0, "t": 45, "b": 0},
            )
            .update_coloraxes(showscale=False),
            use_container_width=True,
        )

    st.plotly_chart(sankey_figure(matrix), use_container_width=True)


def render_queue(filtered: pd.DataFrame) -> pd.Series:
    """Render analyst queue and return selected row."""

    display_columns = [
        "flow_id",
        "severity",
        "attack_class",
        "source_country",
        "source_ip",
        "destination_server",
        "protocol_type",
        "rate",
        "avg_packet_size",
        "variance",
    ]
    st.dataframe(
        filtered[display_columns].head(80),
        use_container_width=True,
        hide_index=True,
    )
    selected_id = st.selectbox("Select flow for investigation", filtered["flow_id"].head(80))
    return filtered[filtered["flow_id"] == selected_id].iloc[0]


def render_evidence(metrics: pd.DataFrame, artifacts: dict[str, Any]) -> None:
    """Render model and validation evidence."""

    left, right = st.columns([1.1, 0.9])
    with left:
        st.subheader("Model Comparison")
        if metrics.empty:
            st.warning("No model metrics found. Run the training stage first.")
        else:
            st.dataframe(metrics, use_container_width=True, hide_index=True)
    with right:
        st.subheader("Validation And Drift")
        validation = artifacts.get("validation", {})
        drift = artifacts.get("drift", {})
        gx = artifacts.get("great_expectations", {})
        st.json(
            {
                "data_validation_passed": validation.get("passed"),
                "validated_rows": validation.get("row_count"),
                "attack_rate": validation.get("attack_rate"),
                "drift_detected": drift.get("drift_detected"),
                "drift_engine": drift.get("engine"),
                "great_expectations_success": gx.get("success"),
            }
        )


def main() -> None:
    """Run the Streamlit app."""

    apply_theme()
    frame = cached_dataset()
    metrics = cached_metrics()
    artifacts = cached_artifacts()

    st.sidebar.title("CyberGuard SOC")
    api_url = st.sidebar.text_input("FastAPI endpoint", DEFAULT_API_URL)
    health = api_health(api_url)
    if health["ok"]:
        st.sidebar.markdown('<span class="status-ok">API online</span>', unsafe_allow_html=True)
    else:
        st.sidebar.markdown('<span class="status-down">API offline</span>', unsafe_allow_html=True)
        st.sidebar.caption(str(health.get("error", ""))[:180])

    countries = st.sidebar.multiselect(
        "Source countries",
        sorted(frame["source_country"].dropna().unique().tolist()),
        default=[],
    )
    severities = st.sidebar.multiselect(
        "Severity",
        ["critical", "high", "medium", "low"],
        default=["critical", "high"],
    )
    servers = st.sidebar.multiselect(
        "Destination servers",
        sorted(frame["destination_server"].dropna().unique().tolist()),
        default=[],
    )
    only_attacks = st.sidebar.toggle("Attack rows only", value=True)

    st.title("CyberGuard SOC Analyst Workbench")
    st.caption(
        "CICIoT2023 intrusion triage with live model scoring, evidence review, and case export."
    )

    summary = summarize_dataset(frame)
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Validated flows", f"{summary['rows']:,}")
    kpi2.metric("Attack rate", f"{summary['attack_rate'] * 100:.1f}%")
    kpi3.metric("Countries", str(summary["countries"]))
    kpi4.metric("Servers", str(summary["servers"]))
    kpi5.metric("Top class", str(summary["top_attack_class"]))

    filtered = filter_events(frame, countries, severities, servers, only_attacks)
    overview_tab, queue_tab, scoring_tab, evidence_tab, export_tab = st.tabs(
        ["SOC Overview", "Analyst Queue", "Live Scoring", "Model Evidence", "Case Export"]
    )

    with overview_tab:
        render_overview(filtered if len(filtered) else frame)

    with queue_tab:
        st.subheader("Prioritized Events")
        if filtered.empty:
            st.warning("No flows match the selected filters.")
            selected = frame.iloc[0]
        else:
            selected = render_queue(filtered)
        st.session_state["selected_flow"] = selected.to_dict()

    selected_flow = pd.Series(st.session_state.get("selected_flow", filtered.iloc[0].to_dict()))
    with scoring_tab:
        st.subheader("Live API Scoring")
        st.dataframe(pd.DataFrame([selected_payload(selected_flow)]), use_container_width=True)
        if st.button("Score Selected Flow", type="primary"):
            try:
                prediction = score_payload(api_url, selected_payload(selected_flow))
                st.session_state["last_prediction"] = prediction
                st.success(
                    f"Risk: {prediction['risk_level']} | probability: {prediction['attack_probability']}"
                )
                st.json(prediction)
            except requests.RequestException as exc:
                st.error(f"Scoring failed: {exc}")

    with evidence_tab:
        render_evidence(metrics, artifacts)
        with st.expander("Model Card"):
            st.json(artifacts.get("model_card", {}))

    with export_tab:
        st.subheader("Case Export")
        prediction = st.session_state.get("last_prediction")
        note = incident_markdown(selected_flow, prediction)
        st.code(note, language="markdown")
        st.download_button(
            "Download Incident Note",
            data=note,
            file_name=f"cyberguard_incident_{selected_flow.get('flow_id', 'selected')}.md",
            mime="text/markdown",
        )
        st.download_button(
            "Download Prediction Payload",
            data=json.dumps(selected_payload(selected_flow), indent=2),
            file_name="cyberguard_prediction_payload.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
