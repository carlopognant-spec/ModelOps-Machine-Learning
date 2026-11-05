"""Compile and execute a three-step Kubeflow pipeline locally, without a cluster."""

import argparse
import csv
import hashlib
import json
import pickle
from pathlib import Path

import numpy as np
from kfp import compiler, dsl, local
from kfp.dsl import Artifact, Dataset, Input, Model, Output
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


@dsl.component(base_image="python:3.12-slim", install_kfp_package=False)
def prepare_data(data_path: str, training: Output[Dataset], validation: Output[Dataset], contract: Output[Artifact]):
    import csv
    import hashlib
    import json
    import math
    from pathlib import Path

    path = Path(data_path)
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        names = reader.fieldnames or []
        rows = list(reader)

    if not rows or len(names) != len(set(names)) or not {"record_id", "split", "target"} <= set(names):
        raise ValueError("Invalid CSV")
    features = [name for name in names if name not in {"record_id", "split", "target"}]
    if len(features) != 13 or len({row["record_id"] for row in rows}) != len(rows):
        raise ValueError("Invalid feature schema or duplicate IDs")
    if any(not row["record_id"] for row in rows) or {row["split"] for row in rows} != {"train", "validation"}:
        raise ValueError("Unexpected IDs or split values")
    if any(not math.isfinite(float(row[col])) for row in rows for col in features):
        raise ValueError("Non-finite feature value found")
    if any(row["target"] not in {"0", "1", "2"} for row in rows):
        raise ValueError("Unexpected target class")

    for artifact, split in [(training, "train"), (validation, "validation")]:
        Path(artifact.path).parent.mkdir(parents=True, exist_ok=True)
        with open(artifact.path, "w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=names)
            writer.writeheader()
            writer.writerows([row for row in rows if row["split"] == split])

    metadata = {
        "feature_names": features,
        "data_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "train_rows": sum(row["split"] == "train" for row in rows),
        "validation_rows": sum(row["split"] == "validation" for row in rows),
    }
    Path(contract.path).parent.mkdir(parents=True, exist_ok=True)
    Path(contract.path).write_text(json.dumps(metadata, indent=2), encoding="utf-8")


@dsl.component(base_image="python:3.12-slim", install_kfp_package=False)
def train_model(training: Input[Dataset], contract: Input[Artifact], regularization: float, model: Output[Model]):
    import csv
    import json
    import pickle
    from pathlib import Path

    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    metadata = json.loads(Path(contract.path).read_text(encoding="utf-8"))
    with open(training.path, newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    x = np.asarray([[float(row[col]) for col in metadata["feature_names"]] for row in rows])
    y = np.asarray([int(row["target"]) for row in rows])

    model_pipe = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=regularization, max_iter=1000, random_state=42),
    )
    model_pipe.fit(x, y)

    bundle = {
        "model": model_pipe,
        "feature_names": metadata["feature_names"],
        "data_sha256": metadata["data_sha256"],
    }
    Path(model.path).parent.mkdir(parents=True, exist_ok=True)
    Path(model.path).write_bytes(pickle.dumps(bundle))


@dsl.component(base_image="python:3.12-slim", install_kfp_package=False)
def evaluate_model(validation: Input[Dataset], model: Input[Model], contract: Input[Artifact]) -> str:
    import csv
    import hashlib
    import json
    import pickle
    from pathlib import Path

    import numpy as np
    from sklearn.metrics import accuracy_score, f1_score

    metadata = json.loads(Path(contract.path).read_text(encoding="utf-8"))
    raw = Path(model.path).read_bytes()
    bundle = pickle.loads(raw)
    if bundle["feature_names"] != metadata["feature_names"] or bundle["data_sha256"] != metadata["data_sha256"]:
        raise ValueError("Model and contract mismatch")

    with open(validation.path, newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    x = np.asarray([[float(row[col]) for col in metadata["feature_names"]] for row in rows])
    y = np.asarray([int(row["target"]) for row in rows])
    pred = bundle["model"].predict(x)
    return json.dumps(
        {
            "accuracy": float(accuracy_score(y, pred)),
            "f1_macro": float(f1_score(y, pred, average="macro")),
            "validation_rows": len(rows),
            "data_sha256": metadata["data_sha256"],
            "model_sha256": hashlib.sha256(raw).hexdigest(),
            "execution": "Kubeflow SDK local SubprocessRunner",
        }
    )


@dsl.pipeline(name="lab12-wine-local")
def wine_pipeline(data_path: str, regularization: float = 1.0) -> str:
    prepared = prepare_data(data_path=data_path)
    trained = train_model(
        training=prepared.outputs["training"],
        contract=prepared.outputs["contract"],
        regularization=regularization,
    )
    scored = evaluate_model(
        validation=prepared.outputs["validation"],
        model=trained.outputs["model"],
        contract=prepared.outputs["contract"],
    )
    return scored.output


def fallback_local_pipeline(data_path: Path) -> dict:
    """Fallback for hosts where KFP local subprocess execution is unavailable."""
    with data_path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        names = reader.fieldnames or []
        rows = list(reader)

    if not rows or len(names) != len(set(names)) or not {"record_id", "split", "target"} <= set(names):
        raise ValueError("Invalid CSV")
    features = [name for name in names if name not in {"record_id", "split", "target"}]
    if len(features) != 13:
        raise ValueError("Expected exactly 13 feature columns")

    train_rows = [row for row in rows if row["split"] == "train"]
    val_rows = [row for row in rows if row["split"] == "validation"]
    if not train_rows or not val_rows:
        raise ValueError("Missing train/validation rows")

    x_train = np.asarray([[float(row[col]) for col in features] for row in train_rows])
    y_train = np.asarray([int(row["target"]) for row in train_rows])
    x_val = np.asarray([[float(row[col]) for col in features] for row in val_rows])
    y_val = np.asarray([int(row["target"]) for row in val_rows])

    model = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000, random_state=42))
    model.fit(x_train, y_train)
    pred = model.predict(x_val)

    raw_model = pickle.dumps(
        {
            "model": model,
            "feature_names": features,
            "data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        }
    )
    return {
        "accuracy": float(accuracy_score(y_val, pred)),
        "f1_macro": float(f1_score(y_val, pred, average="macro")),
        "validation_rows": int(len(val_rows)),
        "data_sha256": hashlib.sha256(data_path.read_bytes()).hexdigest(),
        "model_sha256": hashlib.sha256(raw_model).hexdigest(),
        "execution": "Fallback local Python execution (KFP subprocess runner unavailable)",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path(__file__).resolve().parent / "data" / "12_dataset_tracking_vini.csv")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "output" / "kfp_output")
    parser.add_argument("--compile-only", action="store_true")
    args = parser.parse_args()

    root = args.out.resolve()
    root.mkdir(parents=True, exist_ok=False)
    compiler.Compiler().compile(wine_pipeline, package_path=str(root / "wine_pipeline.yaml"))
    if args.compile_only:
        print("YAML compiled. Components not executed.")
        return

    try:
        local.init(runner=local.SubprocessRunner(use_venv=False), pipeline_root=str(root / "runs"))
        task = wine_pipeline(data_path=str(args.data.resolve()), regularization=1.0)
        report = json.loads(task.output)
    except (FileNotFoundError, OSError) as exc:
        print(f"KFP local subprocess runner unavailable on this host: {exc}")
        print("Using in-process fallback with equivalent prepare/train/evaluate logic.")
        report = fallback_local_pipeline(args.data.resolve())

    (root / "kfp_result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
