---
ID: 2
Origin: 2
UUID: 7a4d2e91
Status: QA Failed
---

# QA Report: LAB03 API, Docker e strategie di deploy

**Plan Reference**: `agent-output/planning/002-lab03-api-docker-deploy.md`
**QA Status**: QA Failed
**QA Specialist**: qa

## Changelog

| Date | Agent Handoff | Request | Summary |
|---|---|---|---|
| 2026-09-23 | Implementer/Reviewer -> QA | Verificare la strategia di test delle modifiche LAB03 | Eseguita suite QA estesa; 6 test passano e 2 falliscono su feature non finite. Modello parzialmente valido gestito correttamente. |

## Timeline

- **Test Strategy Started**: 2026-09-23
- **Test Strategy Completed**: 2026-09-23
- **Implementation Received**: 2026-09-23
- **Testing Started**: 2026-09-23
- **Testing Completed**: 2026-09-23
- **Final Status**: QA Failed

## Phase 1: Test Strategy

### User-facing risks

- Il servizio deve esporre `/health` e `/predict` con risposte coerenti.
- Payload mancanti, non numerici o non finiti devono produrre un errore 4xx senza traceback.
- Il modello è un prerequisito: assenza o struttura invalida devono produrre `500` controllato senza training implicito.
- L'artefatto parzialmente valido non deve raggiungere la fase di scoring.
- Il Dockerfile deve essere coerente con porta, comando e file runtime.
- Nessun dataset reale o dato sanitario deve essere richiesto dai test.

### Test types

- **Contract/API:** `/health`, predizione valida, payload non numerico, feature non finite.
- **Failure-path:** modello mancante, modello malformato e modello parzialmente valido.
- **Integration/manual:** coerenza del Dockerfile e cleanup; build Docker bloccata se il daemon non è disponibile.

### Infrastructure

- `pytest`, FastAPI `TestClient` e dipendenze già dichiarate in `LAB03/requirements.txt`.
- Nessuna nuova dipendenza QA necessaria.
- Docker CLI disponibile, Docker Desktop daemon non disponibile; build container non eseguibile in questo ambiente.

## TDD Compliance Gate

Il documento d'implementazione contiene una tabella `TDD Compliance` per `load_model()` e `/health`. Il gate formale è **PASS** per le modifiche dichiarate. I test QA aggiunti successivamente coprono rischi emersi dalla code review.

## Test Coverage Analysis

| Area | Test | Risultato |
|---|---|---|
| `/health` | `test_health_reports_service_status` | PASS |
| Predizione valida | `test_predict_returns_label_and_score` | PASS |
| Payload non numerico | `test_predict_rejects_invalid_payload` | PASS |
| Modello mancante | `test_predict_reports_missing_model_without_training` | PASS |
| Modello malformato | `test_predict_reports_malformed_model` | PASS |
| Modello parzialmente valido | `test_predict_reports_model_with_missing_scoring_fields` | PASS |
| Feature `NaN` | `test_predict_rejects_non_finite_features[payload0]` | FAIL |
| Feature `Infinity` | `test_predict_rejects_non_finite_features[payload1]` | FAIL |

## Test Execution Results

### Unit/API tests

- **Command**: `Push-Location LAB03; python -m pytest tests -q --tb=short; Pop-Location`
- **Status**: FAIL
- **Result**: `6 passed, 2 failed`

### Failing scenarios

1. **NaN input**: the request reaches the endpoint and produces a `ValueError` while FastAPI serializes a `NaN` response. The client receives an exception rather than a `422` JSON validation response.
2. **Infinity input**: Pydantic accepts the value as a float and the endpoint returns `200`, violating the contract that non-finite features are invalid.

### Positive and negative behavior

- Valid prediction: PASS, `200` with `label` and `score`.
- Invalid string payload: PASS, `422`.
- Missing model: PASS, `500`, no model is created.
- Malformed model: PASS, `500` controlled.
- Partial model with valid accuracy: PASS, `500` controlled because scoring fields are missing.
- Non-finite features: FAIL, contract not enforced.

### Docker and static checks

- Dockerfile manual validation: PASS for base image, dependency installation, copied runtime files, port and Uvicorn command.
- Docker build: NOT EXECUTED; Docker Desktop daemon unavailable.
- Python diagnostics: no errors reported for `service.py` or tests.
- Temporary Python/pytest caches removed after execution.
- No Docker image or container created.

## Findings

### QA failure: non-finite API features are not rejected

**Severity:** Medium

`PredictionRequest` types `f1` and `f2` as plain `float`, which accepts `NaN` and infinity. `NaN` can reach the response path and cause a serialization `ValueError`; infinity is accepted and can produce a `200` response. Both violate the documented API contract for invalid input and can poison scoring results.

**Required fix:** enforce finite numeric values at request validation, for example with a finite-number constraint/validator in the Pydantic model. Add assertions that both `NaN` and infinity return `422` with a JSON error body and no traceback.

### Covered review risk: partial model structure

The QA test with `{"accuracy": 0.9}` passes because the endpoint catches the missing scoring fields and returns `500`. This is behaviorally acceptable, though `load_model()` still validates the structure lazily rather than eagerly.

### Deferred production security risk

The service has no authentication, authorization or TLS. The report correctly frames these as production requirements, but the current container must remain explicitly didactic and must not be deployed with real healthcare data without an API gateway/reverse proxy and security controls.

## QA Decision

**QA FAILED.** The core valid workflow and model failure paths are covered, but non-finite user input can either escape as `200` or cause an unhandled serialization exception. Approval is blocked until finite-number validation is added and the complete suite is green.

Required implementer handoff:

1. Reject `NaN` and positive/negative infinity at request validation.
2. Rerun `python -m pytest LAB03/tests -q` and confirm all tests pass.
3. Confirm no traceback is exposed for invalid JSON numeric values.
4. Keep Docker build status documented as blocked until Docker Desktop is available.

Handing off to uat agent for value delivery validation
