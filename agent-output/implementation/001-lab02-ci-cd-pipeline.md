---
ID: 1
Origin: 1
UUID: c10f1ccd
Status: Active
---

# Implementazione LAB02 CI/CD e pipeline ML

## Plan Reference

- Piano: `agent-output/planning/001-lab02-ci-cd-pipeline.md`
- Epic: Lab 02 - CI/CD, automazione workflow e pipeline
- Target release: non applicabile/TBD; il repository non contiene roadmap o versionamento applicativo.

## Date

2026-09-23

## Changelog

| Date | Handoff | Request | Summary |
|---|---|---|---|
| 2026-09-23 | Implementer -> QA | Seguire il piano | Aggiunti test di prerequisito, import path riproducibile dalla root, validazione prima del training, errori del gate e aggiornamento delle evidenze. |
| 2026-09-23 | QA -> Implementer | Correggere bug del gate | Validati tipo e finitezza di `accuracy`; aggiunti test per valori non numerici e non finiti. |

## Implementation Summary

Il progetto ora esegue i test di `LAB02` anche dalla root del repository e impedisce al training di creare un modello se il dataset non supera la validazione. Il gate segnala con un messaggio controllato anche un artefatto mancante o invalido. Questo rende verificabile la sequenza CI/CD locale richiesta dal laboratorio senza introdurre un servizio CI remoto fuori dallo scope.

## Milestones Completed

- [x] Reso riproducibile l'import dei test dalla root tramite `tests/conftest.py`.
- [x] Aggiunto il prerequisito di validazione dati prima del training.
- [x] Evitata la ricorsione tra `train` e la suite pytest separando il controllo schema dall'esecuzione dei test.
- [x] Aggiunta gestione comprensibile del gate con modello mancante/invalido.
- [x] Aggiornati report, log ed evidenze di cleanup.
- [x] Verificata la sequenza completa dalla root.
- [x] Corretto il `TypeError` del gate su metriche non numeriche o non finite.

## Files Modified

| Path | Changes |
|---|---|
| `LAB02/pipeline.py` | `validate` supporta il controllo schema senza rieseguire pytest; `train` valida prima di creare il modello; `gate` gestisce artefatti mancanti, corrotti, non numerici o non finiti con `[GATE] FAIL`. |
| `LAB02/LAB02_REPORT.md` | Comandi PowerShell dalla root, dipendenza validate-train, quattro test e decisione sulla release documentati. |
| `LAB02/run.log` | Evidenze finali aggiornate con esiti ordinati degli stadi. |
| `agent-output/planning/001-lab02-ci-cd-pipeline.md` | Stato portato a In Progress e changelog di handoff aggiunto. |

## Files Created

| Path | Purpose |
|---|---|
| `LAB02/tests/conftest.py` | Rende importabile il modulo locale `data_loader` quando pytest viene eseguito dalla root. |
| `LAB02/tests/test_pipeline.py` | Verifica il blocco del training su dataset invalido, gate senza modello, sotto soglia e metriche non numeriche/non finite. |

## Code Quality Validation

- [x] `git diff --check` senza errori.
- [x] Test eseguiti dalla root del repository.
- [x] Artefatti temporanei rimossi dopo le prove.
- [x] Nessuna dipendenza o servizio esterno aggiunto.
- [x] Compatibilità con l'orchestratore Bash esistente mantenuta.

## Value Statement Validation

**Originale:** Come studente, voglio una pipeline ML eseguibile in modo riproducibile e con dipendenze tra gli stadi verificabili, così da dimostrare che dati non validi o metriche insufficienti impediscono la consegna dell'artefatto.

**Risultato:** i test sono eseguibili dalla root, `train` valida il dataset prima della scrittura, il gate applica una soglia numerica e fallisce in modo comprensibile quando l'artefatto non è disponibile. La run valida produce accuracy `0.833` e promozione con soglia `0.75`; la run negativa termina con exit code `1` senza creare il modello.

## TDD Compliance

| Function/Class | Test File | Test Written First? | Failure Verified? | Failure Reason | Pass After Impl? |
|---|---|---|---|---|---|
| `train()` validation prerequisite | `LAB02/tests/test_pipeline.py` | Yes | Yes | AssertionError: missing `[VALIDATE] FAIL` and traceback from invalid CSV | Yes |
| `gate()` missing artifact handling | `LAB02/tests/test_pipeline.py` | Yes | Yes | AssertionError: missing `[GATE] FAIL` and uncaught `FileNotFoundError` | Yes |

## Test Coverage

### Unit/behavior coverage

- Dataset columns, target non-null, type conversion and label domain.
- Training blocked before artifact creation on invalid CSV.
- Gate rejects a missing model with a non-zero exit code and clear output.

### Integration coverage

- Root-level sequence: pytest, validate, train and gate.
- Valid run: accuracy `0.833`, gate promoted at `0.75`.
- Invalid run: validation failure, exit code `1`, no model created.

## Test Execution Results

| Command | Result |
|---|---|
| `python -m pytest LAB02/tests -q` | PASS, `9 passed` |
| `python LAB02/pipeline.py --stage validate --data LAB02/csv/data.csv` | PASS |
| `python LAB02/pipeline.py --stage train --seed 7 --data LAB02/csv/data.csv --out LAB02/model_final_check.pkl` | PASS, accuracy `0.833` |
| `python LAB02/pipeline.py --stage gate --model LAB02/model_final_check.pkl --threshold 0.75` | PASS, `PROMOSSO` |
| Invalid CSV through `train` | PASS negative check, exit code `1`, no model |
| Missing model through `gate` | PASS negative check, exit code `1` |
| Malformed/non-finite model through `gate` | PASS negative checks, exit code `1` |
| `git diff --check` | PASS |

## Outstanding Items

- Target release remains TBD/N/A because no roadmap or release artifact exists in the repository; no version file was invented.
- No remote CI provider was configured, consistent with the local fallback and the lab timebox.
- `run_pipeline.sh` expects `python3` in a Bash environment; on Windows the documented PowerShell commands are the supported equivalent.
- QA retest passed after the gate metric validation fix.

## Next Steps

QA validates the changed behavior and report evidence. After QA approval, UAT can verify that the deliverable satisfies the professor's checklist and cleanup requirements.
