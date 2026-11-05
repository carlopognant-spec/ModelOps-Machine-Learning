"""LAB09: local permission matrix, audit log, and controlled training job."""
from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from LAB09.tabular_data import read_dataset

ACTORS = {"alice": "ml_engineer", "bob": "approver", "carla": "data_owner"}
PERMISSIONS = {
    "data_owner": {"read_dataset", "upload"},
    "ml_engineer": {"read_dataset", "train"},
    "approver": {"approve"},
}

BASE = Path(__file__).resolve().parent
DATASET_VERSION = "09_dataset_job_vini.csv"
OUTPUT = BASE / "output"
AUDIT = OUTPUT / "audit.jsonl"


def audit_event(actor: str, action: str, resource: str, allowed: bool, **fields):
    OUTPUT.mkdir(exist_ok=True)
    event = {
        "event_id": uuid.uuid4().hex,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": actor,
        "role": ACTORS.get(actor, "unknown"),
        "action": action,
        "resource": resource,
        "outcome": "allowed" if allowed else "denied",
        **fields,
    }
    with AUDIT.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(event) + "\n")
    print(json.dumps(event, ensure_ascii=False))
    return event


def authorize(actor: str, action: str, resource: str) -> bool:
    role = ACTORS.get(actor)
    allowed = action in PERMISSIONS.get(role, set())
    audit_event(actor, action, resource, allowed, reason="role policy")
    return allowed


def run_job(actor: str, data_path: Path) -> str | None:
    if not authorize(actor, "train", DATASET_VERSION):
        return None
    if not authorize(actor, "read_dataset", DATASET_VERSION):
        return None

    run_id = uuid.uuid4().hex
    x, y, splits, _ = read_dataset(data_path, 13, {"train", "validation"})
    x_train, x_val = x[splits == "train"], x[splits == "validation"]
    y_train, y_val = y[splits == "train"], y[splits == "validation"]

    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500, random_state=42))
    model.fit(x_train, y_train)
    accuracy = float(accuracy_score(y_val, model.predict(x_val)))
    audit_event(
        actor,
        "training_completed",
        DATASET_VERSION,
        True,
        run_id=run_id,
        training_mode="from_scratch",
        base_model_version=None,
        accuracy=accuracy,
    )
    return run_id


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=BASE / "data" / DATASET_VERSION)
    args = parser.parse_args()

    run_job("bob", args.data)
    authorize("alice", "approve", "candidate_model")
    run_id = run_job("alice", args.data)
    if run_id:
        authorize("bob", "approve", f"run:{run_id}")

    print("Local simulation only: no external IAM or model registry was modified")


if __name__ == "__main__":
    main()
