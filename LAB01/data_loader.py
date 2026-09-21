"""Lettura del dataset CSV, separata da train.py."""
import csv
from pathlib import Path

# Percorsi relativi a questo file (non alla cartella da cui lanci lo script)
BASE_DIR = Path(__file__).resolve().parent
CSV_DIR = BASE_DIR / "csv"
DATA_PATH = CSV_DIR / "data.csv"  # <- unica riga da cambiare tra un progetto e l'altro


def leggi_csv(percorso=DATA_PATH, tipi=None):
    """Legge un CSV e restituisce una lista di dict (una riga = un dict).

    tipi: conversioni opzionali per colonna, es. {"f1": float, "label": int}
    """
    percorso = Path(percorso)
    if not percorso.is_file():
        raise FileNotFoundError(f"File CSV non trovato: {percorso}")

    tipi = tipi or {}
    with percorso.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        assenti = [c for c in tipi if c not in (reader.fieldnames or [])]
        if assenti:
            raise ValueError(f"Colonne non presenti nel CSV: {assenti}")
        righe = [{k: tipi.get(k, str)(v) for k, v in r.items()} for r in reader]

    if not righe:
        raise ValueError(f"Il file {percorso.name} non contiene righe di dati")
    return righe


if __name__ == "__main__":
    righe = leggi_csv(tipi={"f1": float, "f2": float, "label": int})
    print(f"{len(righe)} righe lette da {DATA_PATH}")
    print("prima riga:", righe[0])
