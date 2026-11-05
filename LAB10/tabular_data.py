"""CSV contract utilities used by LAB10."""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np


def read_dataset(path: Path, feature_count: int, allowed_splits: set[str]):
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        columns = reader.fieldnames or []
        if not {"record_id", "split", "target"} <= set(columns):
            raise ValueError("Missing required columns: record_id, split, target")
        if len(set(columns)) != len(columns):
            raise ValueError("Duplicate columns are not allowed")
        features = [c for c in columns if c not in {"record_id", "split", "target"}]
        rows = list(reader)

    if len(features) != feature_count or not rows:
        raise ValueError("Unexpected feature count or empty CSV")
    if len({row["record_id"] for row in rows}) != len(rows):
        raise ValueError("record_id must be unique")

    x = np.asarray([[float(row[c]) for c in features] for row in rows])
    y_float = np.asarray([float(row["target"]) for row in rows])
    if not np.isfinite(x).all() or not np.isfinite(y_float).all():
        raise ValueError("Found non-finite numeric values")
    if not np.equal(y_float, np.floor(y_float)).all():
        raise ValueError("Target must be integer for classification")

    splits = np.asarray([row["split"] for row in rows])
    if set(splits) != set(allowed_splits):
        raise ValueError(f"Expected splits {allowed_splits}, found {set(splits)}")

    return x, y_float.astype(int), splits, features
