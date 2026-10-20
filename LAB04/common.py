"""Identita degli artefatti: verificare prima di servire."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib

BASE = Path(__file__).resolve().parent
ARTIFACTS = BASE / "artifacts"
THRESHOLD = 0.85


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_verified(row, base=BASE):
    path = (base / row["artifact"]).resolve()
    if not path.is_relative_to(base.resolve()):
        raise ValueError("Artefatto fuori dal laboratorio")
    if digest(path) != row["sha256"]:
        raise ValueError("Hash modello diverso dal registry: rigenerare il registry")
    bundle = joblib.load(path)  # Solo artefatti locali fidati.
    if bundle["version"] != row["version"]:
        raise ValueError("Versione artefatto diversa dal registry")
    if bundle["feature_names"] != row["feature_names"]:
        raise ValueError("Schema feature diverso dal registry")
    if bundle["model"].n_features_in_ != len(row["feature_names"]):
        raise ValueError("Numero feature del modello incoerente")
    return bundle
