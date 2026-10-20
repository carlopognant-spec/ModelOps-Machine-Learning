"""Rilascia v2 nel registry simulato, poi ripristina e verifica se necessario."""
import json
import sys
import uuid
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import numpy as np

from LAB05.evaluate import BASE, ARTIFACTS, MAX_ACCEPTABLE_DROP, digest, measure, now, requires_rollback, write_json


def load_version(version, row):
    path = (BASE / row["artifact"]).resolve()
    if not path.is_relative_to(ARTIFACTS.resolve()) or digest(path) != row["sha256"]:
        raise ValueError("Percorso o hash artefatto non valido")
    bundle = joblib.load(path)
    if bundle["version"] != version:
        raise ValueError("Versione caricata incoerente")
    return bundle["model"]


def main():
    metrics = json.loads((BASE / "metrics.json").read_text(encoding="utf-8"))
    if metrics["threshold"] != MAX_ACCEPTABLE_DROP:
        raise ValueError("Soglia cambiata dopo la valutazione: ripetere evaluate.py")
    batch_path = ARTIFACTS / "evaluation_batch.npz"
    if digest(batch_path) != metrics["evaluation_batch_sha256"]:
        raise ValueError("Batch diverso dalla valutazione")
    with np.load(batch_path) as batch:
        x, y = batch["x"], batch["y"]
    versions = metrics["versions"]
    # Verifica preventiva delle metriche salvate: non fare rollback su dati obsoleti.
    for version, row in versions.items():
        model = load_version(version, row)
        accuracy = float(np.mean(model.predict(x) == y))
        if not np.isclose(accuracy, row["accuracy"], rtol=0, atol=1e-12):
            raise ValueError("Metrica non coerente con modello e batch")
    run_id = uuid.uuid4().hex
    registry = {"run_id": run_id, "timestamp": now(), "simulation": True,
                "initial_version": "2.0.0", "active_version": "2.0.0", "versions": versions,
                "state": "v2 rilasciata localmente"}
    write_json(BASE / "registry.json", registry)
    write_json(BASE / "registry_before.json", registry)
    print("PRIMA: registry active_version=2.0.0 (rilascio simulato)")
    v1, v2 = versions["1.0.0"]["accuracy"], versions["2.0.0"]["accuracy"]
    drop = v1 - v2
    rollback = requires_rollback(v1, v2)
    final = "1.0.0" if rollback else "2.0.0"
    reason = (f"calo={drop:.6f} {'>' if rollback else '<='} soglia={MAX_ACCEPTABLE_DROP}; "
              + ("ripristinare baseline nota; fix non validato nel timebox didattico" if rollback
                 else "mantenere v2; nessun rollback richiesto"))
    registry.update(active_version=final, state="rollback locale" if rollback else "v2 mantenuta", decision=reason)
    write_json(BASE / "registry.json", registry)
    # Rilegge il registry realmente scritto e ricarica l'artefatto attivo.
    actual = json.loads((BASE / "registry.json").read_text(encoding="utf-8"))
    model = load_version(actual["active_version"], actual["versions"][actual["active_version"]])
    post = measure(model, x, y)
    verified = actual["active_version"] == final and np.isclose(
        post["accuracy"], versions[final]["accuracy"], rtol=0, atol=1e-12)
    event = {"run_id": run_id, "timestamp": now(), "initial_version": "2.0.0",
             "final_version": actual["active_version"], "restored_version": final if rollback else None,
             "rollback": rollback, "threshold": MAX_ACCEPTABLE_DROP, "drop": drop,
             "reason": reason, "verification": {**post, "passed": bool(verified)}}
    with (BASE / "rollback_events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event, allow_nan=False) + "\n")
    write_json(BASE / "post_verification.json", event)
    print(f"v1={v1:.6f}; v2={v2:.6f}; {reason}")
    print(f"DOPO: {actual['active_version']}; verifica={event['verification']}")
    if not verified:
        raise RuntimeError("Verifica post-decisione fallita: conservare i log e indagare")


if __name__ == "__main__":
    main()
