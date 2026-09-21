# LAB01 - Run log, gate e nota finale

## Comando eseguito

Le run sono state eseguite dalla cartella `LAB01`:

```powershell
python train.py --seed 42 --out model_a.pkl
python train.py --seed 7 --out model_b.pkl
```

Il training legge il dataset tramite `DATA_PATH` definito in `data_loader.py` e salva nel pickle:

- `pesi`
- `bias`
- `riferimenti`
- `seed`

## Run log

| id | dataset | parametri | metrica | path modello |
|---|---|---|---:|---|
| run-a | `csv/data.csv` | `seed=42` | `accuracy=0.667` | `model_a.pkl` |
| run-b | `csv/data.csv` | `seed=7` | `accuracy=0.833` | `model_b.pkl` |

Ogni run usa 48 righe per il training e 12 righe per il test.

## Gate

**Promuovi la nuova run se `accuracy_nuova >= accuracy_precedente` e il relativo file `.pkl` esiste.**

Applicazione:

- accuracy precedente: `0.667`
- accuracy nuova: `0.833`
- confronto: `0.833 >= 0.667` -> vero
- `model_b.pkl` esiste -> vero

run-a è la baseline: non ha una run precedente con cui confrontarsi, quindi viene registrata come riferimento.

**Esito: run-b passa il gate e viene promossa**, perché migliora l'accuracy rispetto a run-a e il suo artefatto è presente.

Le due run usano gli stessi dati e lo stesso codice: cambia solo il seed, che determina lo split train/test. La differenza di accuracy dipende quindi dal seed, non da un cambio di dataset o di codice.

## Nota finale

Il test set contiene solo 12 righe: l'accuracy cambia quindi a scatti di circa 8,3 punti percentuali per ogni esempio classificato diversamente. Il risultato non è sufficiente per concludere che il modello generalizzi bene.

Inoltre, con seed diversi le due run vengono valutate su test set diversi, quindi i due numeri non sono davvero confrontabili: il gate promuove run-b, ma parte del miglioramento potrebbe dipendere da uno split più facile.

Mancano infine:

- una versione o un hash del dataset;
- la versione dell'ambiente Python e delle dipendenze;
- una valutazione su più split o cross-validation;
- metriche aggiuntive come precision, recall e confusion matrix.

## Cleanup

Dopo aver registrato i risultati e applicato il gate, i file `model_a.pkl` e `model_b.pkl` sono stati cancellati. Il report conserva comunque metriche, parametri, percorsi e decisione del gate.

- `data.csv` e la cartella `csv/` sono mantenuti perché sono il dataset del lab;
- nessun processo Python o kernel è stato lasciato attivo;
- nessun log intermedio da rimuovere.

## Fallback

Dataset sintetico di 60 righe usato al posto di un dataset reale; nessun altro fallback.
