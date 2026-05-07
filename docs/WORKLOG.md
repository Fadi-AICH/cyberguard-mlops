# Projet ML - Working Log

This file records setup decisions, commands, tooling checks, and evidence needed for the final LaTeX report.

## 2026-05-06 - Initial Analysis

### Environment

- Workspace: `C:\Users\fadia\OneDrive\Bureau\Projet ML`
- Assignment PDF: `Projet ML.pdf`
- Default `python` points to Python 3.14.3.
- Required Python 3.11 is installed and will be invoked with `py -3.11`.
- Docker Desktop is available.
- Docker Compose is available.
- Git, Node.js, and npm are available.
- Poppler PDF tools are available through MiKTeX (`pdftotext`, `pdftoppm`).

### Commands Run

```powershell
Get-Location
Get-ChildItem -Force
python --version
py -3.11 --version
docker --version
docker compose version
git --version
node --version
npm --version
Get-Command pdftotext -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
Get-Command pdftoppm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
py -3.11 -m pip --version
py -3.11 -c "import reportlab, pdfplumber, pypdf; print('pdf packages ok')"
py -3.11 -c "import sklearn, pandas, numpy, fastapi, uvicorn, mlflow, dvc, great_expectations; print('mlops packages ok')"
```

### Tool Findings

- Missing globally: `pdfplumber`, `dvc`.
- The project should use an isolated Python 3.11 virtual environment instead of global packages.
- If manual installation is needed later, use:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Evidence To Capture Later

- Screenshot of the running desktop/web UI.
- Screenshot of the API docs at `/docs`.
- Screenshot of MLflow experiment tracking.
- Screenshot of DVC pipeline status or metrics.
- Screenshot of Docker Compose services running.
- Screenshots of model evaluation and monitoring dashboards.

## 2026-05-06 - Project Build Pass 1

### Scope Implemented

- Created a complete CyberGuard MLOps project around binary network intrusion detection.
- Added reproducible CIC/KDD-style data generation.
- Added schema and quality validation with leakage checks.
- Added preprocessing, training, model comparison, model-card export, and MLflow logging.
- Added FastAPI serving with `/health`, `/predict`, `/batch-predict`, and `/metrics`.
- Added hybrid local inference CLI under `local_inference/`.
- Added DVC pipeline metadata in `dvc.yaml`.
- Added Dockerfile and Docker Compose stack for API, MLflow, Prometheus, and Grafana.
- Added Prometheus scrape config and Grafana dashboard provisioning.
- Added Airflow DAG for the full MLOps workflow.
- Added GitHub Actions CI and pre-commit quality configuration.
- Added report planning docs and screenshot checklist.

### Commands Run

```powershell
$env:PYTHONPATH='src'; py -3.11 -m cyberguard_ml.pipeline.generate_data --rows 6000 --seed 42 --attack-rate 0.32
$env:PYTHONPATH='src'; py -3.11 -m cyberguard_ml.pipeline.validate_data
$env:PYTHONPATH='src'; py -3.11 -m cyberguard_ml.pipeline.train_model
$env:PYTHONPATH='src'; py -3.11 -m cyberguard_ml.monitoring.drift_report
$env:PYTHONPATH='src'; py -3.11 -m pytest
py -3.11 -m black src tests
py -3.11 -m isort src tests
py -3.11 -m black --check src tests
py -3.11 -m isort --check-only src tests
$env:PYTHONPATH='src'; py -3.11 -m mypy src
$env:PYTHONPATH='src'; py -3.11 -c "from fastapi.testclient import TestClient; from cyberguard_ml.api.main import app; c=TestClient(app); print(c.get('/health').json()); r=c.post('/predict', json={}); print(r.status_code); print(r.json())"
docker compose config
```

### Validation Results

```json
{
  "passed": true,
  "row_count": 6000,
  "attack_rate": 0.3255,
  "errors": [],
  "warnings": []
}
```

### Model Results

Best candidate by F1-score: `random_forest`.

