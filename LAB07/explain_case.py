"""Spiega la stessa classe dello stesso caso con SHAP e LIME."""
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from LAB06.monitor import OUTPUT as MONITOR_OUTPUT, batch, load_manifest
from LAB06.simulate import DATA, FEATURES, digest, now, write_json

OUTPUT = Path(__file__).resolve().parent / "output"


def normalize_shap(values, expected_value, class_index, n_features):
    """Formati supportati: lista per classe; (1,feature,classi); (1,feature)."""
    if isinstance(values, list):
        contributions = np.asarray(values[class_index])[0]
    else:
        values = np.asarray(values)
        if values.ndim == 3 and values.shape[0] == 1 and values.shape[1] == n_features:
            contributions = values[0, :, class_index]
        elif values.shape == (1, n_features):
            contributions = values[0]
        else:
            raise ValueError(f"Formato SHAP non supportato: {values.shape}; non indovinare la classe")
    base_values = np.asarray(expected_value).reshape(-1)
    base = float(base_values[class_index] if len(base_values) > 1 else base_values[0])
    if contributions.shape != (n_features,) or not np.isfinite(contributions).all():
        raise ValueError("Contributi SHAP non validi")
    return contributions, base


def select_cases(prediction, y, proba, limit=3):
    wrong = np.flatnonzero(prediction != y)
    ranked_wrong = wrong[np.argsort(-proba[wrong].max(axis=1))].tolist()
    # Se mancano errori, aggiunge casi corretti a bassa confidenza etichettati sospetti.
    uncertain = np.argsort(proba.max(axis=1)).tolist()
    selected = ranked_wrong[:limit]
    for index in uncertain:
        if len(selected) >= limit:
            break
        if index not in selected:
            selected.append(index)
    return selected


