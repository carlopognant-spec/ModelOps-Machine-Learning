"""Test isolati senza training; eseguire manualmente con pytest."""
import importlib
import json

import joblib
import pytest
from fastapi.testclient import TestClient

api = importlib.import_module("LAB04.app")
from LAB04.common import digest, load_verified


class FakeModel:
    n_features_in_ = 13

    def predict(self, x):
        return [0] * len(x)


@pytest.fixture
def client(tmp_path, monkeypatch):
    row = {"version": "v2", "status": "promosso", "accuracy": 0.9, "artifact": "fake.pkl"}
    (tmp_path / "registry.json").write_text(json.dumps({"active_version": "v2", "threshold": 0.85, "versions": [row]}))
    monkeypatch.setattr(api, "BASE", tmp_path)
    monkeypatch.setattr(api, "load_verified", lambda row: {"version": "v2", "feature_names": [str(i) for i in range(13)], "model": FakeModel()})
    with TestClient(api.app) as client:
        yield client


def test_valid_version(client):
    response = client.post("/predict", json={"features": [1.0] * 13})
    assert response.status_code == 200
    assert response.json() == {"prediction": 0, "model_version": "v2"}


@pytest.mark.parametrize("payload", [{}, {"features": [1]}, {"features": ["1"] * 13},
                                      {"features": [False] * 13}, {"features": [None] * 13},
                                      {"features": [1] * 13, "extra": 1}])
def test_invalid_without_prediction(client, payload):
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert "prediction" not in response.json()


@pytest.mark.parametrize("token", ["NaN", "Infinity", "-Infinity"])
def test_nonfinite_json(client, token):
    response = client.post("/predict", content='{"features":[' + token + ',1,1,1,1,1,1,1,1,1,1,1,1]}',
                           headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert "prediction" not in response.json()


def test_artifact_identity_and_hash(tmp_path):
    bundle = {"version": "v3", "feature_names": [str(i) for i in range(13)], "model": FakeModel()}
    path = tmp_path / "model.pkl"
    joblib.dump(bundle, path)
    row = {"artifact": path.name, "version": "v2", "feature_names": bundle["feature_names"], "sha256": digest(path)}
    with pytest.raises(ValueError, match="Versione"):
        load_verified(row, tmp_path)
    row["version"] = "v3"
    assert load_verified(row, tmp_path)["version"] == "v3"
    path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="Hash"):
        load_verified(row, tmp_path)


def test_gate_baseline_and_candidate(monkeypatch):
    registry = importlib.import_module("LAB04.build_registry")
    monkeypatch.setattr(registry, "load_verified", lambda row: None)
    rows = [{"version": "v2", "accuracy": 0.9}, {"version": "v3", "accuracy": 0.5}]
    assert registry.build(rows)["active_version"] == "v2"
    rows[1]["accuracy"] = 0.85
    assert registry.build(rows)["active_version"] == "v3"
    rows[0]["accuracy"] = 0.8
    with pytest.raises(ValueError, match="Baseline"):
        registry.build(rows)
