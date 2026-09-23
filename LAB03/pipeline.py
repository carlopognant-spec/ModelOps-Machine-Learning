"""Modello e preprocessing importati da LAB02 per il servizio API."""
import math
import pickle
import random
from pathlib import Path

from data_loader import DATA_PATH, leggi_csv

FEATURES = ("f1", "f2")
TARGET = "label"
TEST_RATIO = 0.2
EPOCHS = 2_000
LEARNING_RATE = 0.1
DEFAULT_SEED = 7
BASE_DIR = Path(__file__).resolve().parent


def carica_dati(percorso=DATA_PATH):
    return leggi_csv(percorso, tipi={"f1": float, "f2": float, "label": int})


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


def train(percorso_modello, percorso_dati=DATA_PATH, seed=DEFAULT_SEED):
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

    accuracy = sum(
        reale == int(sigmoide(bias + sum(peso * valore for peso, valore in zip(pesi, riga))) >= 0.5)
        for riga, reale in zip(x_test, y_test)
    ) / len(y_test)
    modello = {"pesi": pesi, "bias": bias, "riferimenti": riferimenti,
               "seed": seed, "accuracy": accuracy}
    with open(percorso_modello, "wb") as file_modello:
        pickle.dump(modello, file_modello)
    return modello