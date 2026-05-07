"""Replay processed CICIoT2023 rows against the FastAPI service for Grafana screenshots."""

from __future__ import annotations

import argparse
import time

import pandas as pd
import requests

from cyberguard_ml.settings import DATA_PROCESSED, FEATURES


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://localhost:8000/predict")
    parser.add_argument("--rows", type=int, default=240)
    parser.add_argument("--sleep", type=float, default=0.06)
    args = parser.parse_args()

    frame = pd.read_csv(DATA_PROCESSED).head(args.rows)
    columns = [*FEATURES, "source_country", "destination_server", "source_ip"]
    for _, row in frame[columns].iterrows():
        response = requests.post(args.url, json=row.to_dict(), timeout=10)
        response.raise_for_status()
        time.sleep(args.sleep)
    print(f"Replayed {len(frame)} flows to {args.url}")


if __name__ == "__main__":
    main()
