import importlib
import json

import joblib
import numpy as np
import pytest

from LAB05.evaluate import digest, requires_rollback, write_json


class FixedModel:
    def __init__(self, correct):
        self.correct = correct

    def predict(self, x):
        return (x[:, 0] >= self.correct).astype(int)


@pytest.mark.parametrize("v1,v2,expected", [(0.9, 0.8, True), (0.9, 0.89, False),
                                          (0.95, 0.93, False), (0.8, 0.9, False)])
def test_gate_boundary(v1, v2, expected):
    assert bool(requires_rollback(v1, v2)) == expected


@pytest.mark.parametrize("v2_correct,expected_final", [(60, "1.0.0"), (90, "2.0.0")])
def test_release_then_decision_and_reload(tmp_path, monkeypatch, v2_correct, expected_final):
    rollback = importlib.import_module("LAB05.rollback_versions")
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    x, y = np.arange(100).reshape(-1, 1), np.zeros(100, dtype=int)
    np.savez(artifacts / "evaluation_batch.npz", x=x, y=y)
    versions = {}
    for version, correct in [("1.0.0", 90), ("2.0.0", v2_correct)]:
        path = artifacts / f"{version}.pkl"
        joblib.dump({"version": version, "model": FixedModel(correct)}, path)
        versions[version] = {"accuracy": correct / 100, "artifact": f"artifacts/{path.name}", "sha256": digest(path)}
    write_json(tmp_path / "metrics.json", {"threshold": 0.02, "versions": versions,
                                           "evaluation_batch_sha256": digest(artifacts / "evaluation_batch.npz")})
    monkeypatch.setattr(rollback, "BASE", tmp_path)
    monkeypatch.setattr(rollback, "ARTIFACTS", artifacts)
    rollback.main()
    before = json.loads((tmp_path / "registry_before.json").read_text())
    after = json.loads((tmp_path / "registry.json").read_text())
    event = json.loads((tmp_path / "rollback_events.jsonl").read_text())
    assert before["active_version"] == "2.0.0"
    assert after["active_version"] == expected_final
    assert event["initial_version"] == "2.0.0"
    assert event["verification"]["passed"]
    assert event["verification"]["accuracy"] == versions[expected_final]["accuracy"]
