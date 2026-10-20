"""Ricostruzione del metodo storico; metriche sempre calcolate."""
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import sklearn
from sklearn.datasets import load_wine
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from LAB04.common import ARTIFACTS, digest, now, write_json


def main():
    ARTIFACTS.mkdir(exist_ok=True)
    data = load_wine()
    noisy = data.data + np.random.RandomState(0).normal(0, 2.0, data.data.shape)
    x_train, x_test, y_train, y_test = train_test_split(
        noisy, data.target, test_size=0.3, random_state=42, stratify=data.target)
    models = {
        "v2": RandomForestClassifier(n_estimators=200, random_state=42),
        "v3": RandomForestClassifier(n_estimators=1, max_depth=1, random_state=42),
    }
    for version, model in models.items():
        model.fit(x_train, y_train)
        accuracy = float(accuracy_score(y_test, model.predict(x_test)))
        bundle = {"version": version, "feature_names": list(data.feature_names), "model": model}
        path = ARTIFACTS / f"model_{version}.pkl"
        joblib.dump(bundle, path)
        meta = {
            "version": version, "artifact": f"artifacts/{path.name}",
            "sha256": digest(path), "accuracy": accuracy,
            "algorithm": type(model).__name__, "parameters": model.get_params(),
            "feature_names": list(data.feature_names), "classes": data.target_names.tolist(),
            "timestamp": now(), "dataset": "sklearn.load_wine + Gaussian(0,2)",
            "noise_seed": 0, "split_seed": 42, "test_size": 0.3,
            "n_train": len(y_train), "n_test": len(y_test),
            "sklearn_version": sklearn.__version__,
        }
        write_json(path.with_suffix(".json"), meta)
        print(f"{version}: accuracy={accuracy:.6f}; test={len(y_test)}; modello={path}")
    print("Training terminato. Ora costruire il registry; non confrontare metriche arrotondate.")


if __name__ == "__main__":
    main()
