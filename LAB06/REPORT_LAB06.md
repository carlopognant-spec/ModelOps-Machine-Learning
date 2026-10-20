# LAB06 — Monitoring, Logging, Drift e Notifiche

Studente: Carlo Pognant.

Modulo: ModelOps e Machine Learning — ITS ICT Piemonte, Gen AI Specialist.

Data e ora dell'esecuzione: [INSERIRE DATA E ORA DEL TEST].

Ambiente Python / dipendenze effettive: [DA COMPILARE DOPO ESECUZIONE].

## Stato della relazione

**Codice predisposto, esecuzione ancora da svolgere.** Tutte le verifiche e il cleanup sono [DA COMPILARE DOPO ESECUZIONE]. Le sezioni descrivono il metodo implementato, non un'attivita gia verificata. Dopo l'esecuzione indicare separatamente comportamento previsto, risultato osservato ed eventuale fallback.

## Scenario e obiettivo

Un classificatore clienti di credito sintetico viene monitorato su batch ordinati. Alcuni batch recenti hanno eta spostata e una policy sintetica piu restrittiva per le etichette. Si registrano PSI e accuracy senza fingere un servizio di monitoring reale.

## Struttura del progetto

simulate.py genera dati/modello/predizioni e manifest; drift.py implementa PSI e stato persistente; monitor.py calibra e monitora; tests/test_monitoring.py e requirements.txt. Generati: data/ con modello e NPZ condivisi con LAB07; output/monitoring.json, alerts.jsonl, dashboard.md e monitoring.png.

## Ricostruzione e differenze

Laboratorio nuovo. La soglia 0.08 dell'esempio non viene imposta. Tutti i valori della nuova simulazione restano da ottenere manualmente.

## Passaggi e comandi da eseguire

Directory: root della repository. Seguire gli step LAB06 della [guida manuale](../GUIDA_ESECUZIONE_LAB04-07.md), inclusi setup e gestione terminali. Non incollare tutti i comandi insieme se e previsto un server in primo piano.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB06.simulate
.\.venv-labs\Scripts\python.exe -m LAB06.monitor
.\.venv-labs\Scripts\python.exe -m pytest .\LAB06\tests -q
```

## Metriche ed evidenze osservate

| Batch | PSI eta | Soglia storica | Stato | Accuracy | Soglia accuracy |
|---|---|---|---|---|---|
| recent-00 | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |
| recent-01 | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |
| recent-02 | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |
| recent-03 | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |
| recent-04 | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |

Output effettivo: [INSERIRE OUTPUT DEL TERMINALE].

Esito dei test eseguiti manualmente: [DA COMPILARE DOPO ESECUZIONE].

## Indicatore e soglia motivata

PSI = somma (q-p) ln(q/p). I bin sono fissati dai quantili del riferimento, estremi infiniti e quantili duplicati rimossi. Lo smoothing aggiunge 0.5 ai conteggi e rinormalizza entrambe le distribuzioni; bin vuoti non causano divisioni per zero. I vettori vuoti o non finiti vengono rifiutati.

I 30 batch storici normali e indipendenti dal training calibrano le soglie: per ogni feature, q99 del PSI storico moltiplicato per 1.25, con floor numerico 1e-6. Questo margine didattico evita di usare i recenti per scegliere la soglia. Non e una soglia universale o una garanzia di copertura. Accuracy minima = q05 delle accuracy storiche meno 0.02, con minimo 0. Nessuna calibrazione osserva i batch problematici.

Soglia PSI eta ottenuta e distribuzione storica: [DA COMPILARE DOPO ESECUZIONE].
Soglia accuracy ottenuta: [DA COMPILARE DOPO ESECUZIONE].

## Regola di notifica e log

Sotto o uguale alla soglia: SOTTO SOGLIA e contatore azzerato. Primo superamento: ATTENZIONE, senza alert definitivo. Dal secondo superamento consecutivo: ALERT. Il contatore segue l'eta; i PSI delle altre feature sono informativi. Il controllo di accuracy e separato, per collegare LAB07 a un degrado misurato su etichette sintetiche.

Ogni riga di alerts.jsonl registra timestamp UTC, batch, feature, score, soglia, stato/consecutivi, causa, canale, responsabile, azione proposta, accuracy e versione modello. Il campo notification_sent e sempre false: nessun invio esterno avviene. Il terminale e il JSONL rappresentano la notifica simulata.

Canale ipotetico: Slack #modelops-alerts. Responsabile: Data Scientist on-call / responsabile dati. Azione proposta: controllare eta, policy ed etichette, analizzare sottogruppi e confrontare un modello precedente prima di rollback/retraining. Non e un'azione realmente eseguita.

Estratto log con prima attenzione, alert e ritorno normale: [INSERIRE OUTPUT DEL TERMINALE].

## Dashboard e integrazione LAB07

La tabella Markdown e il grafico Matplotlib mostrano la serie PSI/accuracy e le soglie. L'asse temporale usa ordine dei batch, non giorni realmente trascorsi. I timestamp sono quelli dell'esecuzione. LAB07 legge lo stesso manifest, modello, training, reference, batch e predizioni; gli hash impediscono di mescolare run.

## Fallback

Dashboard locale, nessun MLflow/Prometheus/Grafana. Se un alert non supera realmente la soglia, riportare l'assenza e non completare il checkpoint relativo. Non simulare screenshot di servizi non usati.

## Screenshot da inserire

- [INSERIRE SCREENSHOT 06-01 dati storici]
- [INSERIRE SCREENSHOT 06-02 calibrazione]
- [INSERIRE SCREENSHOT 06-03 serie e sotto soglia]
- [INSERIRE SCREENSHOT 06-04 alert con canale/owner]
- [INSERIRE SCREENSHOT 06-05 grafico]
- [INSERIRE SCREENSHOT 06-06 cleanup e conservazione dati]

Consultare [PIANO_SCREENSHOT.md](../PIANO_SCREENSHOT.md) per comandi e didascalie.

## Limiti

Dati sintetici con soli quattro input; nessun credito reale. Cambiano eta e policy contemporaneamente: PSI non dimostra la causa del degrado. Nessuna misura di latenza p95, uptime, settimana mobile o invio Slack. Le soglie empiriche su 30 batch necessiterebbero validazione indipendente. Il monitor e batch, non un demone continuo.

## Cleanup

Processi di simulazione/monitoring terminano da soli. Conservare tutta data/ e output/ per LAB07 e le evidenze; chiudere il visualizzatore del grafico. Non sono stati avviati exporter, Grafana o MLflow da questi script. Conservazione motivata dei dati, non eliminazione dichiarata a priori.

Stato effettivo: [DA COMPILARE DOPO ESECUZIONE].

Risorse fermate/rimosse: [DA COMPILARE DOPO ESECUZIONE].

File conservati e motivazione: [DA COMPILARE DOPO ESECUZIONE].

## Checkpoint della traccia

- [ ] PSI numerico su reference e batch distinti.
- [ ] Soglia motivata dallo storico senza usare i recenti.
- [ ] Serie temporale stampata e grafico salvato.
- [ ] Sotto soglia distinto da attenzione e alert persistente.
- [ ] Canale ipotetico e responsabile documentati.
- [ ] Log con causa e azione proposta.
- [ ] Dati/versione coerenti disponibili per LAB07.
- [ ] Test manualmente eseguiti e risultato annotato.
- [ ] Fallback e cleanup documentati.

Spuntare soltanto dopo osservazione effettiva. Se un passaggio non e stato svolto scrivere NON VERIFICATO e il motivo.