```json
[
  {
    "name": "logistic_regression",
    "accuracy": 0.906060606060606,
    "precision": 0.8787128712871287,
    "recall": 0.8255813953488372,
    "f1": 0.8513189448441247,
    "roc_auc": 0.9176064802717533
  },
  {
    "name": "random_forest",
    "accuracy": 0.928030303030303,
    "precision": 0.9539295392953929,
    "recall": 0.8186046511627907,
    "f1": 0.8811013767209012,
    "roc_auc": 0.9189077606480273
  },
  {
    "name": "gradient_boosting",
    "accuracy": 0.9204545454545454,
    "precision": 0.9476584022038568,
    "recall": 0.8,
    "f1": 0.8675914249684742,
    "roc_auc": 0.9208309380715965
  }
]
```

### Drift Result

```json
{
  "engine": "fallback_relative_mean_shift",
  "drifted_columns": {
    "packet_rate": 0.2123
  },
  "drift_detected": true,
  "reference_rows": 4200,
  "current_rows": 1800
}
```

### Quality Results

- `pytest`: 7 passed.
- `black --check`: passed.
- `isort --check-only`: passed.
- `mypy src`: passed after clearing orphaned timed-out MyPy processes.
- `ruff`: not installed globally. It is included in `requirements.txt` and `.pre-commit-config.yaml`.
- `docker compose config`: passed.

Install missing project tools with:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### API Smoke Test

```json
{
  "health": {
    "status": "ok",
    "model_loaded": "true"
  },
  "prediction_status": 200,
  "prediction": {
    "is_attack": false,
    "attack_probability": 0.12798,
    "risk_level": "low",
    "model_version": "local-joblib-v1"
  }
}
```

### Local Services Started

API:

```powershell
Set-Location -LiteralPath 'C:\Users\fadia\OneDrive\Bureau\Projet ML'
$env:PYTHONPATH='src'
py -3.11 -m uvicorn cyberguard_ml.api.main:app --host 127.0.0.1 --port 8000
```

MLflow UI:

```powershell
Set-Location -LiteralPath 'C:\Users\fadia\OneDrive\Bureau\Projet ML'
py -3.11 -m mlflow ui --host 127.0.0.1 --port 5000
```

Live URLs verified:

- FastAPI docs: `http://127.0.0.1:8000/docs`
- API health: `http://127.0.0.1:8000/health`
- MLflow UI: `http://127.0.0.1:5000` for local Python, or `http://localhost:5001` for Docker Compose.

### Notes

- DVC is not installed globally, so `dvc repro`, `dvc dag`, and `dvc metrics show` should be run after installing project dependencies in `.venv`.
- Evidently and Great Expectations are also not installed globally. The project includes them in dependencies; the current drift run used the fallback JSON engine.

## 2026-05-06 - Docker MLflow Fix

### Issue

Docker MLflow initially showed only the empty `Default` experiment because MLflow 3 started with an internal `sqlite:///mlflow.db` backend inside the container.

### Fix

- Changed the Docker MLflow service from `mlflow ui` to `mlflow server`.
- Added a persistent SQLite backend store at `/mlflow/mlflow.db`.
- Added proxied artifact serving with `/mlflow/artifacts`.
- Kept host port `5001` because Windows kept a stale listener on `5000`.

### Commands Run

```powershell
docker compose down --remove-orphans
docker compose up -d mlflow
$env:PYTHONPATH='src'
$env:MLFLOW_TRACKING_URI='http://localhost:5001'
$env:PYTHONIOENCODING='utf-8'
.\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.train_model
docker compose up -d --build
docker compose ps
```

### Verified URLs

- FastAPI: `http://localhost:8000/health` returned `200`.
- MLflow: `http://localhost:5001` returned `200`.
- Prometheus: `http://localhost:9090/targets` returned `200`.
- Grafana: `http://localhost:3000` returned `200`.

### MLflow Run

Fresh run URL:

