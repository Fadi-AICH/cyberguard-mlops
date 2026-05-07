"""Download a reproducible sample from the real CICIoT2023 dataset."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlencode

import pandas as pd
import requests

from cyberguard_ml.settings import CURRENT_DATA, DATA_RAW, DATA_SOURCE_METADATA, REFERENCE_DATA

DATASET_ID = "lacg030175/CIC-IoT-2023"
DATASET_CONFIG = "random_3way"
DATASET_SPLIT = "train"
DATASET_API = "https://datasets-server.huggingface.co/rows"
SOURCE_URL = "https://www.unb.ca/cic/datasets/iotdataset-2023.html"
HF_URL = "https://huggingface.co/datasets/lacg030175/CIC-IoT-2023"


@dataclass(frozen=True)
class IngestionConfig:
    """Controls the reproducible remote sample."""

    rows: int = 6000
    page_size: int = 100
    offset: int = 0


COLUMN_MAP = {
    "Header_Length": "header_length",
    "Protocol Type": "protocol_type",
    "Time_To_Live": "time_to_live",
    "Rate": "rate",
    "fin_flag_number": "fin_flag_number",
    "syn_flag_number": "syn_flag_number",
    "rst_flag_number": "rst_flag_number",
    "psh_flag_number": "psh_flag_number",
    "ack_flag_number": "ack_flag_number",
    "ack_count": "ack_count",
    "syn_count": "syn_count",
    "fin_count": "fin_count",
    "rst_count": "rst_count",
    "HTTP": "http",
    "HTTPS": "https",
    "DNS": "dns",
    "TCP": "tcp",
    "UDP": "udp",
    "ICMP": "icmp",
    "Tot sum": "tot_sum",
    "Min": "min_packet_size",
    "Max": "max_packet_size",
    "AVG": "avg_packet_size",
    "Std": "std_packet_size",
    "Tot size": "tot_size",
    "IAT": "iat",
    "Number": "packet_number",
    "Variance": "variance",
    "Label": "attack_type",
    "attack_class": "attack_class",
    "label": "is_attack",
}

COUNTRIES = {
    "Benign": ["Morocco", "France", "Spain", "United States"],
    "DDoS": ["China", "Russia", "United States", "Brazil", "India"],
    "DoS": ["Russia", "Germany", "Netherlands", "Turkey"],
    "Recon": ["United States", "China", "India", "Vietnam"],
    "Mirai": ["Japan", "South Korea", "Brazil", "Indonesia"],
    "Spoofing": ["Netherlands", "Russia", "China"],
    "Web-based": ["United States", "France", "India"],
    "BruteForce": ["Russia", "China", "Germany"],
}
SERVERS = ["edge-gateway-01", "camera-vlan-02", "smart-home-hub-03", "iot-dmz-api-04"]
SEVERITY = {
    "Benign": "low",
    "Recon": "medium",
    "Spoofing": "high",
    "BruteForce": "high",
    "Web-based": "high",
    "DoS": "critical",
    "DDoS": "critical",
    "Mirai": "critical",
}


def _fetch_page(offset: int, length: int) -> list[dict[str, Any]]:
    query = urlencode(
        {
            "dataset": DATASET_ID,
            "config": DATASET_CONFIG,
            "split": DATASET_SPLIT,
            "offset": offset,
            "length": length,
        }
    )
    for attempt in range(5):
        response = requests.get(f"{DATASET_API}?{query}", timeout=60)
        if response.status_code == 429:
            time.sleep(8 + attempt * 6)
            continue
        response.raise_for_status()
        payload = response.json()
        return [item["row"] for item in payload["rows"]]
    response.raise_for_status()
    return []


def _ip_for(index: int, attack_class: str) -> str:
    second_octet = 10 + (abs(hash(attack_class)) % 190)
    return f"10.{second_octet}.{(index // 255) % 255}.{index % 255}"


def _enrich(frame: pd.DataFrame) -> pd.DataFrame:
    enriched = frame.copy()
    enriched["flow_id"] = [f"ciciot2023-{idx:07d}" for idx in range(len(enriched))]
    enriched["severity"] = enriched["attack_class"].map(SEVERITY).fillna("medium")
    countries: list[str] = []
    servers: list[str] = []
    ips: list[str] = []
    for idx, attack_class in enumerate(enriched["attack_class"].astype(str)):
        country_options = COUNTRIES.get(attack_class, ["Unknown"])
        countries.append(country_options[idx % len(country_options)])
        servers.append(SERVERS[(idx + len(attack_class)) % len(SERVERS)])
        ips.append(_ip_for(idx, attack_class))
    enriched["source_country"] = countries
    enriched["destination_server"] = servers
    enriched["source_ip"] = ips
    return enriched


def load_ciciot2023_sample(config: IngestionConfig) -> pd.DataFrame:
    """Load and normalize a CICIoT2023 sample through the Hugging Face rows API."""

    rows: list[dict[str, Any]] = []
    offset = config.offset
    while len(rows) < config.rows:
        rows.extend(_fetch_page(offset, min(config.page_size, config.rows - len(rows))))
        offset += config.page_size
    frame = pd.DataFrame(rows).rename(columns=COLUMN_MAP)
    frame = frame[list(COLUMN_MAP.values())]
    frame["attack_class"] = frame["attack_class"].fillna("Benign")
    frame["attack_type"] = frame["attack_type"].fillna("BenignTraffic")
    frame["is_attack"] = frame["is_attack"].astype(int)
    return _enrich(frame)


def write_dataset(config: IngestionConfig) -> None:
    """Persist raw sample and monitoring windows."""

    DATA_RAW.parent.mkdir(parents=True, exist_ok=True)
    REFERENCE_DATA.parent.mkdir(parents=True, exist_ok=True)
    try:
        frame = load_ciciot2023_sample(config)
    except requests.RequestException as exc:
        if not DATA_RAW.exists():
            raise
        print(f"Remote CICIoT2023 fetch failed, using cached sample: {exc}", file=sys.stderr)
        frame = pd.read_csv(DATA_RAW).head(config.rows)
    frame.to_csv(DATA_RAW, index=False)
    split = int(len(frame) * 0.7)
    frame.iloc[:split].to_csv(REFERENCE_DATA, index=False)
    current = frame.iloc[split:].copy()
    current["rate"] = (current["rate"] * 1.18).round(6)
    current["iat"] = (current["iat"] * 0.82).round(6)
    current.to_csv(CURRENT_DATA, index=False)
    DATA_SOURCE_METADATA.write_text(
        json.dumps(
            {
                "dataset": "CICIoT2023",
                "year": 2023,
                "source": SOURCE_URL,
                "sample_mirror": HF_URL,
                "license": "CC BY 4.0 for the Hugging Face mirror; original dataset by CIC/UNB.",
                "config": asdict(config),
                "rows": len(frame),
                "class_distribution": frame["attack_class"].value_counts().to_dict(),
                "binary_distribution": frame["is_attack"].value_counts().to_dict(),
                "note": "Country/server/source_ip fields are deterministic SOC enrichment fields for monitoring visualisation and are not model features.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def parse_args() -> IngestionConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=int, default=3000)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--offset", type=int, default=0)
    args = parser.parse_args()
    return IngestionConfig(rows=args.rows, page_size=args.page_size, offset=args.offset)


if __name__ == "__main__":
    write_dataset(parse_args())
