"""Calibra soltanto sullo storico, poi monitora i batch recenti in ordine."""
import json
import sys
import uuid
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from LAB06.drift import AlertState, psi, reference_edges
from LAB06.simulate import BASE, DATA, FEATURES, digest, now, write_json

OUTPUT = BASE / "output"


def load_manifest():
    path = DATA / "manifest.json"
    if not path.exists():
        raise FileNotFoundError("Eseguire prima: python -m LAB06.simulate")
    manifest = json.loads(path.read_text(encoding="utf-8"))
    for name, expected in manifest["files_sha256"].items():
        if digest(DATA / name) != expected:
            raise ValueError(f"File modificato: {name}. Non mescolare simulazioni.")
    return manifest


def batch(row):
    with np.load(DATA / row["file"], allow_pickle=False) as data:
        return {key: data[key].copy() for key in data.files}


def main():
    manifest = load_manifest()
    OUTPUT.mkdir(exist_ok=True)
    ref = batch(next(r for r in manifest["batches"] if r["role"] == "reference"))["x"]
    edges = [reference_edges(ref[:, i]) for i in range(len(FEATURES))]
    historical = []
    accuracies = []
    for row in manifest["batches"]:
        if row["role"] == "history":
            data = batch(row)
            scores = [psi(ref[:, i], data["x"][:, i], edges[i]) for i in range(len(FEATURES))]
            historical.append(scores)
            accuracies.append(float(np.mean(data["y"] == data["prediction"])))
    # Regole fissate nel sorgente: q99 storico x 1.25, minimo numerico 1e-6.
    thresholds = np.maximum(np.quantile(historical, 0.99, axis=0) * 1.25, 1e-6)
    accuracy_threshold = max(0.0, float(np.quantile(accuracies, 0.05)) - 0.02)
    calibration = {"timestamp": now(), "history_batch_ids": [r["batch_id"] for r in manifest["batches"] if r["role"] == "history"],
                   "method": "PSI: q99 di 30 batch storici x 1.25, floor 1e-6; accuracy: q05 storico - 0.02",
                   "historical_psi": historical, "historical_accuracy": accuracies,
                   "psi_thresholds": dict(zip(FEATURES, thresholds.tolist())), "accuracy_threshold": accuracy_threshold}
    print("CALIBRAZIONE STORICA", json.dumps(calibration, indent=2))
    state = AlertState(float(thresholds[0]), persistence=2)
    events = []
    monitor_run_id = uuid.uuid4().hex
    for row in manifest["batches"]:
        if row["role"] != "recent":
            continue
        data = batch(row)
        scores = {name: psi(ref[:, i], data["x"][:, i], edges[i]) for i, name in enumerate(FEATURES)}
        status = state.update(scores["eta"])
        accuracy = float(np.mean(data["prediction"] == data["y"]))
        event = {"timestamp": now(), "batch_timestamp": row["timestamp"], "batch_id": row["batch_id"],
                 "sequence": row["sequence"], "feature": "eta", "drift_score": scores["eta"],
                 "threshold": float(thresholds[0]), "state": status, "consecutive": state.consecutive,
                 "feature_psi": scores, "accuracy": accuracy, "accuracy_threshold": accuracy_threshold,
                 "accuracy_alert": accuracy < accuracy_threshold,
                 "cause": f"PSI eta={scores['eta']:.6f}, soglia={thresholds[0]:.6f}, consecutivi={state.consecutive}",
                 "channel": "Slack #modelops-alerts (ipotetico, invio simulato)",
                 "notification_sent": False, "notification_simulated": status == "ALERT",
                 "owner": "Data Scientist on-call / responsabile dati",
                 "proposed_action": "Verificare eta, policy e qualita etichette; confronto per sottogruppi prima di retraining o rollback",
                 "model_version": manifest["model_version"], "run_id": manifest["run_id"], "monitor_run_id": monitor_run_id}
        events.append(event)
        print(json.dumps(event, ensure_ascii=False))
    result = {"run_id": manifest["run_id"], "monitor_run_id": monitor_run_id,
              "manifest_sha256": digest(DATA / "manifest.json"), "calibration": calibration, "events": events}
    write_json(OUTPUT / "monitoring.json", result)
    (OUTPUT / "alerts.jsonl").write_text("\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
    table = ["# Dashboard locale: simulazione", "", "| Batch | PSI eta | Soglia | Stato | Accuracy | Soglia accuracy |", "|---|---|---|---|---|---|"]
    for e in events:
        table.append(f"| {e['batch_id']} | {e['drift_score']:.6f} | {e['threshold']:.6f} | {e['state']} | {e['accuracy']:.6f} | {accuracy_threshold:.6f} |")
    (OUTPUT / "dashboard.md").write_text("\n".join(table), encoding="utf-8")
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
    ids = [e["batch_id"] for e in events]
    axes[0].plot(ids, [e["drift_score"] for e in events], marker="o", label="PSI eta")
    axes[0].axhline(thresholds[0], color="red", linestyle="--", label="Soglia da storico")
    axes[0].set(ylabel="PSI (adimensionale)", title="Monitoring credito sintetico - batch in ordine di simulazione")
    axes[1].plot(ids, [e["accuracy"] for e in events], marker="o", label="Accuracy")
    axes[1].axhline(accuracy_threshold, color="red", linestyle="--", label="Soglia da storico")
    axes[1].set(xlabel="Batch simulato (non giorni reali)", ylabel="Accuracy (quota corretta)", ylim=(0, 1))
    for ax in axes:
        ax.legend()
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT / "monitoring.png", dpi=160)
    plt.close(fig)
    print(f"Dashboard e grafico: {OUTPUT}")
    if not any(e["state"] == "ALERT" for e in events):
        print("ATTENZIONE: nessun alert persistente osservato. Non dichiararlo nel report.")
    if not any(e["accuracy_alert"] for e in events):
        print("ATTENZIONE: nessuna accuracy sotto soglia. LAB07 non dichiarera un degrado inesistente.")


if __name__ == "__main__":
    main()
