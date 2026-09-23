"""Lettura del dataset CSV usato dal servizio LAB03."""
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_DIR = BASE_DIR / "csv"
DATA_PATH = CSV_DIR / "data.csv"


def leggi_csv(percorso=DATA_PATH, tipi=None):
    """Legge un CSV e restituisce una lista di dizionari convertiti."""
    percorso = Path(percorso)
    if not percorso.is_file():
        raise FileNotFoundError(f"File CSV non trovato: {percorso}")

    tipi = tipi or {}
    with percorso.open(newline="", encoding="utf-8-sig") as file_csv:
        reader = csv.DictReader(file_csv)
        assenti = [colonna for colonna in tipi if colonna not in (reader.fieldnames or [])]
        if assenti:
            raise ValueError(f"Colonne non presenti nel CSV: {assenti}")
        righe = [{chiave: tipi.get(chiave, str)(valore) for chiave, valore in riga.items()}
                 for riga in reader]

    if not righe:
        raise ValueError(f"Il file {percorso.name} non contiene righe di dati")
    return righe