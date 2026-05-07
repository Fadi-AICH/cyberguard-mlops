"""Airflow DAG for the CyberGuard MLOps workflow."""

from __future__ import annotations

import subprocess
from datetime import datetime
from os import environ

try:
    from airflow.sdk import DAG, task
except ImportError:  # Airflow 2 compatibility
    from airflow import DAG
    from airflow.decorators import task

PROJECT_DIR = "/opt/airflow/project"


def _run_module(module: str, *args: str) -> None:
    env = {**environ, "PYTHONPATH": f"{PROJECT_DIR}/src"}
    subprocess.run(["python", "-m", module, *args], cwd=PROJECT_DIR, env=env, check=True)


with DAG(
    dag_id="cyberguard_mlops_pipeline",
    description="Validate, train, evaluate, and monitor the CyberGuard intrusion model.",
    start_date=datetime(2026, 5, 1),
    schedule="@daily",
    catchup=False,
    tags=["mlops", "cybersecurity", "intrusion-detection"],
) as dag:

    @task
    def generate_data() -> None:
        _run_module("cyberguard_ml.pipeline.ingest_ciciot2023", "--rows", "3000")

    @task
    def validate_data() -> None:
        _run_module("cyberguard_ml.pipeline.validate_data")

    @task
    def train_model() -> None:
        _run_module("cyberguard_ml.pipeline.train_model")

    @task
    def drift_report() -> None:
        _run_module("cyberguard_ml.monitoring.drift_report")

    @task
    def great_expectations() -> None:
        _run_module("cyberguard_ml.pipeline.great_expectations_check")

    generate_data() >> validate_data() >> great_expectations() >> train_model() >> drift_report()
