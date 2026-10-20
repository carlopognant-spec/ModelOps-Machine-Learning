"""Caricamento all'avvio: errori di identita impediscono il serving."""
from contextlib import asynccontextmanager
import json
import math

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, field_validator

from LAB04.common import BASE, load_verified


@asynccontextmanager
async def lifespan(app):
    registry = json.loads((BASE / "registry.json").read_text(encoding="utf-8"))
    rows = [r for r in registry["versions"] if r["version"] == registry["active_version"]]
    if len(rows) != 1 or rows[0]["status"] != "promosso" or rows[0]["accuracy"] < registry["threshold"]:
        raise ValueError("Versione attiva assente o non promossa")
    app.state.bundle = load_verified(rows[0])
    print(f"Modello caricato: {app.state.bundle['version']}; path={BASE / rows[0]['artifact']}")
    yield


app = FastAPI(title="LAB04 Wine Serving", lifespan=lifespan)


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    features: list[float]

    @field_validator("features", mode="before")
    @classmethod
    def finite_numeric(cls, values):
        if not isinstance(values, list) or not all(
            type(v) in (int, float) and math.isfinite(v) for v in values
        ):
            raise ValueError("Usare una lista di numeri finiti, senza stringhe o booleani")
        return values


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    # Non serializzare NaN/Infinity o eccezioni incluse nell'input di Pydantic.
    return JSONResponse(status_code=422, content={"detail": "Input JSON non valido: features numeriche finite obbligatorie"})


@app.get("/health")
def health():
    return {"status": "ok", "model_version": app.state.bundle["version"]}


@app.post("/predict")
def predict(payload: PredictRequest):
    bundle = app.state.bundle
    if len(payload.features) != len(bundle["feature_names"]):
        raise HTTPException(422, f"Attese {len(bundle['feature_names'])} feature in ordine wine")
    return {"prediction": int(bundle["model"].predict([payload.features])[0]),
            "model_version": bundle["version"]}
