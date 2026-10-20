# LAB04 — Serving FastAPI Docker e Model Registry

Studente: Carlo Pognant.

Modulo: ModelOps e Machine Learning — ITS ICT Piemonte, Gen AI Specialist.

Data e ora dell'esecuzione: [INSERIRE DATA E ORA DEL TEST].

Ambiente Python / dipendenze effettive: [DA COMPILARE DOPO ESECUZIONE].

## Stato della relazione

**Codice predisposto, esecuzione ancora da svolgere.** Tutte le verifiche e il cleanup sono [DA COMPILARE DOPO ESECUZIONE]. Le sezioni descrivono il metodo implementato, non un'attivita gia verificata. Dopo l'esecuzione indicare separatamente comportamento previsto, risultato osservato ed eventuale fallback.

## Scenario e obiettivo

Nessuno sa quale versione risponde in produzione. Si ricostruiscono due RandomForest su wine con rumore gaussiano: v2 con 200 alberi e v3 con 1 albero, max_depth=1. L'obiettivo e servire un artefatto identificabile e applicare un gate numerico.

## Struttura del progetto

train.py, common.py, build_registry.py, app.py, test_predict.py, tests/test_api.py, requirements.txt, Dockerfile, .dockerignore. Generati dopo esecuzione: artifacts/model_v2.pkl e model_v3.pkl, relativi JSON, registry.json e registry.md.

## Ricostruzione e differenze

La relazione scolastica riportava accuracy v2=0.8889, v3=0.5 e v2 attiva. Sono risultati storici, non misure di questa ricostruzione. Si mantengono RandomState(0), rumore con deviazione 2.0, split 0.3 stratificato e seed 42. Il nuovo bundle lega versione e schema al modello e il registry ne conserva l'hash.

## Passaggi e comandi da eseguire

Directory: root della repository. Seguire gli step LAB04 della [guida manuale](../GUIDA_ESECUZIONE_LAB04-07.md), inclusi setup e gestione terminali. Non incollare tutti i comandi insieme se e previsto un server in primo piano.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB04.train
.\.venv-labs\Scripts\python.exe -m LAB04.build_registry
.\.venv-labs\Scripts\python.exe -m uvicorn LAB04.app:app --host 127.0.0.1 --port 8000
.\.venv-labs\Scripts\python.exe -m LAB04.test_predict
.\.venv-labs\Scripts\python.exe -m pytest .\LAB04\tests -q
```

Il comando Uvicorn va nel terminale B e rimane attivo; client e pytest nel terminale A. Dopo i test Ctrl+C in B. Docker facoltativo segue il ramo D della guida.

## Metriche ed evidenze osservate

| Versione | Accuracy misurata | Soglia | Stato misurato | Artefatto |
|---|---|---|---|---|
| v2 | [DA COMPILARE DOPO ESECUZIONE] | 0.85 | [DA COMPILARE DOPO ESECUZIONE] | artifacts/model_v2.pkl |
| v3 | [DA COMPILARE DOPO ESECUZIONE] | 0.85 | [DA COMPILARE DOPO ESECUZIONE] | artifacts/model_v3.pkl |

Output effettivo: [INSERIRE OUTPUT DEL TERMINALE].

Esito dei test eseguiti manualmente: [DA COMPILARE DOPO ESECUZIONE].

## Gate e decisione

Il gate confronta l'accuracy completa con 0.85, senza arrotondare prima del confronto. V2 deve superare la soglia: altrimenti il registry non viene aggiornato e lo scenario va riesaminato. V3 e promossa se e solo se supera la soglia; in quel caso diventa attiva. Un eventuale risultato inatteso va riportato, senza alterare i valori.

Versione attiva osservata: [DA COMPILARE DOPO ESECUZIONE]. Motivazione numerica: [DA COMPILARE DOPO ESECUZIONE].

## API e identita

POST /predict riceve {"features":[13 numeri finiti nell'ordine wine]}. I nomi ordinati si leggono in artifacts/model_v2.json. Restituisce prediction e model_version. Il caricamento avviene all'avvio da un percorso esplicito del registry; hash, versione e numero/nome delle feature devono corrispondere al bundle. Dopo un nuovo training/registry occorre riavviare il server.

Campi mancanti, numeri come stringhe, booleani, lunghezza errata e valori NaN/Infinity devono produrre HTTP 422 senza prediction. Il client verifica codice e versione contro il registry locale; i test isolati non sostituiscono il client HTTP reale.

Risposta valida osservata: [INSERIRE OUTPUT DEL TERMINALE].
Richiesta errata e codice osservato: [INSERIRE OUTPUT DEL TERMINALE].

## Docker e fallback

Build dalla root: docker build -t carlo-lab04-serving:local .\\LAB04. Richiede modelli e registry realmente generati. Avvio e verifica seguono D-03/04 della guida. Se Docker Desktop non e disponibile, usare Uvicorn locale con due terminali e dichiarare il fallback. Stato Docker: [DA COMPILARE DOPO ESECUZIONE].

## Rollback discusso

Se la versione attiva degrada, confrontare una versione precedente sullo stesso batch, verificare schema/hash e soglie, aggiornare il registry solo dopo la decisione e riavviare il servizio; rivalutare poi versione e metriche. Nel LAB04 il rifiuto di v3 prima del rilascio e una mancata promozione. La simulazione di rollback dopo rilascio e nel LAB05.

## Screenshot da inserire

- [INSERIRE SCREENSHOT 04-01 training]
- [INSERIRE SCREENSHOT 04-02 registry]
- [INSERIRE SCREENSHOT 04-03 risposta valida]
- [INSERIRE SCREENSHOT 04-04 HTTP 422]
- [INSERIRE SCREENSHOT 04-05 test (facoltativo)]
- [INSERIRE SCREENSHOT 04-06a/b/c Docker solo se eseguito]
- [INSERIRE SCREENSHOT 04-07 cleanup]

Consultare [PIANO_SCREENSHOT.md](../PIANO_SCREENSHOT.md) per comandi e didascalie.

## Limiti

Rumore sintetico, dataset piccolo, singolo split e nessuna validazione di produzione. Il bundle pickle/joblib deve provenire da sorgente fidata. Hash e schema evitano scambi accidentali, non sostituiscono un registry sicuro. Docker/Windows/Linux e dipendenze vanno verificati con esecuzione reale.

## Cleanup

Fermare Uvicorn con Ctrl+C o il container con D-05, dopo le evidenze. Conservare sorgenti, metadati e registry. Modelli mantenuti fino alla verifica API/Docker; rimovibili dopo backup, rigenerabili con train e build_registry. Non e stato avviato MLflow.

Stato effettivo: [DA COMPILARE DOPO ESECUZIONE].

Risorse fermate/rimosse: [DA COMPILARE DOPO ESECUZIONE].

File conservati e motivazione: [DA COMPILARE DOPO ESECUZIONE].

## Checkpoint della traccia

- [ ] Due versioni realmente generate e registrate con metrica/stato.
- [ ] Risposta /predict identifica la versione del modello caricato.
- [ ] Input invalidi rifiutati e client HTTP completato.
- [ ] Gate v3 motivato dal numero misurato.
- [ ] Procedura di rollback discussa.
- [ ] Docker verificato oppure fallback dichiarato.
- [ ] Cleanup eseguito oppure conservazione motivata.

Spuntare soltanto dopo osservazione effettiva. Se un passaggio non e stato svolto scrivere NON VERIFICATO e il motivo.
