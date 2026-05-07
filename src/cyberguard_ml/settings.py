"""Central project paths and constants."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(os.getenv("CYBERGUARD_PROJECT_ROOT", Path(__file__).resolve().parents[2]))
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "network_flows.csv"
DATA_SOURCE_METADATA = PROJECT_ROOT / "data" / "raw" / "dataset_metadata.json"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed" / "network_flows_validated.csv"
REFERENCE_DATA = PROJECT_ROOT / "data" / "processed" / "reference_window.csv"
CURRENT_DATA = PROJECT_ROOT / "data" / "processed" / "current_window.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "cyberguard_model.joblib"
MODEL_CARD_PATH = MODEL_DIR / "model_card.json"
METRICS_PATH = MODEL_DIR / "metrics.json"
REPORTS_DIR = PROJECT_ROOT / "reports"

TARGET = "is_attack"
CATEGORICAL_FEATURES: list[str] = []
NUMERIC_FEATURES = [
    "header_length",
    "protocol_type",
    "time_to_live",
    "rate",
    "fin_flag_number",
    "syn_flag_number",
    "rst_flag_number",
    "psh_flag_number",
    "ack_flag_number",
    "ack_count",
    "syn_count",
    "fin_count",
    "rst_count",
    "http",
    "https",
    "dns",
    "tcp",
    "udp",
    "icmp",
    "tot_sum",
    "min_packet_size",
    "max_packet_size",
    "avg_packet_size",
    "std_packet_size",
    "tot_size",
    "iat",
    "packet_number",
    "variance",
]
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
METADATA_COLUMNS = [
    "flow_id",
    "attack_type",
    "attack_class",
    "severity",
    "source_country",
    "source_ip",
    "destination_server",
]
