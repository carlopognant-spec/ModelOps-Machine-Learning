# Piano screenshot — evidenze autentiche

Studente: Carlo Pognant. Tutte le caselle sono ancora da verificare.

Usare Win+Shift+S, salvare PNG in evidenze/LABnn e riportare l'ID nel nome (esempio 06-04-alert.png). Tutti i comandi partono dalla root e usano l'ambiente della guida. Per API tenere Uvicorn attivo nel terminale B; client nel terminale A. Per Docker acquisire evidenze solo se build, avvio e test sono stati realmente eseguiti. In caso di fallback riportare il motivo e non compilare didascalie che dichiarano successo.

Mostrare comando e risposta, quando possibile. Non e necessario rieseguire un training o un rollback soltanto per fotografarlo: scorrere l'output autentico o consultare i file persistiti. Se si ripete un comando, registrare il nuovo run e non mescolare evidenze. I comandi qui raggruppati con punto e virgola sono righe di consultazione; per l'esecuzione ordinata usare i singoli step della guida. Non inserire metriche o una didascalia di successo se l'output non le conferma.

## 04-01 — Training e metriche

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB04. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB04.train
```

- Mostrare: Accuracy v2/v3 e percorsi dei modelli.
- Posizione nel report: LAB04: Metriche.
- Didascalia da usare solo se confermata: «Training delle due versioni sullo stesso split wine; valori ottenuti nella mia esecuzione.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 04-02 — Registry e gate

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB04. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB04.build_registry; Get-Content .\LAB04\registry.md
```

- Mostrare: Soglia, stato, motivazione e versione attiva.
- Posizione nel report: LAB04: Gate e decisione.
- Didascalia da usare solo se confermata: «Registry locale aggiornato dal confronto tra accuracy misurata e soglia 0.85.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 04-03 — Risposta API valida

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB04. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB04.test_predict
```

- Mostrare: Riga valida HTTP 200, prediction e model_version; includere comando.
- Posizione nel report: LAB04: API.
- Didascalia da usare solo se confermata: «La risposta valida identifica la versione effettivamente servita dal modello.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 04-04 — Richieste rifiutate

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB04. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB04.test_predict
```

- Mostrare: HTTP 422 per campo mancante, tipo, lunghezza e non finiti; nessuna prediction.
- Posizione nel report: LAB04: API.
- Didascalia da usare solo se confermata: «Le richieste invalide sono rifiutate con HTTP 422 nella verifica eseguita.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 04-05 — Test isolati (facoltativo)

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB04. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m pytest .\LAB04\tests -q
```

- Mostrare: Esito effettivo, nessun risultato presupposto.
- Posizione nel report: LAB04: Verifica.
- Didascalia da usare solo se confermata: «Esito dei test isolati di API, gate e identita artefatto.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 04-06a — Build Docker (solo se eseguita)

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB04. Directory: root.
- Comando:

```powershell
docker build -t carlo-lab04-serving:local .\LAB04
```

- Mostrare: Comando e conclusione reale della build.
- Posizione nel report: LAB04: Docker.
- Didascalia da usare solo se confermata: «Build effettuata con gli artefatti generati localmente; endpoint da verificare separatamente.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 04-06b — Avvio Docker (solo se eseguito)

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB04. Directory: root.
- Comando:

```powershell
docker logs carlo-lab04-serving
```

- Mostrare: Startup complete e versione caricata.
- Posizione nel report: LAB04: Docker.
- Didascalia da usare solo se confermata: «Avvio del container del laboratorio con caricamento del modello.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 04-06c — Endpoint Docker (solo se eseguito)

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB04. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB04.test_predict
```

- Mostrare: Client eseguito dopo avvio container e stop Uvicorn locale.
- Posizione nel report: LAB04: Docker.
- Didascalia da usare solo se confermata: «Risposte HTTP e versione verificate contro il container effettivamente avviato.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 04-07 — Cleanup LAB04

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB04. Directory: root.
- Comando:

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
```

- Mostrare: Ctrl+C nel terminale B e shutdown; se Docker eseguito aggiungere output D-05.
- Posizione nel report: LAB04: Cleanup.
- Didascalia da usare solo se confermata: «Stato delle risorse dopo le verifiche; artefatti conservati o rimossi come indicato nella relazione.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 05-01 — Confronto metriche

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB05. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB05.evaluate
```

