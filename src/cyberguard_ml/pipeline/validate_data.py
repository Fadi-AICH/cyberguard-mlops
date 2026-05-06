"""Validate network-flow data before model training."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

import pandas as pd

from cyberguard_ml.settings import DATA_PROCESSED, DATA_RAW, FEATURES, REPORTS_DIR, TARGET


@dataclass(frozen=True)
class ValidationResult:
    """Serializable validation output."""

    passed: bool
    row_count: int
    attack_rate: float
    errors: list[str]
    warnings: list[str]


def validate_frame(frame: pd.DataFrame) -> ValidationResult:
    """Validate schema, ranges, target quality, and common ML leakage risks."""

    errors: list[str] = []
    warnings: list[str] = []
    required = ["flow_id", *FEATURES, "attack_type", TARGET]
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        errors.append(f"Missing required columns: {missing}")

    if frame.empty:
        errors.append("Dataset is empty.")
        return ValidationResult(False, 0, 0.0, errors, warnings)

    if frame["flow_id"].duplicated().any():
        errors.append("Duplicate flow_id values detected.")

    if frame[TARGET].isna().any() or not set(frame[TARGET].dropna().unique()).issubset({0, 1}):
        errors.append("Target column must contain only 0/1 labels.")

    numeric_ranges = {
        "duration": (0, None),
        "src_bytes": (0, None),
        "dst_bytes": (0, None),
        "serror_rate": (0, 1),
        "same_srv_rate": (0, 1),
        "dst_host_same_srv_rate": (0, 1),
        "payload_entropy": (0, 8),
        "packet_rate": (0, None),
    }
    for column, (lower, upper) in numeric_ranges.items():
        if column not in frame:
            continue
        if (frame[column] < lower).any():
            errors.append(f"{column} contains values below {lower}.")
        if upper is not None and (frame[column] > upper).any():
            errors.append(f"{column} contains values above {upper}.")

    attack_rate = float(frame[TARGET].mean())
    if attack_rate < 0.05 or attack_rate > 0.75:
        warnings.append(f"Attack rate {attack_rate:.3f} may create class imbalance risk.")

    if "attack_type" in FEATURES:
        errors.append("Leakage risk: attack_type must not be used as a feature.")

    return ValidationResult(not errors, len(frame), attack_rate, errors, warnings)


def main() -> None:
    """Load raw CSV, validate it, and write the approved processed dataset."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(DATA_RAW)
    result = validate_frame(frame)
    report_path = REPORTS_DIR / "data_validation.json"
    report_path.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
    if not result.passed:
        raise SystemExit(f"Data validation failed. See {report_path}")
    DATA_PROCESSED.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(DATA_PROCESSED, index=False)
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
