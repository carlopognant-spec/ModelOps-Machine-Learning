# LAB12 - MLflow e Kubeflow Pipelines

Studente: [INSERIRE NOME].

Data esecuzione: [INSERIRE DATA].

## Stato

Template creato. Compilare dopo esecuzione reale.

## Comandi principali

```powershell
.\.venv-labs\Scripts\python.exe -m pip install -r .\LAB12\requirements.txt
.\.venv-labs\Scripts\python.exe -m LAB12.mlflow_tracking train
.\.venv-labs\Scripts\python.exe -m LAB12.mlflow_tracking compare
.\.venv-labs\Scripts\python.exe -m LAB12.mlflow_tracking restore
.\.venv-labs\Scripts\python.exe -m LAB12.kfp_pipeline --out .\LAB12\output\kfp_output
```

## Sezione screenshot (comando + evidenza)

| ID | Comando da lanciare | Cosa deve vedersi | Screenshot |
|---|---|---|---|
| 12-01 | `.\.venv-labs\Scripts\python.exe -m LAB12.mlflow_tracking train` | Quattro run create e `session.json` con run_id | [INSERIRE SCREENSHOT 12-01] |
| 12-02 | `.\.venv-labs\Scripts\python.exe -m LAB12.mlflow_tracking compare` | Ordinamento run e `selected_run.json` | [INSERIRE SCREENSHOT 12-02] |
| 12-03 | `.\.venv-labs\Scripts\python.exe -m LAB12.mlflow_tracking restore` | Restore da artifact store e report metriche | [INSERIRE SCREENSHOT 12-03] |
| 12-04 | `.\.venv-labs\Scripts\python.exe -m LAB12.kfp_pipeline --out .\LAB12\output\kfp_output` | Pipeline locale completata e `kfp_result.json` | [INSERIRE SCREENSHOT 12-04] |
| 12-05 | `Get-Content .\LAB12\output\kfp_output\wine_pipeline.yaml` | YAML compilato dei componenti | [INSERIRE SCREENSHOT 12-05] |

## Note da completare

- Confronto MLflow vs KFP vs servizi cloud gestiti: [DA COMPILARE]
- Limiti osservati in locale: [DA COMPILARE]
- Cleanup: [DA COMPILARE]
