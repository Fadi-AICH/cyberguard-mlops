"""Central project paths and constants."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(os.getenv("CYBERGUARD_PROJECT_ROOT", Path(__file__).resolve().parents[2]))
DATA_RAW = PROJECT_ROOT / "data" / "raw" / "network_flows.csv"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed" / "network_flows_validated.csv"
REFERENCE_DATA = PROJECT_ROOT / "data" / "processed" / "reference_window.csv"
CURRENT_DATA = PROJECT_ROOT / "data" / "processed" / "current_window.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "cyberguard_model.joblib"
MODEL_CARD_PATH = MODEL_DIR / "model_card.json"
METRICS_PATH = MODEL_DIR / "metrics.json"
REPORTS_DIR = PROJECT_ROOT / "reports"

TARGET = "is_attack"
CATEGORICAL_FEATURES = ["protocol_type", "service", "flag"]
NUMERIC_FEATURES = [
    "duration",
    "src_bytes",
    "dst_bytes",
    "count",
    "srv_count",
    "serror_rate",
    "same_srv_rate",
    "dst_host_srv_count",
    "dst_host_same_srv_rate",
    "logged_in",
    "urgent",
    "failed_logins",
    "payload_entropy",
    "packet_rate",
]
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES
