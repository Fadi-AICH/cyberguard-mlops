"""Generate a Great Expectations-style validation suite for CICIoT2023 data."""

from __future__ import annotations

import json
from dataclasses import asdict

import pandas as pd

from cyberguard_ml.pipeline.validate_data import validate_frame
from cyberguard_ml.settings import DATA_PROCESSED, FEATURES, REPORTS_DIR, TARGET


def expectation_suite() -> dict[str, object]:
    """Return a portable expectation suite documented for the report."""

    expectations: list[dict[str, object]] = [
        {"expectation_type": "expect_column_values_to_not_be_null", "kwargs": {"column": column}}
        for column in [*FEATURES, TARGET]
    ]
    expectations.extend(
        [
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "time_to_live", "min_value": 0, "max_value": 255},
            },
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {"column": TARGET, "value_set": [0, 1]},
            },
            {
                "expectation_type": "expect_column_values_to_be_in_set",
                "kwargs": {
                    "column": "severity",
                    "value_set": ["low", "medium", "high", "critical"],
                },
            },
        ]
    )
    return {
        "expectation_suite_name": "ciciot2023_cyberguard_suite",
        "meta": {
            "great_expectations_version": "1.x compatible JSON suite",
            "dataset": "CICIoT2023",
        },
        "expectations": expectations,
    }


def main() -> None:
    """Write the expectation suite and a validation result."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(DATA_PROCESSED)
    result = validate_frame(frame)
    suite_path = REPORTS_DIR / "great_expectations_suite.json"
    validation_path = REPORTS_DIR / "great_expectations_validation.json"
    suite_path.write_text(json.dumps(expectation_suite(), indent=2), encoding="utf-8")
    validation_path.write_text(
        json.dumps(
            {
                "success": result.passed,
                "validation_result": asdict(result),
                "suite_path": str(suite_path),
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(validation_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
