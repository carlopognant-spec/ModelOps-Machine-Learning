---
ID: 1
Origin: 1
UUID: c10f1ccd
Status: QA Failed
---

# QA Report: LAB02 CI/CD e pipeline ML

**Plan Reference**: `agent-output/planning/001-lab02-ci-cd-pipeline.md`
**QA Status**: QA Failed
**QA Specialist**: qa

## Changelog

| Date | Agent Handoff | Request | Summary |
|---|---|---|---|
| 2026-09-23 | Implementer/Reviewer -> QA | Verificare la strategia di test delle modifiche implementate e revisionate | Eseguita strategia QA, aggiunti test per i rischi della review, 5/6 test passano; il gate su modello malformato produce ancora traceback. |

## Timeline

- **Test Strategy Started**: 2026-09-23
- **Test Strategy Completed**: 2026-09-23
- **Implementation Received**: 2026-09-23
- **Testing Started**: 2026-09-23
- **Testing Completed**: 2026-09-23
- **Final Status**: QA Failed

## Phase 1: Test Strategy (Pre-Implementation)

### User-facing risks covered

- Un dataset non valido deve bloccare il training prima della creazione del modello.
- Il comando deve funzionare dalla root del repository, come documentato.
- Un modello mancante o non leggibile deve produrre un fallimento comprensibile e un exit code non zero.
- Un modello sotto soglia non deve essere promosso.
- Un artefatto serializzato ma strutturalmente invalido non deve generare traceback non gestito.
- Il cleanup non deve lasciare modelli temporanei nel workspace.

### Test types and coverage

- **Unit/behavior:** validazione dati, training bloccato, gate su modello mancante, gate su modello malformato e gate sotto soglia.
- **Integration:** sequenza dalla root `pytest -> validate -> train -> gate` con dataset valido.
- **Negative workflow:** CSV alternativo privo di `label`, verifica exit code e assenza del modello.
- **Manual/evidence review:** coerenza tra report, `run.log`, comandi PowerShell e comportamento effettivo.

### Testing infrastructure

- Framework esistente: `pytest`.
- Nessuna nuova dipendenza necessaria.
- Nessun servizio CI remoto presente o richiesto dal piano.
- Coverage percentage non disponibile: il progetto non contiene configurazione `pytest-cov`.

### Acceptance criteria

- La suite esegue dalla root senza import error.
- Il training non crea output su dati invalidi.
- Il gate gestisce modello mancante, malformato e sotto soglia con exit code non zero e output comprensibile.
- La run valida produce una promozione con soglia numerica esplicita.
- I test negativi non modificano il dataset sorgente e non lasciano artefatti.

## Phase 2: Test Execution Results

### TDD Compliance Gate

Il documento d’implementazione contiene la tabella `TDD Compliance` con righe per tutte le nuove funzioni/modifiche dichiarate: `train()` e `gate()`. Entrambe riportano test-first, failure verificata e pass dopo implementazione. Gate TDD: **PASS**.

### Test Coverage Analysis

| File | Function/Class | Test File | Test Case | Coverage Status |
|---|---|---|---|---|
| `LAB02/pipeline.py` | `validate()` / `train()` | `LAB02/tests/test_pipeline.py` | invalid dataset before model creation | COVERED |
| `LAB02/pipeline.py` | `gate()` missing artifact | `LAB02/tests/test_pipeline.py` | missing model | COVERED |
| `LAB02/pipeline.py` | `gate()` threshold decision | `LAB02/tests/test_pipeline.py` | below threshold | COVERED |
| `LAB02/pipeline.py` | `gate()` malformed accuracy | `LAB02/tests/test_pipeline.py` | non-numeric accuracy | FAILING / DEFECT EXPOSED |
| `LAB02/tests/test_data.py` | dataset schema and target | `LAB02/tests/test_data.py` | expected columns and values | COVERED for default dataset only |
| `LAB02/run_pipeline.sh` | stage ordering/stop-on-failure | `LAB02/run.log` and manual workflow | valid sequence | PARTIAL; shell script was not executable in the Windows PowerShell environment |

