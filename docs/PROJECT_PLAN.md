# CyberGuard MLOps - Work Plan

## Product Vision

Build a modern cybersecurity MLOps platform that predicts whether a network flow is benign or malicious, exposes the model through an API, monitors technical and ML drift signals, and documents all steps for a 20+ page LaTeX report.

## Architecture

1. **Data Sources**: reproducible sample from the real CICIoT2023 dataset.
2. **Data Ingestion**: CLI downloader normalizes CICIoT2023 rows and adds report-only SOC enrichment fields.
3. **Data Validation**: schema checks protect required columns, value ranges, class balance, and leakage risks.
4. **Feature Engineering**: typed preprocessing pipeline separates numeric/categorical features and uses one-hot encoding + scaling.
5. **Training**: compare Logistic Regression, Random Forest, and Gradient Boosting with stratified train/test split.
6. **Tracking**: MLflow logs parameters, metrics, artifacts, and model signature when available.
7. **Registry**: best model artifact is packaged under `models/` and can be registered in MLflow.
8. **Serving**: FastAPI offers `/predict`, `/batch-predict`, `/health`, and `/metrics`.
9. **Hybrid Inference**: local CLI loads the packaged model for offline predictions after DVC checkout.
10. **Monitoring**: Prometheus scrapes API metrics; Grafana visualizes latency, throughput, attack rate, severity distribution, attacker countries, world map, and country/server flows.
11. **Drift**: Evidently report compares reference vs current windows.
12. **Orchestration**: Airflow DAG runs validation, training, evaluation, and drift report generation.
13. **CI/CD**: GitHub Actions runs formatting, linting, type checks, tests, and Docker build.
14. **Report Evidence**: screenshots and commands are tracked in `docs/WORKLOG.md`.

## Research Notes

- MLflow Tracking is used because it records runs, parameters, metrics, artifacts, models, and dataset inputs through a UI and API.
- DVC pipelines are used because `dvc.yaml` can define reproducible stages and track produced data/model artifacts.
- A Great Expectations-style validation suite is generated for formal report evidence; the project also includes a lightweight validator so the pipeline remains runnable in constrained CI/Airflow containers.
- Evidently provides data drift reports that compare reference and current datasets.
- Airflow DAGs model the MLOps workflow as ordered tasks.
- GitHub Actions provides CI/CD automation for Python tests and Docker builds.

## Source Links Checked

- https://mlflow.github.io/mlflow-website/docs/latest/ml/tracking/
- https://dvc.org/doc/user-guide/pipelines
- https://docs.evidentlyai.com/metrics/preset_data_drift
- https://docs.greatexpectations.io/docs/guides/validation/validate_data_overview/
- https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html
- https://docs.github.com/actions/learn-github-actions/workflow-syntax-for-github-actions
- https://www.unb.ca/cic/datasets/iotdataset-2023.html
- https://huggingface.co/datasets/lacg030175/CIC-IoT-2023