def main():
    manifest = load_manifest()
    monitoring = json.loads((MONITOR_OUTPUT / "monitoring.json").read_text(encoding="utf-8"))
    if monitoring["manifest_sha256"] != digest(DATA / "manifest.json") or monitoring["run_id"] != manifest["run_id"]:
        raise ValueError("Monitoring e dati appartengono a simulazioni diverse: rieseguire LAB06.monitor")
    signals = [e for e in monitoring["events"] if e["accuracy_alert"]]
    if not signals:
        raise SystemExit("Nessuna accuracy realmente sotto soglia: non si dichiara un degrado. Consultare LAB06/output/dashboard.md e documentare il problema.")
    signal = next((e for e in signals if e["state"] == "ALERT"), signals[0])
    row = next(r for r in manifest["batches"] if r["batch_id"] == signal["batch_id"])
    data = batch(row)
    x, y = data["x"], data["y"]
    bundle = joblib.load(DATA / "model.pkl")
    if bundle["version"] != signal["model_version"] or bundle["feature_names"] != FEATURES:
        raise ValueError("Identita modello incoerente")
    model = bundle["model"]
    prediction, proba = model.predict(x), model.predict_proba(x)
    if not np.array_equal(prediction, data["prediction"]) or not np.allclose(proba, data["proba"]):
        raise ValueError("Predizioni salvate diverse da quelle del modello caricato")
    measured_accuracy = float(np.mean(prediction == y))
    if not np.isclose(measured_accuracy, signal["accuracy"]) or not measured_accuracy < signal["accuracy_threshold"]:
        raise ValueError("Segnale di accuracy non confermato")
    OUTPUT.mkdir(exist_ok=True)
    print("SEGNALE MONITORING", json.dumps(signal, indent=2))
    print("Approfondimento: accuracy misurata sotto la soglia calibrata sullo storico sintetico")
    selected = select_cases(prediction, y, proba)
    cases = []
    for index in selected:
        wrong = bool(prediction[index] != y[index])
        case = {"case_id": f"{row['batch_id']}-row-{index}", "row_index": index,
                "features": dict(zip(FEATURES, x[index].tolist())),
                "predicted": int(prediction[index]), "simulated_true": int(y[index]),
                "confidence": float(proba[index].max()),
                "selection_reason": "Errore reale sulle etichette simulate, prioritario per confidenza" if wrong else "Corretto ma sospetto: confidenza relativamente bassa",
                "actually_wrong": wrong}
        cases.append(case)
        print(json.dumps(case, indent=2, ensure_ascii=False))
    write_json(OUTPUT / "cases.json", {"signal": signal, "cases": cases})
    # Import tardivo: in caso di problemi di installazione restano segnale e casi.
    import shap
    from lime.lime_tabular import LimeTabularExplainer

    index = selected[0]
    class_index = int(np.flatnonzero(model.classes_ == prediction[index])[0])
    class_label = int(model.classes_[class_index])
    explainer = shap.TreeExplainer(model, feature_perturbation="tree_path_dependent", model_output="raw")
    values = explainer.shap_values(x[index:index + 1])
    contributions, base = normalize_shap(values, explainer.expected_value, class_index, len(FEATURES))
    reconstructed_probability = base + float(contributions.sum())
    if not np.isclose(reconstructed_probability, proba[index, class_index], atol=1e-5):
        raise ValueError("SHAP non ricostruisce la probabilita della classe scelta: interrompere e verificare formato/output")
    explanation = shap.Explanation(values=contributions, base_values=base, data=x[index], feature_names=FEATURES)
    shap.plots.waterfall(explanation, show=False)
    plt.gcf().set_size_inches(11, 7)
    plt.title(f"SHAP - {cases[0]['case_id']} - classe {class_label} (1=credito approvato sintetico)")
    plt.tight_layout()
    plt.savefig(OUTPUT / "shap_waterfall.png", dpi=160, bbox_inches="tight")
    plt.close("all")
    with np.load(DATA / "training.npz") as train:
        training_x = train["x"].copy()
    lime_explainer = LimeTabularExplainer(training_x, feature_names=FEATURES,
                                         class_names=[f"classe {c}" for c in model.classes_],
                                         mode="classification", random_state=42)
    lime_exp = lime_explainer.explain_instance(x[index], model.predict_proba,
                                              labels=(class_index,), num_features=len(FEATURES), num_samples=5000)
    weights = sorted(lime_exp.as_map()[class_index], key=lambda pair: abs(pair[1]), reverse=True)
    lime_rules = lime_exp.as_list(label=class_index)
    lime_exp.save_to_file(str(OUTPUT / "lime.html"), labels=(class_index,))
    fig = lime_exp.as_pyplot_figure(label=class_index)
    fig.set_size_inches(11, 6)
    fig.suptitle(f"LIME - {cases[0]['case_id']} - classe {class_label}")
    fig.tight_layout()
    fig.savefig(OUTPUT / "lime.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    shap_ranking = np.argsort(-np.abs(contributions))
    shap_top, lime_top = FEATURES[int(shap_ranking[0])], FEATURES[int(weights[0][0])]
    comparison = {
        "timestamp": now(), "signal": signal, "case": cases[0], "explained_class": class_label,
        "monitoring_sha256": digest(MONITOR_OUTPUT / "monitoring.json"),
        "model_sha256": manifest["files_sha256"]["model.pkl"],
        "shap_version": shap.__version__, "shap_base_probability": base,
        "shap_reconstructed_probability": reconstructed_probability,
        "shap_contributions": dict(zip(FEATURES, contributions.tolist())),
        "lime_weights": {FEATURES[int(i)]: float(w) for i, w in weights},
        "lime_rules": lime_rules, "lime_local_fit_r2": float(lime_exp.score),
        "shap_top": shap_top, "lime_top": lime_top, "same_top_feature": shap_top == lime_top,
        "top_feature_drift": {name: {"psi": signal["feature_psi"][name],
                                      "threshold": monitoring["calibration"]["psi_thresholds"][name],
                                      "above_threshold": signal["feature_psi"][name] > monitoring["calibration"]["psi_thresholds"][name]}
                              for name in sorted({shap_top, lime_top})},
        "limits": "Associazione, non causalita. SHAP spiega il modello; LIME e un'approssimazione locale con perturbazioni, R2 da verificare. Scenario con eta e policy modificate insieme.",
    }
    write_json(OUTPUT / "comparison.json", comparison)
    print("CONTRIBUTI SHAP", comparison["shap_contributions"])
    print("REGOLE LIME", lime_rules, "R2 locale=", lime_exp.score)
    print("CONFRONTO", json.dumps(comparison, indent=2, ensure_ascii=False))
    summary = f"""# Evidenza generata dall'esecuzione manuale

Timestamp: {comparison['timestamp']}. Modello: {signal['model_version']}.
Segnale: accuracy {measured_accuracy:.6f} < {signal['accuracy_threshold']:.6f}.

| Segnale monitoring | Batch | Caso | Feature SHAP | Feature LIME | Interpretazione | Azione |
|---|---|---|---|---|---|---|
| Accuracy sotto soglia | {row['batch_id']} | {cases[0]['case_id']} | {shap_top} | {lime_top} | Concordanza top: {shap_top == lime_top}; associazione da verificare | Audit feature e policy |

## Nota business
Nel batch sintetico {row['batch_id']} il modello ha un'accuracy sotto la soglia storica.
Sono stati isolati {len(cases)} casi; il caso {cases[0]['case_id']} e stato spiegato per la classe {class_label}.
Richiedono attenzione {shap_top} (SHAP) e {lime_top} (LIME); il dettaglio PSI e in comparison.json.
Il rischio operativo simulato e approvare o rifiutare credito in modo errato.
Comunicare a responsabile rischio credito, responsabile dati e Data Scientist on-call.
Verificare qualita delle feature, cambiamenti di policy, etichette e prestazioni per sottogruppi;
confrontare un modello precedente sugli stessi batch prima di proporre rollback o riaddestramento.
Non e dimostrato che il drift sia la causa del degrado: nella simulazione cambia anche la policy delle etichette.
Nessun messaggio esterno inviato; nessuna decisione automatica di credito reale.
"""
    (OUTPUT / "summary.md").write_text(summary, encoding="utf-8")
    print(f"Grafici, HTML e nota business: {OUTPUT}")


if __name__ == "__main__":
    main()
