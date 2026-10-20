"""Gate misurato e registry coerente con gli artefatti."""
import json
import math
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from LAB04.common import ARTIFACTS, BASE, THRESHOLD, load_verified, now, write_json


def build(rows):
    for row in rows:
        accuracy = row["accuracy"]
        if isinstance(accuracy, bool) or not isinstance(accuracy, (int, float)) or not math.isfinite(accuracy) or not 0 <= accuracy <= 1:
            raise ValueError("Accuracy non valida")
        load_verified(row)
        row["status"] = "promosso" if accuracy >= THRESHOLD else "scartato"
        row["reason"] = f"accuracy={accuracy:.6f} {'>=' if accuracy >= THRESHOLD else '<'} {THRESHOLD}"
    baseline, candidate = rows
    # Non pubblicare un registry nuovo che nasconda il fallimento della baseline.
    if baseline["status"] != "promosso":
        raise ValueError("Baseline v2 sotto soglia: scenario storico non riprodotto. Nessun registry aggiornato; non avviare API.")
    active = candidate["version"] if candidate["status"] == "promosso" else baseline["version"]
    return {"timestamp": now(), "threshold": THRESHOLD, "active_version": active, "versions": rows}


def main():
    rows = [json.loads((ARTIFACTS / f"model_{v}.json").read_text(encoding="utf-8")) for v in ("v2", "v3")]
    registry = build(rows)
    write_json(BASE / "registry.json", registry)
    lines = ["# Registry LAB04", "", "| Versione | Artefatto | Accuracy | Stato | Motivo |", "|---|---|---|---|---|"]
    for row in rows:
        lines.append(f"| {row['version']} | {row['artifact']} | {row['accuracy']:.6f} | {row['status']} | {row['reason']} |")
        print(row["version"], row["status"], row["reason"])
    lines.extend(["", f"Versione attiva: {registry['active_version']}; soglia: {THRESHOLD}"])
    (BASE / "registry.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Versione attiva: {registry['active_version']}")


if __name__ == "__main__":
    main()
