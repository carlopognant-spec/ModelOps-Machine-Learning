---
ID: 2
Origin: 2
UUID: 7a4d2e91
Status: Active
---

# Implementazione LAB03 API, Docker e deploy

## Plan Reference

- Piano: `agent-output/planning/002-lab03-api-docker-deploy.md`
- Target release: `N/A`, confermato dall'utente perché il progetto didattico non usa release.

## Date

2026-09-23

## Changelog

| Date | Handoff | Request | Summary |
|---|---|---|---|
| 2026-09-23 | Planner -> Implementer | Eseguire piano LAB03 | Verificato il materiale esistente e completato il contratto di errore dell'artefatto modello. |
| 2026-09-23 | QA -> Implementer | Correggere input non finiti | Applicato `FiniteFloat` a `f1` e `f2`; `NaN` e Infinity ora restituiscono `422`. |

## Implementation Summary

LAB03 espone il modello riusato da LAB02 tramite FastAPI, con contratto `/health` e `/predict`, payload numerico e risposte di errore documentate. Il servizio ora richiede esplicitamente `model.pkl`: non esegue training implicito alla prima richiesta e restituisce `500` controllato per modello assente o malformato. Il Dockerfile resta minimale e coerente con il servizio.

## Milestones Completed

- [x] Formalizzato il riuso di modello, preprocessing, loader e dataset di LAB02.
- [x] Verificati input valido, input non valido, health e output del modello.
- [x] Corretto il comportamento su modello mancante e artefatto malformato.
- [x] Verificato manualmente il Dockerfile.
- [x] Aggiornato il report con fallback Docker e cleanup.
- [x] Confermato `Target Release: N/A`.
- [x] Rifiutati valori non finiti nel payload API con status `422`.

## Files Modified

| Path | Changes |
|---|---|
| `LAB03/service.py` | Il modello è un prerequisito; aggiunta validazione della struttura, gestione controllata degli errori di caricamento e campi Pydantic `FiniteFloat`. |
| `LAB03/tests/test_service.py` | Aggiunti test per health, modello mancante, modello malformato, modello parziale e input non finiti. |
| `LAB03/LAB03_REPORT.md` | Aggiornati risultati, contratto sul modello e cleanup. |
| `agent-output/planning/002-lab03-api-docker-deploy.md` | Stato In Progress, decisione release e changelog. |

## Files Reused/Created Before Plan Execution

| Path | Purpose |
|---|---|
| `LAB03/pipeline.py` | Preprocessing e modello derivati da LAB02. |
| `LAB03/data_loader.py` | Loader derivato da LAB02. |
| `LAB03/csv/data.csv` | Dataset sintetico derivato da LAB02. |
| `LAB03/model.pkl` | Artefatto modello necessario al runtime. |
| `LAB03/Dockerfile` | Container minimale FastAPI/Uvicorn. |
| `LAB03/requirements.txt` | Dipendenze pinned del servizio. |

## Code Quality Validation

- [x] `python -m pytest LAB03/tests -q`: `8 passed`.
- [x] `python -m compileall -q data_loader.py pipeline.py service.py tests`: pass.
- [x] Diagnostica VS Code sui file Python: nessun errore.
- [x] Dockerfile manualmente validato.
- [x] Cache Python e pytest rimosse.
- [x] Nessuna immagine o container Docker lasciato.
- [ ] `docker build`: non eseguito perché il daemon Docker Desktop non era attivo.

## TDD Compliance

| Function/Class | Test File | Test Written First? | Failure Verified? | Failure Reason | Pass After Impl? |
|---|---|---|---|---|---|
| `load_model()` missing artifact behavior | `LAB03/tests/test_service.py` | Yes | Yes | AssertionError: missing model returned `200` after implicit training | Yes |
| `load_model()` malformed artifact behavior | `LAB03/tests/test_service.py` | Yes | Yes | Unhandled `RuntimeError` escaped FastAPI handler | Yes |
| `/health` endpoint contract | `LAB03/tests/test_service.py` | Yes | N/A | Existing endpoint; coverage added | Yes |

## Test Coverage

- Valid prediction: `200`, binary `label`, numeric `score`.
- Invalid payload: `422`.
- Health endpoint: `200` and `{"status": "ok"}`.
- Missing model: `500`, no implicit training or artifact creation.
- Malformed model: `500`, no traceback leaked through the API.
- Non-finite features: `422` per `NaN`, `Infinity` e `-Infinity`.

## Test Execution Results

| Command | Result |
|---|---|
| `python -m pytest LAB03/tests -q` | PASS, `8 passed` |
| `python -m compileall -q data_loader.py pipeline.py service.py tests` | PASS |
| Dockerfile manual validation | PASS |
| `docker build -t lab03-scoring .` | BLOCKED: Docker Desktop daemon unavailable |
| Cleanup of Python/pytest caches | PASS |

## Outstanding Items

- Docker image build and runtime smoke test remain pending until Docker Desktop daemon is started.
- Production use with healthcare data requires compliance review, authentication, secret management, private networking, encryption and retention policy.
- No remote CI or cloud endpoint was created.
- QA regression for non-finite features passed after the `FiniteFloat` fix.

## Next Steps

QA should rerun the eight tests and, when Docker is available, build and start the image for `/health` and `/predict` smoke tests. UAT can then review the deployment decision and API contract against the professor's checklist.