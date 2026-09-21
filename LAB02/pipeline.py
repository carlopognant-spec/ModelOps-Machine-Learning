"""Pipeline LAB02: validate, train e gate."""
import argparse
import math
import pickle
import random
import subprocess
import sys
from pathlib import Path

from data_loader import DATA_PATH, leggi_csv

FEATURES = ("f1", "f2")
TARGET = "label"
TEST_RATIO = 0.2
EPOCHS = 2_000
LEARNING_RATE = 0.1
DEFAULT_SEED = 7
DEFAULT_MODEL = "model.pkl"
DEFAULT_THRESHOLD = 0.75
BASE_DIR = Path(__file__).resolve().parent


def carica_dati(percorso=DATA_PATH):
    return leggi_csv(percorso, tipi={"f1": float, "f2": float, "label": int})


def validate(percorso=DATA_PATH):
    try:
        subprocess.run(
            [sys.executable, "-m", "pytest", str(BASE_DIR / "tests"), "-q"],
            cwd=BASE_DIR,
            check=True,
        )
        righe = carica_dati(percorso)
        valori_validi = {riga[TARGET] for riga in righe} <= {0, 1}
        if not valori_validi or len(righe) < 2:
            raise ValueError("servono almeno due righe e label 0/1")
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError) as errore:
        print(f"[VALIDATE] FAIL: {errore}")
        raise SystemExit(1) from errore
    print("[VALIDATE] PASS: schema dati verificato")


def standardizza(caratteristiche, riferimenti=None):
    if riferimenti is None:
        medie = [sum(riga[i] for riga in caratteristiche) / len(caratteristiche)
                 for i in range(len(FEATURES))]
        deviazioni = [
            math.sqrt(sum((riga[i] - medie[i]) ** 2 for riga in caratteristiche)
                      / len(caratteristiche))
            for i in range(len(FEATURES))
        ]
        riferimenti = (medie, [deviazione or 1.0 for deviazione in deviazioni])

    medie, deviazioni = riferimenti
    scalate = [[(valore - medie[i]) / deviazioni[i]
                for i, valore in enumerate(riga)] for riga in caratteristiche]
    return scalate, riferimenti


def sigmoide(valore):
    return 1 / (1 + math.exp(-valore))


def train(seed, percorso_modello, percorso_dati=DATA_PATH):
    righe = list(carica_dati(percorso_dati))
    random.Random(seed).shuffle(righe)
    numero_test = max(1, round(len(righe) * TEST_RATIO))
    righe_test = righe[:numero_test]
    righe_train = righe[numero_test:]

    x_train = [[riga[nome] for nome in FEATURES] for riga in righe_train]
    y_train = [riga[TARGET] for riga in righe_train]
    x_test = [[riga[nome] for nome in FEATURES] for riga in righe_test]
    y_test = [riga[TARGET] for riga in righe_test]
    x_train, riferimenti = standardizza(x_train)
    x_test, _ = standardizza(x_test, riferimenti)

    pesi = [0.0] * len(FEATURES)
    bias = 0.0
    for _ in range(EPOCHS):
        gradienti = [0.0] * len(pesi)
        gradiente_bias = 0.0
        for riga, obiettivo in zip(x_train, y_train):
            probabilita = sigmoide(bias + sum(peso * valore for peso, valore in zip(pesi, riga)))
            errore = probabilita - obiettivo
            for indice, valore in enumerate(riga):
                gradienti[indice] += errore * valore
            gradiente_bias += errore
        numero_righe = len(x_train)
        pesi = [peso - LEARNING_RATE * gradiente / numero_righe
                for peso, gradiente in zip(pesi, gradienti)]
        bias -= LEARNING_RATE * gradiente_bias / numero_righe

    previsioni = [int(sigmoide(bias + sum(peso * valore for peso, valore in zip(pesi, riga))) >= 0.5)
                  for riga in x_test]
    accuracy = sum(reale == previsto for reale, previsto in zip(y_test, previsioni)) / len(y_test)
    modello = {"pesi": pesi, "bias": bias, "riferimenti": riferimenti,
               "seed": seed, "accuracy": accuracy}
    with open(percorso_modello, "wb") as file_modello:
        pickle.dump(modello, file_modello)
    print(f"[TRAIN] accuracy={accuracy:.3f} model={percorso_modello}")


def gate(percorso_modello, soglia):
    with open(percorso_modello, "rb") as file_modello:
        modello = pickle.load(file_modello)
    accuracy = modello["accuracy"]
    esito = "PROMOSSO" if accuracy >= soglia else "RESPINTO"
    print(f"[GATE] accuracy={accuracy:.3f} soglia={soglia:.2f} -> {esito}")
    if esito == "RESPINTO":
        raise SystemExit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=("validate", "train", "gate"), required=True)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--out", default=DEFAULT_MODEL)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--data", default=str(DATA_PATH))
    args = parser.parse_args()

    if args.stage == "validate":
        validate(args.data)
    elif args.stage == "train":
        train(args.seed, args.out, args.data)
    else:
        gate(args.model, args.threshold)


if __name__ == "__main__":
    main()
