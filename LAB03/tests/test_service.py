import pickle

import pytest

from fastapi.testclient import TestClient

import service
from service import app


client = TestClient(app)


def test_health_reports_service_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_returns_label_and_score():
    response = client.post("/predict", json={"f1": 1.0, "f2": 2.0})

    assert response.status_code == 200
    assert set(response.json()) == {"label", "score"}
    assert response.json()["label"] in (0, 1)


def test_predict_rejects_invalid_payload():
    response = client.post("/predict", json={"f1": "invalid", "f2": 2.0})

    assert response.status_code == 422
    assert "detail" in response.json()


def test_predict_reports_missing_model_without_training(tmp_path, monkeypatch):
    monkeypatch.setattr(service, "MODEL_PATH", tmp_path / "missing.pkl")

    response = client.post("/predict", json={"f1": 1.0, "f2": 2.0})

    assert response.status_code == 500
    assert "modello non disponibile" in response.json()["detail"]
    assert not service.MODEL_PATH.exists()


def test_predict_reports_malformed_model(tmp_path, monkeypatch):
    model_path = tmp_path / "malformed.pkl"
    with model_path.open("wb") as file_model:
        pickle.dump({"accuracy": "not-a-number"}, file_model)
    monkeypatch.setattr(service, "MODEL_PATH", model_path)

    response = client.post("/predict", json={"f1": 1.0, "f2": 2.0})

    assert response.status_code == 500
    assert "artefatto modello non valido" in response.json()["detail"]


def test_predict_reports_model_with_missing_scoring_fields(tmp_path, monkeypatch):
    model_path = tmp_path / "partial.pkl"
    with model_path.open("wb") as file_model:
        pickle.dump({"accuracy": 0.9}, file_model)
    monkeypatch.setattr(service, "MODEL_PATH", model_path)

    response = client.post("/predict", json={"f1": 1.0, "f2": 2.0})

    assert response.status_code == 500
    assert "modello non disponibile" in response.json()["detail"]


@pytest.mark.parametrize("payload", [
    {"f1": "NaN", "f2": 2.0},
    {"f1": "Infinity", "f2": 2.0},
])
def test_predict_rejects_non_finite_features(payload):
    response = client.post("/predict", json=payload)

    assert response.status_code == 422
    assert "detail" in response.json()