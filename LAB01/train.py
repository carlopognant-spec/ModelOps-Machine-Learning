"""Addestramento di un classificatore binario sui dati di LAB01.

Il modello e' una regressione logistica implementata con la libreria standard
di Python, così ogni passaggio dell'addestramento resta visibile.
"""
import math
import random
import argparse
import pickle

from data_loader import DATA_PATH, leggi_csv


FEATURE_NAMES = ("f1", "f2")
TARGET_NAME = "label"
TEST_RATIO = 0.2
LEARNING_RATE = 0.1
EPOCHS = 2_000
RANDOM_SEED = 42


def dividi_dati(righe, rapporto_test=TEST_RATIO, seme=RANDOM_SEED):
	"""Mescola le righe in modo riproducibile e crea train/test set."""
	righe = list(righe)
	random.Random(seme).shuffle(righe)
	numero_test = max(1, round(len(righe) * rapporto_test))
	return righe[numero_test:], righe[:numero_test]


def prepara_dati(righe):
	"""Trasforma i dizionari del CSV in coppie (feature, target)."""
	caratteristiche = [[riga[nome] for nome in FEATURE_NAMES] for riga in righe]
	obiettivi = [riga[TARGET_NAME] for riga in righe]
	return caratteristiche, obiettivi


def standardizza(caratteristiche, riferimenti=None):
	"""Scala le feature usando media e deviazione calcolate sul train set."""
	if riferimenti is None:
		medie = [sum(riga[i] for riga in caratteristiche) / len(caratteristiche)
				 for i in range(len(FEATURE_NAMES))]
		deviazioni = [
			math.sqrt(sum((riga[i] - medie[i]) ** 2 for riga in caratteristiche)
					  / len(caratteristiche))
			for i in range(len(FEATURE_NAMES))
		]
		deviazioni = [deviazione or 1.0 for deviazione in deviazioni]
		riferimenti = (medie, deviazioni)

	medie, deviazioni = riferimenti
	scalate = [
		[(valore - medie[i]) / deviazioni[i] for i, valore in enumerate(riga)]
		for riga in caratteristiche
	]
	return scalate, riferimenti


def sigmoide(valore):
	"""Converte un punteggio numerico in una probabilità tra 0 e 1."""
	return 1 / (1 + math.exp(-valore))


def addestra(caratteristiche, obiettivi, tasso=LEARNING_RATE, epoche=EPOCHS):
	"""Impara pesi e bias minimizzando l'errore della regressione logistica."""
	pesi = [0.0] * len(caratteristiche[0])
	bias = 0.0

	for _ in range(epoche):
		gradienti_pesi = [0.0] * len(pesi)
		gradiente_bias = 0.0

		for riga, obiettivo in zip(caratteristiche, obiettivi):
			punteggio = bias + sum(peso * valore for peso, valore in zip(pesi, riga))
			probabilita = sigmoide(punteggio)
			errore = probabilita - obiettivo

			for i, valore in enumerate(riga):
				gradienti_pesi[i] += errore * valore
			gradiente_bias += errore

		numero_righe = len(caratteristiche)
		pesi = [
			peso - tasso * gradiente / numero_righe
			for peso, gradiente in zip(pesi, gradienti_pesi)
		]
		bias -= tasso * gradiente_bias / numero_righe

	return pesi, bias


def predici(caratteristiche, pesi, bias):
	"""Restituisce la classe prevista per ogni riga."""
	previsioni = []
	for riga in caratteristiche:
		punteggio = bias + sum(peso * valore for peso, valore in zip(pesi, riga))
		previsioni.append(int(sigmoide(punteggio) >= 0.5))
	return previsioni


def accuratezza(reali, previste):
	"""Calcola la proporzione di previsioni corrette."""
	corretti = sum(reale == prevista for reale, prevista in zip(reali, previste))
	return corretti / len(reali)


def main():
	"""Esegue tutti gli step della pipeline di training."""
	parser = argparse.ArgumentParser(description="Addestra il modello di LAB01.")
	parser.add_argument("--seed", type=int, default=RANDOM_SEED)
	parser.add_argument("--out", default="model.pkl")
	args = parser.parse_args()

	righe = leggi_csv(DATA_PATH, tipi={"f1": float, "f2": float, "label": int})
	righe_train, righe_test = dividi_dati(righe, seme=args.seed)

	x_train, y_train = prepara_dati(righe_train)
	x_test, y_test = prepara_dati(righe_test)
	x_train, riferimenti = standardizza(x_train)
	x_test, _ = standardizza(x_test, riferimenti)

	pesi, bias = addestra(x_train, y_train)
	previsioni = predici(x_test, pesi, bias)
	accuracy = accuratezza(y_test, previsioni)
	modello = {
		"pesi": pesi,
		"bias": bias,
		"riferimenti": riferimenti,
		"seed": args.seed,
	}
	with open(args.out, "wb") as file_modello:
		pickle.dump(modello, file_modello)

	print(f"Righe totali: {len(righe)}")
	print(f"Training: {len(x_train)} righe | Test: {len(x_test)} righe")
	print(f"Accuratezza sul test: {accuracy:.1%}")
	print(f"Pesi appresi: {pesi} | Bias: {bias:.3f}")
	print(f"run: seed={args.seed} accuracy={accuracy:.3f} model={args.out}")


if __name__ == "__main__":
	main()