```text
http://localhost:5001/#/experiments/1/runs/e73ee80108bb40469bb33cef008a0399
```

## 2026-05-06 - Grafana Dashboard Upgrade

### Issue

The first Grafana dashboard was too basic for a polished report screenshot.

### Fix

- Rebuilt the provisioned Grafana dashboard as `CyberGuard SOC MLOps Command Center`.
- Added KPI cards, service health, total predictions, attack alerts, attack ratio, latency gauge, traffic trends, latency percentiles, heatmap, runtime footprint, target status, predictions/minute, and alert percentage.
- Added a fixed Prometheus datasource UID for more reliable dashboard provisioning.
- Fixed Docker model path resolution with `CYBERGUARD_PROJECT_ROOT=/app`.
- Rebuilt and recreated the API container.

### Commands Run

```powershell
docker compose restart grafana
docker compose build api
docker compose up -d --force-recreate api prometheus grafana
docker compose ps
```

### Traffic Generation

Synthetic benign and attack requests were sent to `http://localhost:8000/predict` so Grafana panels have visible data.

### Verified URL

```text
http://localhost:3000/d/cyberguard-soc/cyberguard-soc-mlops-command-center?orgId=1&from=now-30m&to=now&refresh=5s
```

## 2026-05-07 - GitHub Repository Publish

### Commands

```powershell
winget install --id GitHub.cli --exact --source winget --accept-package-agreements --accept-source-agreements
gh auth login
git init
git branch -M main
git add -A
git rm --cached -r src\cyberguard_mlops.egg-info screenshots\desktop.ini
git commit -m "Build CyberGuard MLOps project"
gh repo create cyberguard-mlops --private --source . --remote origin --push
```

### Repository

```text
https://github.com/Fadi-AICH/cyberguard-mlops
```

### Notes

- The first workflow startup run did not create jobs, so the CI workflow was updated with manual `workflow_dispatch`.
- GitHub Actions installs `.[dev]` for fast CI checks.
- Local full setup still uses `requirements.txt`, which installs `.[dev,mlops]`.
- The repository was changed from private to public because private runs startup-failed before job creation.
- GitHub then started jobs but blocked execution with: `The job was not started because your account is locked due to a billing issue.`

### GitHub Actions Follow-up

After the GitHub account billing issue is fixed, rerun the workflow:

```powershell
gh workflow run ci.yml --repo Fadi-AICH/cyberguard-mlops
gh run list --repo Fadi-AICH/cyberguard-mlops --limit 5
```

Then capture the Actions tab screenshot:

```text
https://github.com/Fadi-AICH/cyberguard-mlops/actions
```

## 2026-05-07 - CICIoT2023 Real Dataset Upgrade

### Dataset Decision

- Replaced the synthetic generator evidence path with a real public cybersecurity dataset sample: CICIoT2023.
- Official source: `https://www.unb.ca/cic/datasets/iotdataset-2023.html`
- Reproducible sample mirror/API: `https://huggingface.co/datasets/lacg030175/CIC-IoT-2023`
- Dataset year: 2023.
- Use case: binary IoT intrusion detection.
- Important governance note: `source_country`, `source_ip`, `destination_server`, and `severity` are deterministic SOC enrichment fields for monitoring visuals only. They are not model features.

### Major Changes

- Added CICIoT2023 ingestion with retry and cached-sample fallback.
- Updated the model feature schema to CICIoT2023 network-flow fields.
- Updated validation for real numeric ranges, including high packet-size variance values.
- Added Great Expectations-style suite and validation result artifacts.
- Added Evidently HTML drift report generation.
- Registered `CyberGuard-CICIoT2023-Intrusion-Detector` in MLflow Model Registry.
- Rebuilt Grafana as `CyberGuard CICIoT2023 SOC Command Center`.
- Added SOC dashboard panels: world attack map, country/server flow matrix, top attacker/source ranking, severity donut, attack ratio, latency percentiles, API health, and runtime footprint.
- Added replay script to generate live Prometheus/Grafana evidence from real CICIoT2023 rows.
- Added Airflow Docker service and verified a successful DAG test run.

