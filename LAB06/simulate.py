"""Genera una sola volta dati sintetici, modello e predizioni condivisi con LAB07."""
import hashlib
import json
import platform
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np
import sklearn
from sklearn.ensemble import RandomForestClassifier

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
FEATURES = ["eta", "reddito_migliaia_euro_anno", "rapporto_debito", "anni_impiego"]
VERSION = "credit-sim-v1"


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def customers(rng, n, shifted=False):
    age = np.clip(rng.normal(65 if shifted else 40, 8, n), 18, 85)
    income = np.clip(rng.normal(50, 15, n), 10, 130)
    debt = np.clip(rng.normal(0.30, 0.12, n), 0, 1)
    employment = np.clip(rng.normal(8, 4, n), 0, 40)
    x = np.column_stack([age, income, debt, employment])
    score = 0.06 * (age - 40) + 0.04 * (income - 50) - 6 * (debt - 0.3) + 0.1 * (employment - 8)
    # Scenario predefinito: nei batch shifted cambia anche la policy sintetica.
    # Non attribuire il degrado al solo drift dell'eta.
    cutoff = 3.0 if shifted else 0.0
    y = (score + rng.normal(0, 0.4, n) > cutoff).astype(int)
    return x, y


def main():
    if DATA.exists() and any(DATA.iterdir()):
        raise SystemExit("LAB06/data non vuota: conservarla per LAB07. Per una nuova simulazione archiviare prima l'intera cartella.")
    DATA.mkdir(exist_ok=True)
    rng = np.random.default_rng(42)
    x_train, y_train = customers(rng, 3000)
    model = RandomForestClassifier(n_estimators=200, max_depth=8, random_state=42, n_jobs=1)
    model.fit(x_train, y_train)
    np.savez(DATA / "training.npz", x=x_train, y=y_train)
    model_path = DATA / "model.pkl"
    joblib.dump({"version": VERSION, "feature_names": FEATURES, "model": model}, model_path)
    manifest = {"run_id": uuid.uuid4().hex, "timestamp": now(), "seed": 42, "synthetic": True,
                "model_version": VERSION, "feature_names": FEATURES, "batches": [],
                "scenario": "credito sintetico; eta spostata e policy etichetta piu restrittiva nei batch shifted; nessuna causalita inferita",
                "python": platform.python_version(), "sklearn": sklearn.__version__}
    specifications = [("reference", "reference", False)]
    specifications += [(f"history-{i:02}", "history", False) for i in range(30)]
    specifications += [(f"recent-{i:02}", "recent", shift) for i, shift in enumerate([False, True, True, True, False])]
    for sequence, (batch_id, role, shifted) in enumerate(specifications):
        x, y = customers(rng, 1000 if role == "reference" else 500, shifted)
        prediction = model.predict(x)
        proba = model.predict_proba(x)
        np.savez(DATA / f"{batch_id}.npz", x=x, y=y, prediction=prediction, proba=proba)
        manifest["batches"].append({"batch_id": batch_id, "role": role, "sequence": sequence,
                                     "timestamp": now(), "shifted_scenario": shifted,
                                     "file": f"{batch_id}.npz", "n": len(y)})
        print(f"{batch_id}: ruolo={role}; n={len(y)}; accuracy={np.mean(prediction == y):.6f}; scenario_shift={shifted}")
    manifest["files_sha256"] = {p.name: digest(p) for p in DATA.iterdir() if p.is_file()}
    write_json(DATA / "manifest.json", manifest)
    print(f"Dati sintetici salvati in {DATA}; versione={VERSION}; run={manifest['run_id']}")


if __name__ == "__main__":
    main()
