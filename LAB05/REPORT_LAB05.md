# LAB05 — Versioning Rollback e Prime Metriche

Studente: Carlo Pognant.

Modulo: ModelOps e Machine Learning — ITS ICT Piemonte, Gen AI Specialist.

Data e ora dell'esecuzione: [INSERIRE DATA E ORA DEL TEST].

Ambiente Python / dipendenze effettive: [DA COMPILARE DOPO ESECUZIONE].

## Stato della relazione

**Codice predisposto, esecuzione ancora da svolgere.** Tutte le verifiche e il cleanup sono [DA COMPILARE DOPO ESECUZIONE]. Le sezioni descrivono il metodo implementato, non un'attivita gia verificata. Dopo l'esecuzione indicare separatamente comportamento previsto, risultato osservato ed eventuale fallback.

## Scenario e obiettivo

La traccia descrive un rilascio con feature mismatch e possibili errori 5xx. La dimostrazione locale usa invece un modello LogisticRegression stabile e un DecisionTree max_depth=1 per rappresentare un degrado di qualita. Non viene introdotto un vero feature mismatch e non vengono misurati errori HTTP.

## Struttura del progetto

evaluate.py, rollback_versions.py, rollback_log.py, tests/test_rollback.py, requirements.txt. Generati: artifacts/model-1.0.0.pkl, model-2.0.0.pkl, evaluation_batch.npz, metrics.json, registry_before.json, registry.json, post_verification.json e rollback_events.jsonl.

## Ricostruzione e differenze

Risultati scolastici storici: v1=0.9474, v2=0.9123, calo=0.0351, versione finale=1.0.0. Nessuno di questi valori e stato rimisurato durante la preparazione. Il dataset resta sklearn breast_cancer, esplicitamente medico. Split 0.3 stratificato seed 42, LogisticRegression(max_iter=5000) non scalata e DecisionTree(max_depth=1).

## Passaggi e comandi da eseguire

Directory: root della repository. Seguire gli step LAB05 della [guida manuale](../GUIDA_ESECUZIONE_LAB04-07.md), inclusi setup e gestione terminali. Non incollare tutti i comandi insieme se e previsto un server in primo piano.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB05.evaluate
.\.venv-labs\Scripts\python.exe -m LAB05.rollback_versions
.\.venv-labs\Scripts\python.exe -m LAB05.rollback_log
.\.venv-labs\Scripts\python.exe -m pytest .\LAB05\tests -q
```

## Metriche ed evidenze osservate

| Versione | Accuracy sullo stesso batch | Latenza media locale (ms/predizione singola) | Chiamate |
|---|---|---|---|
| 1.0.0 | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |
| 2.0.0 | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |

Output effettivo: [INSERIRE OUTPUT DEL TERMINALE].

Esito dei test eseguiti manualmente: [DA COMPILARE DOPO ESECUZIONE].

## Metodo di misura e gate

Stesse righe train/test per entrambe le versioni. Accuracy calcolata sull'intero test; latenza con perf_counter_ns, warmup e cinque passaggi sullo stesso batch, una predict per osservazione. Unita: millisecondi per chiamata; esclusi training, rete e caricamento. Il confronto sequenziale risente del carico macchina e non misura un SLA.

MAX_ACCEPTABLE_DROP = 0.02 e definita nel sorgente prima della valutazione. Calo = accuracy_v1 - accuracy_v2; rollback se maggiore di 0.02, con sola tolleranza 1e-12 al confine floating point. I numeri non vengono arrotondati per la decisione.

Calo osservato: [DA COMPILARE DOPO ESECUZIONE]. Soglia: 0.02, cioe 2 punti percentuali. Decisione: [DA COMPILARE DOPO ESECUZIONE].

## Rilascio e ripristino simulati

rollback_versions legge metriche e artefatti con hash, ricontrolla accuracy/batch, poi scrive registry_before e registry con 2.0.0 attiva. Se il gate rileva degrado, modifica il registry a 1.0.0; altrimenti mantiene 2.0.0 e non dichiara rollback. Rilegge il registry, ricarica il modello finale e misura nuovamente accuracy e latenza. Un evento persistente conserva versione iniziale/finale e verifica. Non cambia un servizio di produzione reale.

La motivazione didattica preferisce la baseline nota quando il degrado supera la soglia; il fix non e validato nel timebox. Non esiste una misura reale del tempo necessario a correggerlo. Il riferimento tecnico chiamava rollback anche il semplice blocco di promozione: questa ricostruzione distingue i due eventi.

| Verifica | Osservazione |
|---|---|
| Versione prima | [DA COMPILARE DOPO ESECUZIONE] |
| Versione dopo | [DA COMPILARE DOPO ESECUZIONE] |
| Accuracy post-decisione | [DA COMPILARE DOPO ESECUZIONE] |
| Esito verifica post-decisione | [DA COMPILARE DOPO ESECUZIONE] |
| Run ID / timestamp evento | [DA COMPILARE DOPO ESECUZIONE] |
| Errori HTTP 5xx | NON MISURATI in questa dimostrazione |

## Log e fallback

rollback_log visualizza gli eventi JSONL scritti dall'azione, con timestamp UTC autentico; non ricrea il timestamp al momento della lettura. Conservare l'evento del run_id corretto. Registry JSON locale al posto di MLflow; nessun tag, branch temporaneo o server avviato.

## Screenshot da inserire

- [INSERIRE SCREENSHOT 05-01 metriche]
- [INSERIRE SCREENSHOT 05-02 soglia/decisione]
- [INSERIRE SCREENSHOT 05-03 registry prima/dopo]
- [INSERIRE SCREENSHOT 05-04 post-verifica]
- [INSERIRE SCREENSHOT 05-05 log]
- [INSERIRE SCREENSHOT 05-06 cleanup]

Consultare [PIANO_SCREENSHOT.md](../PIANO_SCREENSHOT.md) per comandi e didascalie.

## Limiti

Dataset medico usato soltanto per la dimostrazione del gate, non presentato come credito. Singolo split, eventuali warning di convergenza da riportare; latenza influenzata dal carico locale. Non misura errori 5xx o disponibilita del servizio. Non prova la gestione di un vero incidente di produzione.

## Cleanup

Gli script terminano da soli. Conservare registry prima/dopo, metriche, log e post-verifica; modelli e batch necessari fino alla verifica e al backup. Dopo backup i soli modelli possono essere rimossi con F-03; per ripetere la verifica rigenerarli con evaluate e rieseguire rollback_versions. Nessun MLflow, tag o branch da rimuovere.

Stato effettivo: [DA COMPILARE DOPO ESECUZIONE].

Risorse fermate/rimosse: [DA COMPILARE DOPO ESECUZIONE].

File conservati e motivazione: [DA COMPILARE DOPO ESECUZIONE].

## Checkpoint della traccia

- [ ] Metriche realmente misurate sullo stesso batch.
- [ ] Latenza con unita e metodo documentati.
- [ ] Gate predefinito confronta numeri effettivi.
- [ ] Registry mostra v2 inizialmente rilasciata.
- [ ] Cambio a v1 e rivalutazione verificati, oppure nessun rollback motivato.
- [ ] Log conserva versioni, timestamp, causa e verifica.
- [ ] Limiti feature mismatch/5xx dichiarati.
- [ ] Cleanup documentato.

Spuntare soltanto dopo osservazione effettiva. Se un passaggio non e stato svolto scrivere NON VERIFICATO e il motivo.
