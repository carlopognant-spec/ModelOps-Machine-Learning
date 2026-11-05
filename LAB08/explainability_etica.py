"""Lab08: explain one denied credit case and flag proxy-risk features."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import shap
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "08_dataset_credit_scoring_sintetico.csv"
OUTPUT = BASE / "output"

FEATURES = ["reddito_dichiarato", "insolvenze_passate", "anni_impiego", "cap_residenza"]
TARGET = "approvato"
PROXY_FEATURES = {"cap_residenza"}


def load_data(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    frame = pd.read_csv(path)
    required = FEATURES + [TARGET]
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    data = frame[required].apply(pd.to_numeric, errors="coerce")
    if data.isna().any().any() or data.empty:
        raise ValueError("Dataset contains missing or invalid numeric values")
    if set(data[TARGET].unique()) != {0, 1}:
        raise ValueError("Target must contain classes 0 and 1")
    return data[FEATURES], data[TARGET].astype(int)


def extract_shap_values(explainer: shap.TreeExplainer, row: pd.DataFrame, class_index: int) -> np.ndarray:
    raw = explainer.shap_values(row)
    if isinstance(raw, list):
        return np.asarray(raw[class_index])[0]
    arr = np.asarray(raw)
    if arr.ndim == 3:
        return arr[0, :, class_index]
    if arr.ndim == 2:
        return arr[0]
    raise ValueError(f"Unsupported SHAP format: {arr.shape}")


def main() -> None:
    x, y = load_data(DATA)
    x_train, x_test, y_train, _ = train_test_split(
        x, y, test_size=0.25, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(x_train, y_train)
    predicted = model.predict(x_test)
    proba = model.predict_proba(x_test)

    denied_index = np.flatnonzero(predicted == 0)
    if denied_index.size == 0:
        raise RuntimeError("No denied prediction found in test split")
    denied_class = int(np.flatnonzero(model.classes_ == 0)[0])
    chosen_pos = int(denied_index[np.argmax(proba[denied_index, denied_class])])
    chosen_row = x_test.iloc[[chosen_pos]]

    explainer = shap.TreeExplainer(model)
    contributions = extract_shap_values(explainer, chosen_row, denied_class)
    ranking = np.argsort(-np.abs(contributions))
    ranked_features = [FEATURES[int(i)] for i in ranking]
    flagged_proxy = [name for name in ranked_features if name in PROXY_FEATURES]

    OUTPUT.mkdir(exist_ok=True)
    result = {
        "decision": "deny",
        "confidence_deny": float(proba[chosen_pos, denied_class]),
        "row_index_in_test": chosen_row.index[0].item() if hasattr(chosen_row.index[0], "item") else int(chosen_row.index[0]),
        "input": {name: float(chosen_row.iloc[0][name]) for name in FEATURES},
        "shap_contributions": {FEATURES[i]: float(contributions[i]) for i in range(len(FEATURES))},
        "ranked_features": ranked_features,
        "proxy_features_found": flagged_proxy,
    }
    (OUTPUT / "explanation.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print("Denied case selected")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