- Mostrare: Accuracy, latenza media in ms e chiamate per entrambe le versioni.
- Posizione nel report: LAB05: Metriche.
- Didascalia da usare solo se confermata: «Le versioni sono valutate sulle stesse osservazioni; latenza locale misurata con lo stesso metodo.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 05-02 — Soglia e decisione

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB05. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB05.rollback_versions
```

- Mostrare: v1, v2, calo, soglia 0.02 e motivo.
- Posizione nel report: LAB05: Gate.
- Didascalia da usare solo se confermata: «La decisione deriva dal calo effettivo rispetto alla soglia fissata prima della valutazione.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 05-03 — Registry prima e dopo

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB05. Directory: root.
- Comando:

```powershell
Get-Content .\LAB05\registry_before.json; Get-Content .\LAB05\registry.json
```

- Mostrare: 2.0.0 iniziale e versione finale; usare due immagini se necessario.
- Posizione nel report: LAB05: Rilascio e ripristino.
- Didascalia da usare solo se confermata: «Confronto tra registry iniziale del rilascio simulato e registry dopo la decisione.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 05-04 — Verifica post-decisione

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB05. Directory: root.
- Comando:

```powershell
Get-Content .\LAB05\post_verification.json
```

- Mostrare: Versione finale, accuracy rivalutata, passed e timestamp.
- Posizione nel report: LAB05: Verifica.
- Didascalia da usare solo se confermata: «Il modello indicato dal registry finale e ricaricato e rivalutato sullo stesso batch.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 05-05 — Log autentico

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB05. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB05.rollback_log
```

- Mostrare: Run ID, timestamp, versioni, soglia, degrado e verifica.
- Posizione nel report: LAB05: Log.
- Didascalia da usare solo se confermata: «Evento persistito durante l'azione locale; il timestamp non e inventato al momento della lettura.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 05-06 — Cleanup LAB05

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB05. Directory: root.
- Comando:

```powershell
Get-ChildItem .\LAB05\artifacts
```

- Mostrare: File mantenuti; se rimozione opzionale eseguita includere comando F-03 e inventario successivo.
- Posizione nel report: LAB05: Cleanup.
- Didascalia da usare solo se confermata: «Inventario finale degli artefatti e conservazione motivata delle evidenze per la verifica.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 06-01 — Batch storici

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB06. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB06.simulate
```

- Mostrare: ID, ruoli e numerosita di reference/history/recent; modello sintetico.
- Posizione nel report: LAB06: Scenario.
- Didascalia da usare solo se confermata: «Simulazione riproducibile di clienti di credito con batch distinti e predizioni persistite.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 06-02 — Calibrazione soglie

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB06. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB06.monitor
```

- Mostrare: CALIBRAZIONE STORICA con metodo, PSI storici e soglie; cattura piu immagini se serve.
- Posizione nel report: LAB06: Indicatore e soglia.
- Didascalia da usare solo se confermata: «Le soglie sono ricavate esclusivamente dai batch storici simulati prima della valutazione dei recenti.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 06-03 — Serie temporale e sotto soglia

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB06. Directory: root.
- Comando:

```powershell
Get-Content .\LAB06\output\dashboard.md
```

- Mostrare: PSI, soglia, stati, accuracy e ritorno sotto soglia se osservato.
- Posizione nel report: LAB06: Serie temporale.
- Didascalia da usare solo se confermata: «Tabella locale del monitoring; i batch sono ordinati per sequenza della simulazione.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 06-04 — Alert con responsabilita

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB06. Directory: root.
- Comando:

```powershell
Get-Content .\LAB06\output\alerts.jsonl
```

- Mostrare: Prima attenzione, eventuale ALERT persistente, causa, canale, owner e notification_sent=false.
- Posizione nel report: LAB06: Regola e log.
- Didascalia da usare solo se confermata: «Notifica simulata a terminale e nel log; nessun messaggio Slack realmente inviato.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 06-05 — Grafico monitoring

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB06. Directory: root.
- Comando:

```powershell
Invoke-Item .\LAB06\output\monitoring.png
```

- Mostrare: Due pannelli leggibili, assi, legenda e soglie; allegare anche PNG originale.
- Posizione nel report: LAB06: Dashboard.
- Didascalia da usare solo se confermata: «Serie di PSI e accuracy sui batch simulati con le rispettive soglie storiche.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 06-06 — Cleanup e dati conservati

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB06. Directory: root.
- Comando:

