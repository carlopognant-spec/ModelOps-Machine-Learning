"""API di scoring del modello LAB02 per il deploy LAB03."""
import math
import pickle
from collections.abc import Mapping
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, FiniteFloat

from pipeline import sigmoide, standardizza

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model.pkl"

app = FastAPI(title="LAB03 Healthcare Scoring API", version="1.0.0")


class PredictionRequest(BaseModel):
    f1: FiniteFloat = Field(..., description="Prima caratteristica numerica finita")
    f2: FiniteFloat = Field(..., description="Seconda caratteristica numerica finita")


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"modello non trovato: {MODEL_PATH}")
    with MODEL_PATH.open("rb") as file_model:
        modello = pickle.load(file_model)
    if not isinstance(modello, Mapping):
        raise RuntimeError("artefatto modello non valido: struttura inattesa")
    accuracy = modello.get("accuracy")
    if isinstance(accuracy, bool) or not isinstance(accuracy, (int, float)) or not math.isfinite(accuracy):
        raise RuntimeError("artefatto modello non valido")
    return modello


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(payload: PredictionRequest):
    try:
        modello = load_model()
        caratteristiche, _ = standardizza([[payload.f1, payload.f2]], modello["riferimenti"])
        score = sigmoide(modello["bias"] + sum(
            peso * valore for peso, valore in zip(modello["pesi"], caratteristiche[0])
        ))
        return {"label": int(score >= 0.5), "score": round(score, 6)}
    except (KeyError, TypeError, ValueError, OSError, RuntimeError,
            pickle.PickleError, EOFError) as errore:
        return JSONResponse(status_code=500, content={"detail": f"modello non disponibile: {errore}"})