"""Training e misure locali, solo su invocazione manuale."""
import hashlib
import json
import platform
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

import joblib
import numpy as np
import sklearn
from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

BASE = Path(__file__).resolve().parent
ARTIFACTS = BASE / "artifacts"
MAX_ACCEPTABLE_DROP = 0.02  # Definita prima di generare o valutare i modelli.


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def measure(model, x, y, repeats=5):
    predictions = model.predict(x)
    # Warmup, poi una predict per osservazione, stesse righe e ripetizioni.
    model.predict(x[:1])
    elapsed = []
    for _ in range(repeats):
        for row in x:
            start = perf_counter_ns()
            model.predict(row.reshape(1, -1))
            elapsed.append((perf_counter_ns() - start) / 1_000_000)
    return {"accuracy": float(accuracy_score(y, predictions)),
            "latency_mean_ms": float(np.mean(elapsed)), "latency_n_calls": len(elapsed)}


def requires_rollback(v1, v2, threshold=MAX_ACCEPTABLE_DROP):
    if not all(np.isfinite(v) and 0 <= v <= 1 for v in (v1, v2)):
        raise ValueError("Accuracy non valida")
    # Tolleranza esclusivamente per la rappresentazione floating point del confine.
    drop = v1 - v2
    return drop > threshold and not np.isclose(drop, threshold, rtol=0, atol=1e-12)


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    data = load_breast_cancer()  # Dataset medico dichiarato: solo demo LAB05.
    x_train, x_test, y_train, y_test = train_test_split(
        data.data, data.target, test_size=0.3, random_state=42, stratify=data.target)
    np.savez(ARTIFACTS / "evaluation_batch.npz", x=x_test, y=y_test)
    versions = {}
    for version, model in {
        "1.0.0": LogisticRegression(max_iter=5000, random_state=42),
        "2.0.0": DecisionTreeClassifier(max_depth=1, random_state=42),
    }.items():
        model.fit(x_train, y_train)
        path = ARTIFACTS / f"model-{version}.pkl"
        joblib.dump({"version": version, "model": model}, path)
        versions[version] = {**measure(model, x_test, y_test),
                             "artifact": f"artifacts/{path.name}", "sha256": digest(path),
                             "algorithm": type(model).__name__, "parameters": model.get_params()}
        print(f"{version}: {versions[version]}")
    metrics = {"timestamp": now(), "threshold": MAX_ACCEPTABLE_DROP, "versions": versions,
               "dataset": "sklearn.load_breast_cancer (medico, non credito)",
               "split_seed": 42, "test_size": 0.3, "stratified": True,
               "evaluation_batch_sha256": digest(ARTIFACTS / "evaluation_batch.npz"),
               "latency_method": "perf_counter_ns; 1 osservazione/chiamata; warmup; 5 ripetizioni; solo predict, nessun HTTP",
               "python": platform.python_version(), "sklearn": sklearn.__version__}
    write_json(BASE / "metrics.json", metrics)
    print(f"Soglia predefinita: {MAX_ACCEPTABLE_DROP}; misure salvate in metrics.json")


if __name__ == "__main__":
    main()