```powershell
Get-Item .\LAB06\data\manifest.json,.\LAB06\data\model.pkl,.\LAB06\output\monitoring.json
```

- Mostrare: Conservazione per LAB07 e fine processo nel terminale.
- Posizione nel report: LAB06: Cleanup.
- Didascalia da usare solo se confermata: «Dati, modello e segnale mantenuti per la continuita con LAB07; nessun servizio di monitoring avviato.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 07-01 — Segnale degradato

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB07. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB07.explain_case
```

- Mostrare: Timestamp, ID batch, accuracy misurata, soglia e versione.
- Posizione nel report: LAB07: Segnale.
- Didascalia da usare solo se confermata: «L'analisi parte dal segnale di accuracy realmente calcolato nella simulazione LAB06.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 07-02 — Casi selezionati

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB07. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB07.explain_case
```

- Mostrare: 2–3 casi con input, classe predetta/reale, confidenza e motivo; includere ID.
- Posizione nel report: LAB07: Casi.
- Didascalia da usare solo se confermata: «Gli errori sulle etichette simulate sono distinti dai casi corretti considerati soltanto sospetti.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 07-03 — Contributi SHAP

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB07. Directory: root.
- Comando:

```powershell
.\.venv-labs\Scripts\python.exe -m LAB07.explain_case
```

- Mostrare: Classe spiegata, base/probabilita ricostruita e contributi.
- Posizione nel report: LAB07: SHAP.
- Didascalia da usare solo se confermata: «Contributi SHAP relativi alla classe predetta del caso identificato.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 07-04 — Waterfall SHAP

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB07. Directory: root.
- Comando:

```powershell
Invoke-Item .\LAB07\output\shap_waterfall.png
```

- Mostrare: ID caso, classe, feature, valori e scala; conservare PNG originale.
- Posizione nel report: LAB07: SHAP.
- Didascalia da usare solo se confermata: «Waterfall locale del caso analizzato; i contributi ricostruiscono la probabilita del modello.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 07-05 — Pesi e grafico LIME

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB07. Directory: root.
- Comando:

```powershell
Get-Content .\LAB07\output\comparison.json; Invoke-Item .\LAB07\output\lime.png
```

- Mostrare: Stesso caso/classe, regole, pesi e R2 locale; due immagini se necessario.
- Posizione nel report: LAB07: LIME.
- Didascalia da usare solo se confermata: «LIME approssima localmente la stessa predizione; la fedelta e riportata insieme ai pesi.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 07-06 — Confronto e nota business

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB07. Directory: root.
- Comando:

```powershell
Get-Content .\LAB07\output\summary.md; Get-Content .\LAB07\output\comparison.json
```

- Mostrare: Tabella segnale/caso/feature, concordanza effettiva, PSI delle top feature e azione proposta.
- Posizione nel report: LAB07: Confronto e nota business.
- Didascalia da usare solo se confermata: «Ranking e drift sono confrontati come associazioni; non costituiscono una prova causale del degrado.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## 07-07 — Cleanup LAB07

- [ ] Acquisito dopo esecuzione personale.
- Laboratorio: LAB07. Directory: root.
- Comando:

```powershell
Get-ChildItem .\LAB07\output
```

- Mostrare: File finali mantenuti, termine del comando e visualizzatori chiusi.
- Posizione nel report: LAB07: Cleanup.
- Didascalia da usare solo se confermata: «Grafici e risultati finali sono conservati come evidenze; le eventuali copie temporanee sono gestite dopo il backup.»
- Esito / percorso immagine: [DA COMPILARE DOPO ESECUZIONE].

## Chiusura

- [ ] Controllati tutti gli ID citati nei quattro report.
- [ ] PNG dei grafici salvati anche come originali, senza ritagli di assi o legenda.
- [ ] Eventuali errori/fallback riportati con il proprio output.
- [ ] ZIP delle evidenze aperto e verificato prima di rimuovere file.
- [ ] Cleanup descritto come realmente eseguito, incompleto o conservazione motivata.

Se un checkpoint non e stato verificato, lasciare [DA COMPILARE DOPO ESECUZIONE] o scrivere NON VERIFICATO con il motivo. Nessuno screenshot viene generato automaticamente per imitare il terminale.
