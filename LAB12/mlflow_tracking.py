"""Real MLflow runs, comparison, and restored-model inference."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pickle
import platform
import subprocess
import sys
from pathlib import Path

import mlflow
import numpy as np
import sklearn
from mlflow import MlflowClient
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

BASE = Path(__file__).resolve().parent
URI = "sqlite:///" + (BASE / "mlflow.db").as_posix()
EXPERIMENT = "lab12-esperimenti-locali"


def read_data(path: Path):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        rows = list(reader)
    if len(columns) != len(set(columns)) or not {"record_id", "split", "target"} <= set(columns):
        raise ValueError("Invalid CSV header")
    features = [c for c in columns if c not in {"record_id", "split", "target"}]
    if len(features) != 13 or not rows:
        raise ValueError("Expected official dataset with 13 features")
    ids = np.asarray([row["record_id"] for row in rows])
    x = np.asarray([[float(row[c]) for c in features] for row in rows])
    targets = np.asarray([float(row["target"]) for row in rows])
    split = np.asarray([row["split"] for row in rows])
    if len(set(ids)) != len(ids) or any(not value for value in ids):
        raise ValueError("Invalid record IDs")
    if not np.isfinite(x).all() or not np.isfinite(targets).all() or not np.equal(targets, np.floor(targets)).all():
        raise ValueError("Invalid numeric values")
    if set(split) != {"train", "validation"} or set(targets) != {0.0, 1.0, 2.0}:
        raise ValueError("Unexpected split or class values")
    return x, targets.astype(int), split, features, ids


def client_and_experiment():
    mlflow.set_tracking_uri(URI)
    client = MlflowClient(tracking_uri=URI)
    exp = client.get_experiment_by_name(EXPERIMENT)
    if exp is None:
        experiment_id = client.create_experiment(EXPERIMENT, artifact_location=(BASE / "artifacts").as_uri())
    else:
        experiment_id = exp.experiment_id
    return client, experiment_id


def train(data: Path) -> None:
    _, experiment_id = client_and_experiment()
    x, y, split, features, ids = read_data(data)
    tr, va = split == "train", split == "validation"

    specs = [
        (
            "logreg_C_0_1",
            make_pipeline(StandardScaler(), LogisticRegression(C=0.1, max_iter=1000, random_state=42)),
            {"algorithm": "logreg", "C": 0.1},
        ),
        (
            "logreg_C_1",
            make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000, random_state=42)),
            {"algorithm": "logreg", "C": 1.0},
        ),
        (
            "forest_depth_3",
            RandomForestClassifier(n_estimators=100, max_depth=3, random_state=42),
            {"algorithm": "forest", "max_depth": 3, "n_estimators": 100},
        ),
        (
            "forest_depth_5",
            RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
            {"algorithm": "forest", "max_depth": 5, "n_estimators": 100},
        ),
    ]

    run_ids = []
    for name, model, params in specs:
        with mlflow.start_run(experiment_id=experiment_id, run_name=name) as run:
            model.fit(x[tr], y[tr])
            pred = model.predict(x[va])
            scores = {
                "accuracy": float(accuracy_score(y[va], pred)),
                "f1_macro": float(f1_score(y[va], pred, average="macro")),
            }
            raw = pickle.dumps(model)
            metadata = {
                "dataset_sha256": hashlib.sha256(data.read_bytes()).hexdigest(),
                "model_sha256": hashlib.sha256(raw).hexdigest(),
                "run_id": run.info.run_id,
                "feature_names": features,
                "train_ids": ids[tr].tolist(),
                "validation_ids": ids[va].tolist(),
                "split": "CSV provided by teacher; no new split generated",
                "metrics": scores,
                "python": platform.python_version(),
                "sklearn": sklearn.__version__,
                "mlflow": mlflow.__version__,
            }
            mlflow.log_params({**params, "seed": 42, "train_rows": int(tr.sum()), "validation_rows": int(va.sum())})
            mlflow.set_tag("data_sha256", metadata["dataset_sha256"])
            mlflow.log_metrics(scores)
            mlflow.log_dict(metadata, "metadata.json")

            folder = BASE / "local_models" / run.info.run_id
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "model.pkl").write_bytes(raw)
            mlflow.log_artifact(str(folder / "model.pkl"))
            run_ids.append(run.info.run_id)

    session = {
        "tracking_uri": URI,
        "experiment_id": experiment_id,
        "run_ids": run_ids,
        "data_path": str(data.resolve()),
    }
    (BASE / "session.json").write_text(json.dumps(session, indent=2), encoding="utf-8")
    print(json.dumps(session, indent=2))


def compare() -> None:
    client, experiment_id = client_and_experiment()
    session = json.loads((BASE / "session.json").read_text(encoding="utf-8"))
    expected = set(session["run_ids"])
    runs = client.search_runs([experiment_id], filter_string="attributes.status = 'FINISHED'", max_results=1000)
    rows = [
        {
            "run_id": run.info.run_id,
            "name": run.data.tags.get("mlflow.runName", ""),
            "accuracy": run.data.metrics["accuracy"],
            "f1_macro": run.data.metrics["f1_macro"],
        }
        for run in runs
        if run.info.run_id in expected
    ]
    if len(rows) != 4:
        raise RuntimeError("Expected exactly four runs in current session")

    rows.sort(key=lambda row: (-row["f1_macro"], -row["accuracy"], row["name"]))
    with (BASE / "comparison.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    chosen = {
        **rows[0],
        "rule": "max f1_macro; tie-break by accuracy, then name",
        "tracking_uri": URI,
    }
    (BASE / "selected_run.json").write_text(json.dumps(chosen, indent=2), encoding="utf-8")
    print(json.dumps({"comparison": rows, "selected": chosen}, indent=2))


def restore(data: Path, run_id: str | None = None) -> None:
    client, _ = client_and_experiment()
    selected = json.loads((BASE / "selected_run.json").read_text(encoding="utf-8")) if run_id is None else {"run_id": run_id}
    run_id = selected["run_id"]

    dest = BASE / "restored" / run_id
    dest.mkdir(parents=True, exist_ok=True)
    model_path = Path(client.download_artifacts(run_id, "model.pkl", str(dest)))
    meta_path = Path(client.download_artifacts(run_id, "metadata.json", str(dest)))
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    raw = model_path.read_bytes()

    if hashlib.sha256(raw).hexdigest() != metadata["model_sha256"] or metadata["run_id"] != run_id:
        raise RuntimeError("Artifact and metadata mismatch")
    if hashlib.sha256(data.read_bytes()).hexdigest() != metadata["dataset_sha256"]:
        raise ValueError("Dataset hash mismatch")

    x, y, split, features, ids = read_data(data)
    va = split == "validation"
    if features != metadata["feature_names"] or ids[va].tolist() != metadata["validation_ids"]:
        raise ValueError("Validation schema or IDs mismatch")

    model = pickle.loads(raw)
    pred = model.predict(x[va])
    score = float(accuracy_score(y[va], pred))
    rows = [
        {"record_id": str(i), "target": int(t), "prediction": int(p), "run_id": run_id}
        for i, t, p in zip(ids[va], y[va], pred)
    ]
    with (dest / "predictions.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "run_id": run_id,
        "restored_accuracy": score,
        "logged_accuracy": metadata["metrics"]["accuracy"],
        "prediction_rows": len(rows),
        "model_source": "MLflow artifact store",
    }
    (dest / "restore_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ["train", "restore"]:
        cmd = sub.add_parser(name)
        cmd.add_argument("--data", type=Path, default=BASE / "data" / "12_dataset_tracking_vini.csv")
        if name == "restore":
            cmd.add_argument("--run-id")

    sub.add_parser("compare")
    sub.add_parser("ui")
    args = parser.parse_args()

    if args.command == "train":
        train(args.data)
    elif args.command == "compare":
        compare()
    elif args.command == "ui":
        subprocess.run(
            [sys.executable, "-m", "mlflow", "ui", "--backend-store-uri", URI, "--host", "127.0.0.1", "--port", "5000"],
            check=True,
        )
    else:
        restore(args.data, args.run_id)


if __name__ == "__main__":
    main()
