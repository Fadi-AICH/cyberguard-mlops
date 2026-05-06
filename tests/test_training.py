from __future__ import annotations

from sklearn.pipeline import Pipeline

from cyberguard_ml.pipeline.train_model import build_preprocessor, candidate_models


def test_preprocessor_contains_expected_transformers() -> None:
    preprocessor = build_preprocessor()

    transformer_names = {name for name, _, _ in preprocessor.transformers}

    assert transformer_names == {"numeric", "categorical"}


def test_candidate_models_are_named() -> None:
    models = candidate_models()

    assert {"logistic_regression", "random_forest", "gradient_boosting"} == set(models)


def test_pipeline_contract_can_be_built() -> None:
    for estimator in candidate_models().values():
        pipeline = Pipeline([("preprocess", build_preprocessor()), ("model", estimator)])
        assert "preprocess" in pipeline.named_steps
        assert "model" in pipeline.named_steps
