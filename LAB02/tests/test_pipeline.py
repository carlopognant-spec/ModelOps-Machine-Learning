import subprocess
import sys
import pickle
import pytest
from pathlib import Path


LAB02_DIR = Path(__file__).resolve().parents[1]
PIPELINE = LAB02_DIR / "pipeline.py"


def test_train_rejects_invalid_dataset_before_creating_model(tmp_path):
    dataset = tmp_path / "data_missing_label.csv"
    dataset.write_text("f1,f2\n1,2\n", encoding="utf-8")
    model = tmp_path / "model.pkl"

    result = subprocess.run(
        [sys.executable, str(PIPELINE), "--stage", "train",
         "--data", str(dataset), "--out", str(model)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "[VALIDATE] FAIL" in result.stdout
    assert not model.exists()


def test_gate_reports_missing_model(tmp_path):
    result = subprocess.run(
        [sys.executable, str(PIPELINE), "--stage", "gate",
         "--model", str(tmp_path / "missing.pkl"), "--threshold", "0.75"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "[GATE] FAIL" in result.stdout


def test_gate_rejects_malformed_model(tmp_path):
    model = tmp_path / "malformed.pkl"
    with model.open("wb") as file_model:
        pickle.dump({"accuracy": "not-a-number"}, file_model)

    result = subprocess.run(
        [sys.executable, str(PIPELINE), "--stage", "gate",
         "--model", str(model), "--threshold", "0.75"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "[GATE] FAIL" in result.stdout


def test_gate_rejects_accuracy_below_threshold(tmp_path):
    model = tmp_path / "under_threshold.pkl"
    with model.open("wb") as file_model:
        pickle.dump({"accuracy": 0.5}, file_model)

    result = subprocess.run(
        [sys.executable, str(PIPELINE), "--stage", "gate",
         "--model", str(model), "--threshold", "0.75"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "RESPINTO" in result.stdout


@pytest.mark.parametrize("accuracy", [float("nan"), float("inf"), float("-inf")])
def test_gate_rejects_non_finite_accuracy(tmp_path, accuracy):
    model = tmp_path / "non_finite.pkl"
    with model.open("wb") as file_model:
        pickle.dump({"accuracy": accuracy}, file_model)

    result = subprocess.run(
        [sys.executable, str(PIPELINE), "--stage", "gate",
         "--model", str(model), "--threshold", "0.75"],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "[GATE] FAIL" in result.stdout