### Commands Run

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.ingest_ciciot2023 --rows 3000 --page-size 100 --offset 0
.\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.validate_data
.\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.great_expectations_check
.\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.train_model
.\.venv\Scripts\python.exe -m cyberguard_ml.monitoring.drift_report
.\.venv\Scripts\python.exe -m cyberguard_ml.monitoring.soc_report
.\.venv\Scripts\dvc.exe repro
.\.venv\Scripts\dvc.exe dag
.\.venv\Scripts\dvc.exe metrics show
.\.venv\Scripts\dvc.exe status
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check src tests dags scripts
.\.venv\Scripts\python.exe -m mypy src
.\.venv\Scripts\python.exe -m black --check src tests dags scripts
.\.venv\Scripts\python.exe -m isort --check-only src tests dags scripts
docker compose build api
docker compose up -d --force-recreate api prometheus grafana
.\.venv\Scripts\python.exe scripts\replay_ciciot2023_traffic.py --rows 240 --sleep 0.03
docker compose --profile airflow up -d airflow
docker exec cyberguard-airflow bash -lc "airflow dags test cyberguard_mlops_pipeline 2026-05-06"
```

### Current Validation Results

```json
{
  "passed": true,
  "row_count": 3000,
  "attack_rate": 0.8433333333333334,
  "errors": [],
  "warnings": []
}
```

### Current Model Results

Best candidate by F1-score: `gradient_boosting`.

```json
[
  {
    "name": "logistic_regression",
    "accuracy": 0.8348484848484848,
    "precision": 1.0,
    "recall": 0.8043087971274686,
    "f1": 0.891542288557214,
    "roc_auc": 0.9381569085426436
  },
  {
    "name": "random_forest",
    "accuracy": 0.8909090909090909,
    "precision": 0.9821073558648111,
    "recall": 0.8868940754039497,
    "f1": 0.9320754716981132,
    "roc_auc": 0.9614090742709731
  },
  {
    "name": "gradient_boosting",
    "accuracy": 0.9030303030303031,
    "precision": 0.9624765478424016,
    "recall": 0.9210053859964094,
    "f1": 0.9412844036697248,
    "roc_auc": 0.9565285597252968
  }
]
```

### Monitoring Results

```json
{
  "engine": "evidently_with_json_summary",
  "drifted_columns": {
    "variance": 0.2883
  },
  "drift_detected": true,
  "reference_rows": 2100,
  "current_rows": 900,
  "html_report": "reports/evidently_drift_report.html"
}
```

### Verified URLs

- FastAPI docs: `http://localhost:8000/docs`
- MLflow UI: `http://localhost:5001`
- Prometheus targets: `http://localhost:9090/targets`
- Grafana SOC dashboard: `http://localhost:3000/d/cyberguard-soc/cyberguard-ciciot2023-soc-command-center?orgId=1&from=now-30m&to=now&refresh=5s`
- Airflow UI: `http://localhost:8080`
- Airflow local login from current container: username `admin`, password stored in `docker exec cyberguard-airflow bash -lc "cat /opt/airflow/simple_auth_manager_passwords.json.generated"`

### Verification Results

- `pytest`: 7 passed.
- `ruff`: passed.
- `mypy`: passed.
- `black --check`: passed.
- `isort --check-only`: passed.
- `dvc status`: data and pipelines are up to date.
- Docker API health: `{"status":"ok","model_loaded":"true"}`.
- Prometheus metrics include `cyberguard_predictions_by_context_total` and `cyberguard_predicted_attacks_by_context_total`.
- Airflow DAG test finished with state `success`.
- Pushed commit `efc1126` to GitHub. Latest Actions run `#7` started but completed as `failure` before exposing steps, consistent with the account-level Actions/billing runner block seen earlier.
- Latest Actions URL: `https://github.com/Fadi-AICH/cyberguard-mlops/actions/runs/25472140055`
