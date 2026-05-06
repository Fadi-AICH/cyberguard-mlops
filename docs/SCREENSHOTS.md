# Screenshot Checklist For The Final Report

Capture these after the stack is running and the pipeline has produced artifacts.

## Required Screenshots

1. PDF assignment/process-flow reference: `Projet ML.pdf` page 1.
2. Terminal: `py -3.11 --version`, `docker --version`, and `docker compose version`.
3. Terminal: successful data generation and validation commands.
4. Terminal: model training output with the candidate metrics table.
5. Terminal or UI: `dvc dag` and `dvc metrics show`.
6. MLflow UI: experiment run comparison for `cyberguard-intrusion-detection`.
7. FastAPI docs: `http://127.0.0.1:8000/docs`.
8. API prediction response from `/predict`.
9. Prometheus targets: `http://localhost:9090/targets`.
10. Grafana dashboard: `CyberGuard API Monitoring`.
11. Evidently drift report or fallback JSON report.
12. GitHub Actions CI workflow page after pushing to GitHub.
13. Airflow DAG graph view after deploying the DAG.

## Screenshot Naming Convention

Use:

```text
screenshots/01_environment_versions.png
screenshots/02_data_validation.png
screenshots/03_training_metrics.png
screenshots/04_dvc_pipeline.png
screenshots/05_mlflow_runs.png
screenshots/06_fastapi_docs.png
screenshots/07_prediction_response.png
screenshots/08_prometheus_targets.png
screenshots/09_grafana_dashboard.png
screenshots/10_drift_report.png
screenshots/11_airflow_dag.png
screenshots/12_github_actions.png
```