### Tests Added During QA

Added to `LAB02/tests/test_pipeline.py`:

- `test_gate_rejects_malformed_model`
- `test_gate_rejects_accuracy_below_threshold`

The first test is intentionally red and remains as a regression test for the implementer. The below-threshold test passes.

### Unit Tests

- **Command**: `python -m pytest LAB02/tests -q`
- **Status**: FAIL
- **Result**: `5 passed, 1 failed`
- **Failure**: `test_gate_rejects_malformed_model`; a pickle containing `{"accuracy": "not-a-number"}` reaches the comparison and raises an uncaught `TypeError` instead of printing `[GATE] FAIL`.
- **Coverage Percentage**: Not measured; no coverage configuration is present.

### Integration Tests

- **Valid commands**:
  - `python LAB02/pipeline.py --stage validate --data LAB02/csv/data.csv`
  - `python LAB02/pipeline.py --stage train --seed 7 --data LAB02/csv/data.csv --out LAB02/model_qa_check.pkl`
  - `python LAB02/pipeline.py --stage gate --model LAB02/model_qa_check.pkl --threshold 0.75`
- **Status**: PARTIAL PASS
- **Result**: validation, training and gate succeed; accuracy is `0.833` and gate result is `PROMOSSO`.
- **Important observation**: the first `validate` command also runs the complete pytest suite. Because the QA regression test is red, it returns failure before the direct dataset check, even when the supplied CSV is valid. This is expected from the current implementation but blocks a clean pipeline run until the malformed-model defect is fixed.

### Negative Workflow

- Temporary CSV without `label` passed to `validate`.
- **Result**: exit code `1`; `[VALIDATE] FAIL` emitted; no model created.
- Temporary CSV and models were removed after execution.

### Static and Cleanup Checks

- `get_errors` on changed Python files: no diagnostics.
- `git diff --check`: pass.
- No `*.pkl` model artifacts remain under `LAB02` after QA runs.

## Findings

### Failing finding: malformed model is not handled

**Severity:** Medium

A readable pickle with a non-numeric `accuracy` causes an unhandled `TypeError` at the gate comparison. The current exception handling covers missing/corrupt files and missing keys, but not invalid metric types or values. This violates the intended contract of a comprehensible gate failure and makes the overall pytest/validate stage fail with a traceback.

**Required fix:** validate that the loaded artifact is a mapping and that `accuracy` is numeric and finite before comparing it with the threshold; emit `[GATE] FAIL` and return exit code `1` for invalid artifacts. Add/keep the failing test as the regression test.

### Coverage gap: alternate dataset is not exercised by pytest

The data tests import and inspect the fixed `DATA_PATH`. The CLI `--data` path is checked by `validate()` after pytest, but there is no test proving that the full expected schema contract is applied to an alternate dataset. Add a parameterized or subprocess test for a valid alternate dataset and for malformed values/columns, while keeping the test fixture isolated from the repository dataset.

### Coverage gap: shell orchestrator on Windows

`run_pipeline.sh` depends on Bash and `python3`, so it was not directly executed in the PowerShell environment. The documented PowerShell sequence was executed instead. This is acceptable as the stated fallback, but the report should continue to distinguish the two execution paths.

## QA Decision

**QA FAILED.** The main workflow works for valid data, invalid data is blocked, and the threshold rejection is covered. Approval is blocked by the unhandled malformed-model case and the resulting failing regression test.

Required handoff to implementer:

1. Fix the gate validation for non-numeric/non-finite `accuracy` and malformed artifact structures.
2. Rerun `python -m pytest LAB02/tests -q` and the valid root-level workflow.
3. Add coverage for alternate `--data` files if the CLI contract is retained.
4. Return this QA report for retest after the suite is green.

Handing off to uat agent for value delivery validation
