# LAB10 - Fine-tuning, distillazione e ottimizzazione

Studente: [INSERIRE NOME].

Data esecuzione: [INSERIRE DATA].

## Stato

Template creato. Compilare dopo esecuzione reale.

## Comandi principali

```powershell
.\.venv-labs\Scripts\python.exe -m pip install -r .\LAB10\requirements.txt
.\.venv-labs\Scripts\python.exe -m LAB10.finetuning_distillation
```

## Sezione screenshot (comando + evidenza)

| ID | Comando da lanciare | Cosa deve vedersi | Screenshot |
|---|---|---|---|
| 10-01 | `.\.venv-labs\Scripts\python.exe -m LAB10.finetuning_distillation` | Conteggio split source/target_train/test | [INSERIRE SCREENSHOT 10-01] |
| 10-02 | `.\.venv-labs\Scripts\python.exe -m LAB10.finetuning_distillation` | Tabella metriche baseline/teacher/student | [INSERIRE SCREENSHOT 10-02] |
| 10-03 | `.\.venv-labs\Scripts\python.exe -m LAB10.finetuning_distillation` | `student_fidelity` e differenza accuracy | [INSERIRE SCREENSHOT 10-03] |
| 10-04 | `Get-Content .\LAB10\output\report.json` | Report JSON completo con misure | [INSERIRE SCREENSHOT 10-04] |

## Note da completare

- Decisione finale baseline vs teacher vs student: [DA COMPILARE]
- Vincoli usati (byte, latenza, accuracy): [DA COMPILARE]
- Cleanup: [DA COMPILARE]
