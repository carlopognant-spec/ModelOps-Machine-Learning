# LAB09 - Permessi, audit e fine-tuning pipeline

Studente: [INSERIRE NOME].

Data esecuzione: [INSERIRE DATA].

## Stato

Template creato. Compilare dopo esecuzione reale.

## Comandi principali

```powershell
.\.venv-labs\Scripts\python.exe -m pip install -r .\LAB09\requirements.txt
.\.venv-labs\Scripts\python.exe -m LAB09.finetune_job
```

## Sezione screenshot (comando + evidenza)

| ID | Comando da lanciare | Cosa deve vedersi | Screenshot |
|---|---|---|---|
| 09-01 | `.\.venv-labs\Scripts\python.exe -m LAB09.finetune_job` | Tentativo negato: `bob` su train | [INSERIRE SCREENSHOT 09-01] |
| 09-02 | `.\.venv-labs\Scripts\python.exe -m LAB09.finetune_job` | Tentativo negato: `alice` su approve | [INSERIRE SCREENSHOT 09-02] |
| 09-03 | `.\.venv-labs\Scripts\python.exe -m LAB09.finetune_job` | Training completato con run_id e accuracy | [INSERIRE SCREENSHOT 09-03] |
| 09-04 | `Get-Content .\LAB09\output\audit.jsonl` | Log audit con eventi allowed/denied | [INSERIRE SCREENSHOT 09-04] |

## Note da completare

- Matrice ruoli/azioni: [DA COMPILARE]
- Distinzione tra simulazione locale e IAM reale: [DA COMPILARE]
- Cleanup: [DA COMPILARE]
