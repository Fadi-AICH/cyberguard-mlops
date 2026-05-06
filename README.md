# CyberGuard MLOps

CyberGuard MLOps is a cybersecurity-themed machine learning project that implements the full MLOps process requested in `Projet ML.pdf`: data ingestion, validation, feature engineering, model training, experiment tracking, model registry hooks, FastAPI serving, hybrid local inference, Docker deployment, monitoring, Airflow orchestration, CI/CD, and report-ready documentation.

## Quick Start

Use Python 3.11 explicitly on this machine:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.generate_data --rows 6000
.\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.validate_data
.\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.train_model
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m uvicorn cyberguard_ml.api.main:app --reload
```

Open:

- API: `http://127.0.0.1:8000`
- API docs: `http://127.0.0.1:8000/docs`
- Metrics: `http://127.0.0.1:8000/metrics`

## Docker Stack

```powershell
docker compose up --build
```

Services:

- FastAPI: `http://localhost:8000`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (`admin` / `admin`)
- MLflow UI: `http://localhost:5001`

The Docker MLflow service uses host port `5001` because Windows may keep a stale local listener on `5000`.

## Project Theme

The ML problem is binary intrusion detection from network-flow telemetry. The generated data uses CIC/KDD-style fields such as protocol, service, TCP flags, byte counts, connection rates, error rates, entropy, and login anomalies. This keeps the project reproducible while matching a realistic cyber-defense scenario.
