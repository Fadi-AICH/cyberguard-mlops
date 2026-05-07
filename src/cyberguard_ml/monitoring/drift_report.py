"""Generate a data drift report for reference vs current flow windows."""

from __future__ import annotations

import json

import pandas as pd

from cyberguard_ml.settings import CURRENT_DATA, REFERENCE_DATA, REPORTS_DIR


def _fallback_report(reference: pd.DataFrame, current: pd.DataFrame) -> dict[str, object]:
    numeric = reference.select_dtypes(include="number").columns.intersection(current.columns)
    drifted: dict[str, float] = {}
    for column in numeric:
        ref_mean = float(reference[column].mean())
        cur_mean = float(current[column].mean())
        denominator = max(abs(ref_mean), 1.0)
        relative_shift = abs(cur_mean - ref_mean) / denominator
        if relative_shift >= 0.1:
            drifted[column] = round(relative_shift, 4)
    return {
        "engine": "fallback_relative_mean_shift",
        "drifted_columns": drifted,
        "drift_detected": bool(drifted),
        "reference_rows": len(reference),
        "current_rows": len(current),
    }


def main() -> None:
    """Write drift summary JSON and Evidently HTML when installed."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    reference = pd.read_csv(REFERENCE_DATA)
    current = pd.read_csv(CURRENT_DATA)
    payload = _fallback_report(reference, current)
    summary_output = REPORTS_DIR / "drift_report.json"
    html_output = REPORTS_DIR / "evidently_drift_report.html"
    try:
        from evidently import Report
        from evidently.presets import DataDriftPreset

        report = Report([DataDriftPreset()])
        snapshot = report.run(current, reference)
        snapshot.save_html(str(html_output))
        if not html_output.exists():
            raise FileNotFoundError(f"Evidently did not create {html_output}")
        payload["engine"] = "evidently_with_json_summary"
        payload["html_report"] = str(html_output)
    except Exception:
        html_output.write_text(
            "<html><body><h1>CyberGuard Drift Report</h1>"
            f"<pre>{json.dumps(payload, indent=2)}</pre></body></html>",
            encoding="utf-8",
        )
        payload["html_report"] = str(html_output)
    summary_output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
