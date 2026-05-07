# Screenshot Checklist For The Final Report

The old screenshots `01_...` to `13_...` were taken before the CICIoT2023 upgrade. Keep them as backup, but retake the final report evidence with the `v2_` names below.

## Before Capturing

Run these once from the activated venv prompt:

```powershell
Set-Location -LiteralPath 'C:\Users\fadia\OneDrive\Bureau\Projet ML'
$env:PYTHONPATH='src'
.\.venv\Scripts\dvc.exe status
docker compose --profile airflow ps
.\.venv\Scripts\python.exe scripts\replay_ciciot2023_traffic.py --rows 240 --sleep 0.03
```

Use browser zoom around 90-100% and hide unrelated tabs where possible.

## Required V2 Screenshots

1. `screenshots/v2_01_environment_versions.png`
   - Terminal showing:
   ```powershell
   py -3.11 --version
   docker --version
   docker compose version
   .\.venv\Scripts\python.exe --version
   ```

2. `screenshots/v2_02_ciciot2023_ingestion_validation.png`
   - Terminal showing:
   ```powershell
   $env:PYTHONPATH='src'
   .\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.ingest_ciciot2023 --rows 3000 --page-size 100 --offset 0
   .\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.validate_data
   ```
   - Must show `passed: true`, `row_count: 3000`.

3. `screenshots/v2_03_training_metrics_ciciot2023.png`
   - Terminal showing:
   ```powershell
   .\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.train_model
   ```
   - Capture the metrics table where `gradient_boosting` has F1 around `0.941`.

4. `screenshots/v2_04_dvc_pipeline_ciciot2023.png`
   - Terminal showing:
   ```powershell
   .\.venv\Scripts\dvc.exe dag
   .\.venv\Scripts\dvc.exe metrics show
   .\.venv\Scripts\dvc.exe status
   ```
   - Must show the pipeline graph and `Data and pipelines are up to date.`

5. `screenshots/v2_05_quality_tests.png`
   - Terminal showing:
   ```powershell
   .\.venv\Scripts\python.exe -m pytest
   .\.venv\Scripts\python.exe -m ruff check src tests dags scripts
   .\.venv\Scripts\python.exe -m mypy src
   ```

6. `screenshots/v2_06_mlflow_registry_ciciot2023.png`
   - Browser: `http://localhost:5001`
   - Open `cyberguard-intrusion-detection`, then the registered model `CyberGuard-CICIoT2023-Intrusion-Detector`.
   - Capture the experiment run or registry page with model version visible.

7. `screenshots/v2_07_fastapi_docs_ciciot2023.png`
   - Browser: `http://localhost:8000/docs`
   - Show `/health`, `/predict`, `/batch-predict`, and `/metrics`.

8. `screenshots/v2_08_prediction_response.png`
   - In FastAPI docs, open `/predict`, click `Try it out`, execute with the default body, and capture the JSON response.

9. `screenshots/v2_09_docker_services.png`
   - Terminal or Docker Desktop showing:
   ```powershell
   docker compose --profile airflow ps
   ```
   - Must show API, MLflow, Prometheus, Grafana, and Airflow running.

10. `screenshots/v2_10_prometheus_targets.png`
    - Browser: `http://localhost:9090/targets`
    - Show `cyberguard-api` target as UP.

11. `screenshots/v2_11_grafana_soc_dashboard.png`
    - Browser:
    ```text
    http://localhost:3000/d/cyberguard-soc/cyberguard-ciciot2023-soc-command-center?orgId=1&from=now-30m&to=now&refresh=5s
    ```
    - Capture the SOC dashboard with severity donut, top attacker countries, world map, and country/server flow matrix visible.

12. `screenshots/v2_12_evidently_drift_html.png`
    - Open:
    ```powershell
    start reports\evidently_drift_report.html
    ```
    - Capture the Evidently data drift report in the browser.

13. `screenshots/v2_13_soc_threat_report_html.png`
    - Open:
    ```powershell
    start reports\soc_threat_report.html
    ```
    - Capture the offline SOC report tables.

14. `screenshots/v2_14_airflow_dag_success.png`
    - Browser: `http://localhost:8080`
    - Login with user `admin`.
    - Get password:
    ```powershell
    docker exec cyberguard-airflow bash -lc "cat /opt/airflow/simple_auth_manager_passwords.json.generated"
    ```
    - Open `cyberguard_mlops_pipeline`; capture the successful DAG/test run or graph view.

15. `screenshots/v2_15_github_repo_actions.png`
    - Browser: `https://github.com/Fadi-AICH/cyberguard-mlops`
    - Capture repo files and Actions tab.
    - If Actions still show billing/account block, capture that as a documented infrastructure issue, not a project code failure.

## Optional Nice Evidence

- Docker Desktop containers page with all `cyberguard-*` services.
- MLflow run detail page showing params, metrics, and artifacts.
- `reports/great_expectations_validation.json` opened in VS Code.
- `models/model_card.json` opened in VS Code.
