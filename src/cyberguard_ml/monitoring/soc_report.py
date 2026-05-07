"""Create an offline SOC visualization report from processed CICIoT2023 data."""

from __future__ import annotations

from html import escape
from typing import cast

import pandas as pd

from cyberguard_ml.settings import DATA_PROCESSED, REPORTS_DIR


def _table_html(frame: pd.DataFrame) -> str:
    return cast(str, frame.to_html(index=False, classes="table", border=0))


def main() -> None:
    """Write a compact HTML report with country, server, and severity views."""

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    frame = pd.read_csv(DATA_PROCESSED)
    attacks = frame[frame["is_attack"] == 1]
    severity = attacks["severity"].value_counts().rename_axis("severity").reset_index(name="count")
    country = (
        attacks["source_country"]
        .value_counts()
        .head(10)
        .rename_axis("country")
        .reset_index(name="count")
    )
    flow = (
        attacks.groupby(["source_country", "destination_server", "severity"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(15)
    )
    attack_types = (
        attacks["attack_class"].value_counts().rename_axis("attack_class").reset_index(name="count")
    )

    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>CyberGuard CICIoT2023 SOC Report</title>
  <style>
    body {{ margin: 0; background: #0b1017; color: #e8eef8; font-family: Inter, Segoe UI, Arial, sans-serif; }}
    header {{ padding: 28px 36px; border-bottom: 1px solid #223047; background: #111827; }}
    h1 {{ margin: 0; font-size: 30px; }}
    h2 {{ margin: 0 0 14px; font-size: 18px; color: #93c5fd; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; padding: 24px 36px; }}
    .panel {{ background: #121a26; border: 1px solid #26364f; border-radius: 8px; padding: 18px; box-shadow: 0 10px 28px rgba(0,0,0,.24); }}
    .kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; padding: 20px 36px 0; }}
    .kpi {{ background: #162033; border: 1px solid #2f4363; border-radius: 8px; padding: 16px; }}
    .label {{ color: #9ca3af; font-size: 12px; text-transform: uppercase; }}
    .value {{ font-size: 30px; color: #34d399; font-weight: 700; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid #243044; text-align: left; }}
    th {{ color: #93c5fd; font-size: 12px; text-transform: uppercase; }}
    .bar {{ height: 10px; background: linear-gradient(90deg, #22c55e, #f59e0b, #ef4444); border-radius: 999px; }}
  </style>
</head>
<body>
  <header>
    <h1>CyberGuard CICIoT2023 SOC Report</h1>
    <p>Offline visualization for report evidence: severity levels, top source countries, attack classes, and country/server flow matrix.</p>
  </header>
  <section class="kpis">
    <div class="kpi"><div class="label">Rows</div><div class="value">{len(frame)}</div></div>
    <div class="kpi"><div class="label">Attack Rows</div><div class="value">{len(attacks)}</div></div>
    <div class="kpi"><div class="label">Countries</div><div class="value">{attacks['source_country'].nunique()}</div></div>
    <div class="kpi"><div class="label">Servers</div><div class="value">{attacks['destination_server'].nunique()}</div></div>
  </section>
  <main class="grid">
    <section class="panel"><h2>Severity Levels</h2>{_table_html(severity)}<div class="bar"></div></section>
    <section class="panel"><h2>Top Source Countries</h2>{_table_html(country)}</section>
    <section class="panel"><h2>Attack Classes</h2>{_table_html(attack_types)}</section>
    <section class="panel"><h2>Country / Server Flow Matrix</h2>{_table_html(flow)}</section>
  </main>
  <footer style="padding: 20px 36px; color: #9ca3af;">Dataset: {escape('CICIoT2023, Canadian Institute for Cybersecurity / University of New Brunswick')}</footer>
</body>
</html>
"""
    output = REPORTS_DIR / "soc_threat_report.html"
    output.write_text(html, encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
