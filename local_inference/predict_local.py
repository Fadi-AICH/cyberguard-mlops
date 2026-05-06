"""Offline hybrid inference entry point for a DVC-checked-out model."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from cyberguard_ml.settings import FEATURES, MODEL_PATH


def predict_file(input_csv: Path) -> list[dict[str, float | int]]:
    """Score a CSV file locally without starting the API."""

    model = joblib.load(MODEL_PATH)
    frame = pd.read_csv(input_csv)
    probabilities = model.predict_proba(frame[FEATURES])[:, 1]
    predictions = (probabilities >= 0.5).astype(int)
    return [
        {"row": int(index), "is_attack": int(pred), "attack_probability": float(prob)}
        for index, (pred, prob) in enumerate(zip(predictions, probabilities, strict=True))
    ]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path)
    args = parser.parse_args()
    print(json.dumps(predict_file(args.input_csv), indent=2))

