# CyberGuard MLOps

CyberGuard MLOps is a cybersecurity-themed machine learning project that implements the full MLOps process requested in `Projet ML.pdf`: data ingestion, validation, feature engineering, model training, experiment tracking, model registry hooks, FastAPI serving, hybrid local inference, Docker deployment, monitoring, Airflow orchestration, CI/CD, and report-ready documentation.

## Quick Start

Use Python 3.11 explicitly on this machine:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m cyberguard_ml.pipeline.ingest_ciciot2023 --rows 3000
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
- SOC Analyst UI: `http://localhost:8501`

The Docker MLflow service uses host port `5001` because Windows may keep a stale local listener on `5000`.

## SOC Analyst UI

The Streamlit SOC workbench is an analyst-facing interface over the same CICIoT2023 artifacts used by the MLOps pipeline. It provides KPI triage, severity distribution, attacker-country ranking, world map, country/server flow diagram, prioritized event queue, live FastAPI scoring, model evidence, drift evidence, and downloadable incident notes.

Run locally:

```powershell
$env:PYTHONPATH='src'
.\.venv\Scripts\streamlit.exe run src\cyberguard_ml\ui\soc_analyst_app.py --server.port 8501
```

Run with Docker Compose:

```powershell
docker compose up -d api soc-ui
```

## Project Theme

The ML problem is binary intrusion detection from real CICIoT2023 network-flow telemetry. CICIoT2023 was released in 2023 by the Canadian Institute for Cybersecurity at the University of New Brunswick and contains IoT traffic from 105 devices with 33 attacks grouped into DDoS, DoS, Recon, Web-based, Brute Force, Spoofing, and Mirai categories.
