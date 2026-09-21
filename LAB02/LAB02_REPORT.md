# LAB02 - CI/CD, automazione e pipeline

## Pipeline implementata

La pipeline è composta da questi stadi, eseguiti in ordine:

1. `pytest tests -q`: controlla lo schema del dataset e i valori della target.
2. `python pipeline.py --stage validate`: esegue i test e verifica che i dati siano caricabili.
3. `python pipeline.py --stage train`: allena il modello e salva `model.pkl`.
4. `python pipeline.py --stage gate`: confronta l'accuracy con la soglia numerica.

`run_pipeline.sh` usa `set -euo pipefail`: se uno stadio fallisce, gli stadi successivi non partono. Gli output e gli esiti vengono salvati in `run.log`.

## Comando e risultato

```bash
pytest tests/ -q
python pipeline.py --stage validate
python pipeline.py --stage train --seed 7 --out model.pkl
python pipeline.py --stage gate --model model.pkl --threshold 0.75
```

Risultato della run valida:

```text
[TEST] 2 passed
[VALIDATE] PASS: schema dati verificato
[TRAIN] accuracy=0.833 model=model.pkl
[GATE] accuracy=0.833 soglia=0.75 -> PROMOSSO
```

Il gate promuove il modello perché `0.833 >= 0.75`.

## Fallimento intenzionale

È stato creato temporaneamente un CSV senza la colonna `label` e validato con:

```bash
python pipeline.py --stage validate --data tests/data_missing_label.csv
```

La pipeline ha bloccato l'esecuzione con exit code `1` e messaggio:

```text
[VALIDATE] FAIL: Colonne non presenti nel CSV: ['label']
```

Il training non è stato eseguito sul dataset invalido. Il fixture temporaneo è stato cancellato dopo la prova.

## Limiti e fallback

- Il dataset contiene solo 60 righe e il test set contiene 12 righe.
- Run con seed diversi possono usare test set diversi, quindi l'accuracy non è una misura completamente confrontabile.
- Il gate usa una soglia didattica fissa di `0.75`, non una baseline di produzione.
- Non è configurato un servizio CI remoto come GitHub Actions.
- Fallback usato: esecuzione locale tramite terminale e script Bash; il dataset è sintetico.

## Cleanup

- `model.pkl` generato durante le prove è stato rimosso.
- Il CSV originale `csv/data.csv` è stato mantenuto.
- Il CSV temporaneo senza `label` è stato rimosso.
- `run.log` è mantenuto perché fa parte delle evidenze finali.
- Non risultano processi Python o kernel lasciati attivi.
- Le cache locali Python e pytest generate durante i test sono state rimosse.
