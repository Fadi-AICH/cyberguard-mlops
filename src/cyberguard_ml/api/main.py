"""FastAPI application for CyberGuard model serving."""

from __future__ import annotations

import time
from typing import Any

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse

from cyberguard_ml.schemas.prediction import NetworkFlow, PredictionResponse
from cyberguard_ml.settings import FEATURES, MODEL_PATH

try:
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
except Exception:  # pragma: no cover - dependency fallback
    CONTENT_TYPE_LATEST = "text/plain; version=0.0.4"
    Counter = Histogram = None  # type: ignore[assignment]


app = FastAPI(
    title="CyberGuard MLOps API",
    description="Real-time network intrusion scoring API with Prometheus metrics.",
    version="0.1.0",
)

REQUEST_COUNT = Counter("cyberguard_predictions_total", "Prediction requests") if Counter else None
ATTACK_COUNT = (
    Counter("cyberguard_predicted_attacks_total", "Predicted attacks") if Counter else None
)
LATENCY = (
    Histogram("cyberguard_prediction_latency_seconds", "Prediction latency") if Histogram else None
)
MODEL: Any | None = None


def load_model() -> Any:
    """Load the packaged model once."""

    global MODEL
    if MODEL is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}")
        MODEL = joblib.load(MODEL_PATH)
    return MODEL


def risk_level(probability: float) -> str:
    """Map probability to an analyst-friendly risk band."""

    if probability >= 0.8:
        return "critical"
    if probability >= 0.55:
        return "high"
    if probability >= 0.32:
        return "medium"
    return "low"


@app.get("/health")
def health() -> dict[str, str]:
    """Return API health and model availability."""

    return {"status": "ok", "model_loaded": str(MODEL_PATH.exists()).lower()}


@app.post("/predict", response_model=PredictionResponse)
def predict(flow: NetworkFlow) -> PredictionResponse:
    """Score a single network flow."""

    start = time.perf_counter()
    if REQUEST_COUNT:
        REQUEST_COUNT.inc()
    try:
        model = load_model()
        frame = pd.DataFrame([flow.model_dump()])[FEATURES]
        probability = float(model.predict_proba(frame)[0, 1])
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    finally:
        if LATENCY:
            LATENCY.observe(time.perf_counter() - start)

    is_attack = probability >= 0.5
    if is_attack and ATTACK_COUNT:
        ATTACK_COUNT.inc()
    return PredictionResponse(
        is_attack=is_attack,
        attack_probability=round(probability, 5),
        risk_level=risk_level(probability),
        model_version="local-joblib-v1",
    )


@app.post("/batch-predict", response_model=list[PredictionResponse])
def batch_predict(flows: list[NetworkFlow]) -> list[PredictionResponse]:
    """Score multiple flows."""

    if len(flows) > 1000:
        raise HTTPException(status_code=413, detail="Batch size cannot exceed 1000 flows.")
    return [predict(flow) for flow in flows]


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    """Expose Prometheus metrics."""

    if not Counter:
        return PlainTextResponse("# prometheus_client is not installed\n", media_type="text/plain")
    return PlainTextResponse(generate_latest().decode("utf-8"), media_type=CONTENT_TYPE_LATEST)
