"""Train, evaluate, and package the CyberGuard intrusion-detection model."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from cyberguard_ml.settings import (
    CATEGORICAL_FEATURES,
    DATA_PROCESSED,
    FEATURES,
    METRICS_PATH,
    MODEL_CARD_PATH,
    MODEL_DIR,
    MODEL_PATH,
    NUMERIC_FEATURES,
    TARGET,
)


@dataclass(frozen=True)
class ModelResult:
    """Evaluation summary for one candidate model."""

    name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float


def build_preprocessor() -> ColumnTransformer:
    """Create the feature preprocessing graph."""

    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), NUMERIC_FEATURES),
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
        ]
    )


def candidate_models() -> dict[str, Any]:
    """Return candidate estimators to compare."""

    return {
        "logistic_regression": LogisticRegression(max_iter=1200, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=180,
            max_depth=12,
            min_samples_leaf=3,
            class_weight="balanced_subsample",
            random_state=42,
            n_jobs=-1,
        ),
        "gradient_boosting": GradientBoostingClassifier(random_state=42),
    }


def _score_model(
    name: str, pipeline: Pipeline, x_test: pd.DataFrame, y_test: pd.Series
) -> ModelResult:
    predictions = pipeline.predict(x_test)
    probabilities = pipeline.predict_proba(x_test)[:, 1]
    return ModelResult(
        name=name,
        accuracy=float(accuracy_score(y_test, predictions)),
        precision=float(precision_score(y_test, predictions)),
        recall=float(recall_score(y_test, predictions)),
        f1=float(f1_score(y_test, predictions)),
        roc_auc=float(roc_auc_score(y_test, probabilities)),
    )


def train() -> tuple[Pipeline, list[ModelResult]]:
    """Train all candidates and return the best F1 model."""

    frame = pd.read_csv(DATA_PROCESSED)
    x = frame[FEATURES]
    y = frame[TARGET]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.22, random_state=42, stratify=y
    )

    results: list[ModelResult] = []
    fitted: dict[str, Pipeline] = {}
    for name, estimator in candidate_models().items():
        pipeline = Pipeline([("preprocess", build_preprocessor()), ("model", estimator)])
        pipeline.fit(x_train, y_train)
        fitted[name] = pipeline
        results.append(_score_model(name, pipeline, x_test, y_test))

    best_result = max(results, key=lambda item: (item.f1, item.recall, item.roc_auc))
    best_model = fitted[best_result.name]
    return best_model, results


def maybe_log_mlflow(results: list[ModelResult], best_model: Pipeline) -> None:
    """Log metrics and model artifacts to MLflow when it is installed."""

    try:
        import mlflow.sklearn

        import mlflow
    except Exception:
        return

    mlflow.set_experiment("cyberguard-intrusion-detection")
    best_result = max(results, key=lambda item: item.f1)
    with mlflow.start_run(run_name=f"best-{best_result.name}"):
        mlflow.log_param("problem_type", "binary_intrusion_detection")
        mlflow.log_param("best_model", best_result.name)
        for result in results:
            prefix = result.name
            mlflow.log_metric(f"{prefix}_accuracy", result.accuracy)
            mlflow.log_metric(f"{prefix}_precision", result.precision)
            mlflow.log_metric(f"{prefix}_recall", result.recall)
            mlflow.log_metric(f"{prefix}_f1", result.f1)
            mlflow.log_metric(f"{prefix}_roc_auc", result.roc_auc)
        mlflow.sklearn.log_model(best_model, name="cyberguard_model")


def write_artifacts(best_model: Pipeline, results: list[ModelResult]) -> None:
    """Persist model, metrics, and model-card metadata."""

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)
    payload = [asdict(result) for result in results]
    METRICS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    best = max(payload, key=lambda item: item["f1"])
    MODEL_CARD_PATH.write_text(
        json.dumps(
            {
                "model_name": "CyberGuard Intrusion Detector",
                "problem": "Binary network intrusion detection",
                "best_candidate": best,
                "features": FEATURES,
                "intended_use": "Educational MLOps project and defensive triage assistant.",
                "limitations": [
                    "Synthetic data is reproducible and CIC-style, but not a replacement for production telemetry.",
                    "Predictions support analyst triage and must not be used as the only security control.",
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    best_model, results = train()
    write_artifacts(best_model, results)
    maybe_log_mlflow(results, best_model)
    print(json.dumps([asdict(result) for result in results], indent=2))


if __name__ == "__main__":
    main()
