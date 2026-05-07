"""Validate network-flow data before model training."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass

import pandas as pd

from cyberguard_ml.settings import (
    DATA_PROCESSED,
    DATA_RAW,
    FEATURES,
    METADATA_COLUMNS,
    REPORTS_DIR,
    TARGET,
)


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
    required = [*METADATA_COLUMNS, *FEATURES, TARGET]
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        errors.append(f"Missing required columns: {missing}")

    if frame.empty:
        errors.append("Dataset is empty.")
        return ValidationResult(False, 0, 0.0, errors, warnings)

    if "flow_id" in frame and frame["flow_id"].duplicated().any():
        errors.append("Duplicate flow_id values detected.")

    if TARGET in frame and (
        frame[TARGET].isna().any() or not set(frame[TARGET].dropna().unique()).issubset({0, 1})
    ):
        errors.append("Target column must contain only 0/1 labels.")

    numeric_ranges = {
        "header_length": (0, None),
        "protocol_type": (0, None),
        "time_to_live": (0, 255),
        "rate": (0, None),
        "fin_flag_number": (0, 1),
        "syn_flag_number": (0, 1),
        "rst_flag_number": (0, 1),
        "psh_flag_number": (0, 1),
        "ack_flag_number": (0, 1),
        "http": (0, 1),
        "https": (0, 1),
        "dns": (0, 1),
        "tcp": (0, 1),
        "udp": (0, 1),
        "icmp": (0, 1),
        "tot_sum": (0, None),
        "min_packet_size": (0, None),
        "max_packet_size": (0, None),
        "avg_packet_size": (0, None),
        "std_packet_size": (0, None),
        "tot_size": (0, None),
        "iat": (0, None),
        "packet_number": (0, None),
        "variance": (0, None),
    }
    for column, (lower, upper) in numeric_ranges.items():
        if column not in frame:
            continue
        series = pd.to_numeric(frame[column], errors="coerce")
        if series.isna().any():
            errors.append(f"{column} contains non-numeric values.")
            continue
        if (series < lower).any():
            errors.append(f"{column} contains values below {lower}.")
        if upper is not None and (series > upper).any():
            errors.append(f"{column} contains values above {upper}.")

    attack_rate = float(frame[TARGET].mean()) if TARGET in frame else 0.0
    if attack_rate < 0.05 or attack_rate > 0.95:
        warnings.append(f"Attack rate {attack_rate:.3f} may create class imbalance risk.")

    leakage_columns = {"attack_type", "attack_class", "severity", "source_country", "source_ip"}
    leaked = sorted(leakage_columns.intersection(FEATURES))
    if leaked:
        errors.append(f"Leakage risk: metadata columns must not be used as features: {leaked}")

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
