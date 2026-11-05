"""LAB10 tabular path: baseline, teacher adaptation, and student distillation."""
from __future__ import annotations

import argparse
import copy
import json
import pickle
import time
from pathlib import Path
from statistics import median

import numpy as np
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor

from LAB10.tabular_data import read_dataset

SEED = 42
BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "10_dataset_cifre_domini.csv"


def latency_ms(predict_fn, batch: np.ndarray, repeats: int = 50) -> float:
    for _ in range(5):
        predict_fn(batch)
    samples = []
    for _ in range(repeats):
        start = time.perf_counter()
        predict_fn(batch)
        samples.append((time.perf_counter() - start) * 1000.0)
    return float(median(samples))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=DATA)
    args = parser.parse_args()

    x, y, splits, _ = read_dataset(args.data, 64, {"source", "target_train", "test"})
    source_idx = np.flatnonzero(splits == "source")
    target_idx = np.flatnonzero(splits == "target_train")
    test_idx = np.flatnonzero(splits == "test")

    scaler = StandardScaler().fit(x[source_idx])
    x_source = scaler.transform(x[source_idx])
    x_target = scaler.transform(x[target_idx])
    x_test = scaler.transform(x[test_idx])
    y_test = y[test_idx]

    baseline = SGDClassifier(
        loss="log_loss",
        alpha=0.0001,
        random_state=SEED,
        learning_rate="constant",
        eta0=0.005,
        max_iter=1000,
        tol=0.001,
    )
    baseline.fit(x_source, y[source_idx])

    teacher = copy.deepcopy(baseline)
    rng = np.random.default_rng(SEED)
    for _ in range(20):
        order = rng.permutation(len(x_target))
        teacher.partial_fit(x_target[order], y[target_idx][order])

    distillation_x = np.vstack([x_source, x_target])
    soft_targets = teacher.predict_proba(distillation_x)
    student = DecisionTreeRegressor(max_depth=6, min_samples_leaf=8, random_state=SEED)
    student.fit(distillation_x, soft_targets)

    def student_predict(values: np.ndarray) -> np.ndarray:
        return teacher.classes_[np.argmax(student.predict(values), axis=1)]

    batch = x_test[:32]
    rows = []
    for name, model, predict_fn in [
        ("baseline", baseline, baseline.predict),
        ("teacher", teacher, teacher.predict),
        ("student", student, student_predict),
    ]:
        bundle = {"model": model, "scaler": scaler, "classes": teacher.classes_}
        rows.append(
            {
                "model": name,
                "accuracy": float(accuracy_score(y_test, predict_fn(x_test))),
                "serialized_bytes": len(pickle.dumps(bundle)),
                "median_ms_per_batch": latency_ms(predict_fn, batch),
                "batch_size": int(len(batch)),
            }
        )

    result = {
        "splits": {
            "source": int(len(source_idx)),
            "target_train": int(len(target_idx)),
            "test": int(len(test_idx)),
        },
        "seed": SEED,
        "measurements": rows,
        "student_fidelity": float(np.mean(student_predict(x_test) == teacher.predict(x_test))),
        "accuracy_drop_teacher_to_student": float(rows[1]["accuracy"] - rows[2]["accuracy"]),
    }

    output = BASE / "output"
    output.mkdir(exist_ok=True)
    (output / "report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
