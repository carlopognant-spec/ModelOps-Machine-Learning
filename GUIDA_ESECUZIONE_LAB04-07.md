# Guida all'esecuzione manuale LAB04–07

Studente: Carlo Pognant. Modulo: ModelOps e Machine Learning — ITS ICT Piemonte.

Il codice e predisposto; nessun training, test, server, Docker o calcolo SHAP/LIME e stato eseguito durante la preparazione. Ogni risultato e **[DA COMPILARE DOPO ESECUZIONE]**. Non copiare i numeri storici nelle nuove tabelle. I comandi seguenti sono da eseguire personalmente e uno step alla volta: fermarsi in caso di errore, leggere il traceback e non continuare con file incompleti.

## Prima di iniziare

Tutti gli step usano **la root della repository**, salvo il terminale B che va anch'esso portato alla root. Il percorso specifico di questo PC e C:\Users\carlo\Desktop\ModelOps-Machine-Learning. Se la cartella viene spostata cambiare soltanto quel percorso nello step S-01. Non serve entrare in LABnn: i comandi usano moduli Python e gli script ricavano i percorsi da __file__. Anche l'invocazione con percorso assoluto degli script train/build/evaluate/rollback/simulate/monitor/explain_case e supportata; per Uvicorn avviare dalla root oppure specificare --app-dir con la root assoluta.

Usare un terminale **PowerShell**, non il pulsante Run Python File con un interprete casuale. Nel terminale A eseguire i client e raccogliere le metriche; B e riservato a Uvicorn. L'ambiente si chiama .venv-labs per lasciare separati i LAB precedenti. L'attivazione non e necessaria: ogni comando indica l'interprete esatto.

Dipendenze principali: NumPy 1.26.4, SciPy 1.13.1, scikit-learn 1.5.2, joblib 1.4.2; LAB04 aggiunge FastAPI/Pydantic/Uvicorn/httpx; LAB06 Matplotlib; LAB07 SHAP 0.46.0 e LIME 0.2.0.1 con Numba/llvmlite fissati. Pytest e predisposto per i test manualmente avviati. Python 3.12 preferito; sul PC e disponibile 3.11 come alternativa. Installazione e compatibilita operativa restano da verificare. Non usare Python 3.14 con questi pin.

La durata dei nuovi laboratori puo superare il timebox didattico: qui si preparano entrambi gli explainers e controlli aggiuntivi. Non servono MLflow, Prometheus, Grafana, account Slack o cloud. Le notifiche sono simulate e i dati del credito sintetici.

## Preparazione

### S-01 — Aprire la cartella

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Apri VS Code, File > Apri cartella, scegli ModelOps-Machine-Learning. Poi Terminale > Nuovo terminale, profilo PowerShell. Queste righe verificano root e modifiche.

```powershell
Set-Location -LiteralPath 'C:\Users\carlo\Desktop\ModelOps-Machine-Learning'
Get-Location
Get-ChildItem -Name
git status --short --branch
```

- Cosa osservare / file: Il percorso deve terminare con ModelOps-Machine-Learning e devono esserci LAB01–07 e README.md.
- Screenshot: Facoltativo: stato iniziale.
- Se fallisce: Se non esiste il percorso, apri la cartella reale e usa il suo percorso assoluto. Non eseguire reset o clean.
- Passaggio successivo: S-02.

### S-02 — Scegliere Python

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Cercare prima Python 3.12.

```powershell
py -0p
py -3.12 --version
```

- Cosa osservare / file: Se py -3.12 fallisce, sul PC ispezionato e disponibile py -3.11: usa il comando alternativo nello step successivo. Non scegliere il 3.14 predefinito.
- Screenshot: Nessuno richiesto.
- Se fallisce: Se py non esiste, installa Python 3.12 x64 da python.org con Python Launcher, riapri VS Code. Se hai python 3.12 senza launcher usa python --version e python -m venv nello step successivo.
- Passaggio successivo: S-03.

### S-03 — Creare ambiente dedicato

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Creare un ambiente nuovo, isolato da LAB01–03. Esegui solo se .venv-labs non esiste.

```powershell
py -3.12 -m venv .venv-labs
```

- Cosa osservare / file: Deve comparire .venv-labs\Scripts\python.exe.
- Screenshot: Nessuno richiesto.
- Se fallisce: Alternativa gia disponibile su questo PC: py -3.11 -m venv .venv-labs. Esegui UNA sola delle due varianti. Un ambiente gia esistente con Python 3.14 va conservato/rinominato prima di ricrearlo; non riutilizzarlo con queste dipendenze.
- Passaggio successivo: S-04.

### S-04 — Verificare interprete

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Usare direttamente l'eseguibile dell'ambiente: non serve attivare Activate.ps1.

```powershell
.\.venv-labs\Scripts\python.exe --version
.\.venv-labs\Scripts\python.exe -m pip --version
```

- Cosa osservare / file: Versione 3.12.x o 3.11.x; percorso pip dentro .venv-labs.
- Screenshot: Facoltativo: versione ambiente.
- Se fallisce: In VS Code Ctrl+Shift+P > Python: Select Interpreter > Enter interpreter path > .venv-labs\Scripts\python.exe. Se PowerShell blocca Activate.ps1 continua con il percorso esplicito, senza cambiare policy globali.
- Passaggio successivo: S-05.

### S-05 — Installare dipendenze

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Installare insieme le dipendenze coerenti dei quattro LAB; richiede rete, nessun servizio a pagamento.

```powershell
.\.venv-labs\Scripts\python.exe -m pip install -r .\LAB04\requirements.txt -r .\LAB05\requirements.txt -r .\LAB06\requirements.txt -r .\LAB07\requirements.txt
.\.venv-labs\Scripts\python.exe -m pip check
```

- Cosa osservare / file: pip deve terminare senza errori e pip check senza conflitti. Questo non dimostra che i laboratori funzionino.
- Screenshot: Facoltativo: installazione e pip check.
- Se fallisce: Se wheel non disponibile controlla di non usare 3.14 o Python 32 bit. Per problemi SHAP/Numba usare l'ambiente 3.11/3.12 e reinstallare dai requirements, senza aggiornare numpy da solo.
- Passaggio successivo: S-06.

### S-06 — Conservare evidenze

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Salvare un transcript autentico di questo terminale. Crea a mano sottocartelle LAB04–07 per gli screenshot se desiderato.

```powershell
New-Item -ItemType Directory -Path .\evidenze -Force
Start-Transcript -Path ('.\evidenze\sessione-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.txt')
```

- Cosa osservare / file: PowerShell mostra il percorso del transcript. I file sono locali e ignorati da Git.
- Screenshot: Ogni screenshot dovra includere comando e risposta; usare Win+Shift+S e salvare PNG.
- Se fallisce: Il transcript del terminale A non cattura il terminale B. Per conservare anche i log del server avvia un transcript distinto nel terminale B prima di Uvicorn.
- Passaggio successivo: 04-01.

## LAB04

### 04-01 — Training

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Generare modelli v2/v3 sullo stesso split wine con rumore e seed documentati.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB04.train
```

- Cosa osservare / file: Due accuracy misurate; LAB04/artifacts/model_v2.pkl, model_v3.pkl e metadati .json. Nessun valore e imposto.
- Screenshot: 04-01: metriche e percorsi.
- Se fallisce: ModuleNotFoundError: ripetere S-05 con lo stesso interprete. Non proseguire se training fallisce. Rilanciare sovrascrive i due artefatti: acquisire prima le evidenze esistenti.
- Passaggio successivo: 04-02.

### 04-02 — Gate e registry

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Verificare artefatti e confrontare metriche non arrotondate con 0.85.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB04.build_registry
Get-Content .\LAB04\registry.json
Get-Content .\LAB04\registry.md
```

- Cosa osservare / file: Stato e motivazione per entrambe le versioni, active_version. Attesa didattica: v2 attiva e v3 scartata, da confermare. I JSON sono generati solo ora.
- Screenshot: 04-02: registry, soglia e decisione.
- Se fallisce: Se v2 e sotto soglia lo script si ferma: non avviare API, conservare output e annotare mancata riproduzione. Non correggere metriche a mano. Se v3 supera davvero la soglia, il registry la promuove.
- Passaggio successivo: 04-03.

### 04-03 — Avviare API nel terminale B

- Directory: root della repository, terminale B.
- Scopo: Apri un secondo terminale PowerShell (B) in VS Code, esegui Set-Location alla root come S-01, poi questo comando. Lascia B attivo; usa A per i client.

```powershell
.\.venv-labs\Scripts\python.exe -m uvicorn LAB04.app:app --host 127.0.0.1 --port 8000
```

- Cosa osservare / file: Application startup complete e modello/versione caricati. Il prompt B resta occupato.
- Screenshot: Facoltativo: startup e versione.
- Se fallisce: Modello/registry assente: eseguire 04-01/02 in A. Hash o versione diversi: fermare B e ricostruire registry dopo il training. Porta occupata: vedere troubleshooting; non uccidere processi sconosciuti.
- Passaggio successivo: 04-04 nel terminale A.

### 04-04 — Provare endpoint

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Nel terminale A inviare richieste reali al server di B.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB04.test_predict
```

- Cosa osservare / file: HTTP 200 con prediction e model_version coerente col registry; HTTP 422 per richieste invalide senza prediction; NaN/Infinity rifiutati. PASS solo se il client termina senza assertion/errori.
- Screenshot: 04-03 risposta valida e versione; 04-04 risposte 422.
- Se fallisce: Connection refused: B deve restare avviato e mostrare startup complete. Errore diverso da 422: conservare output e non dichiarare superato. Le 13 feature sono nell'ordine wine dei metadati.
- Passaggio successivo: 04-05.

### 04-05 — Test automatici predisposti

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Eseguire manualmente test isolati API, gate e identita; questi test non fanno training.

```powershell
.\.venv-labs\Scripts\python.exe -m pytest .\LAB04\tests -q
```

- Cosa osservare / file: Risultato effettivo pytest, da trascrivere nel report. Le fixture non sono misure di accuracy del modello reale.
- Screenshot: 04-05 se utile al report; conservare comunque l'output.
- Se fallisce: Non eseguire pytest sull'intero repository: i LAB precedenti non rientrano in queste verifiche. Se fallisce conservare traceback.
- Passaggio successivo: 04-06 oppure ramo Docker D-01.

### 04-06 — Fermare API locale

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Prima premi Ctrl+C in B e attendi shutdown complete, poi esegui la verifica in A. La pressione Ctrl+C e manuale, non una stringa da incollare.

```powershell
Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
```

- Cosa osservare / file: Nessun listener del server appena fermato; se rimane un processo identificarlo prima di agire.
- Screenshot: 04-07 cleanup locale; annotare se altri servizi usano la porta.
- Se fallisce: Questo controllo richiede Windows; se non supportato usa i log di shutdown di B e documenta il limite.
- Passaggio successivo: 05-01 o D-01.

## Docker LAB04 (facoltativo)

### D-01 — Verificare Docker Desktop

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Aprire Docker Desktop, attendere Engine running e usare Linux containers. Fermare prima Uvicorn per liberare 8000.

```powershell
docker version
```

- Cosa osservare / file: Devono comparire Client e Server; la sola CLI non prova che il daemon funzioni.
- Screenshot: Nessuna evidenza di build ancora.
- Se fallisce: Se daemon non disponibile fermare questo ramo: usare 04-03/04-04 come fallback e scrivere Docker non verificato.
- Passaggio successivo: D-02.

### D-02 — Build da artefatti reali

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Costruire usando LAB04 come build context, dopo training e registry; tutti i Test-Path devono essere True prima della build.

```powershell
Test-Path .\LAB04\registry.json
Test-Path .\LAB04\artifacts\model_v2.pkl
Test-Path .\LAB04\artifacts\model_v3.pkl
docker build -t carlo-lab04-serving:local .\LAB04
```

- Cosa osservare / file: Build senza errori. Non e ancora una prova dell'endpoint.
- Screenshot: 04-06a build realmente eseguita.
- Se fallisce: File mancanti: ripetere 04-01/02. Non usare modelli segnaposto. Ambiente locale 3.12 e container 3.11: verificare gli avvisi e il serving; per allineamento completo usare il fallback locale 3.11.
- Passaggio successivo: D-03.

### D-03 — Avviare container

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Avviare esclusivamente il container di questo laboratorio.

```powershell
docker run -d --name carlo-lab04-serving -p 127.0.0.1:8000:8000 carlo-lab04-serving:local
docker logs carlo-lab04-serving
```

- Cosa osservare / file: Attendere nei log startup complete. Ripetere docker logs se il caricamento e ancora in corso.
- Screenshot: 04-06b startup container.
- Se fallisce: Nome gia presente: ispezionare docker ps -a e non rimuovere risorse estranee. Porta occupata: fermare solo il proprio server precedente.
- Passaggio successivo: D-04.

### D-04 — Verificare serving container

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Riutilizzare il client di 04-04 contro il container, con gli stessi artefatti della build.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB04.test_predict
```

- Cosa osservare / file: HTTP 200/versione e 422 validati realmente. Dopo nuove build/modifiche ricreare il container, non confrontare registry aggiornato con un vecchio container.
- Screenshot: 04-06c verifica Docker soltanto se eseguita.
- Se fallisce: Se connection refused controllare docker logs e docker ps. Non dichiarare Docker verificato solo perche la build termina.
- Passaggio successivo: D-05.

### D-05 — Cleanup risorse Docker

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Dopo gli screenshot eliminare solo container e immagine di questo LAB. Eseguire solo se creati da te.

```powershell
docker stop carlo-lab04-serving
docker rm carlo-lab04-serving
docker image rm carlo-lab04-serving:local
docker ps -a --filter name=carlo-lab04-serving
docker image ls carlo-lab04-serving
```

- Cosa osservare / file: Controllare output stop/rm e assenza delle risorse nominate. Nessun prune globale.
- Screenshot: 04-07 cleanup Docker, aggiuntivo a quello locale.
- Se fallisce: Se immagine ancora usata ispezionare i propri container; non forzare rimozioni di altre risorse. In caso di errore segnare cleanup incompleto.
- Passaggio successivo: 05-01.

## LAB05

### 05-01 — Misurare due versioni

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Training sul dataset medico dichiarato, stesso split e batch per v1/v2; latenza reale di predict per singola osservazione.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB05.evaluate
```

- Cosa osservare / file: Accuracy, latency_mean_ms e numero chiamate; modelli e evaluation_batch.npz in artifacts, metrics.json in LAB05. Salvare eventuali warning.
- Screenshot: 05-01 metriche e latenza con unita.
- Se fallisce: ConvergenceWarning: non nasconderlo. Registrare e discutere il limite; non riscalare o cambiare parametri per forzare numeri identici alla relazione.
- Passaggio successivo: 05-02.

### 05-02 — Gate e rollback locale

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Rilasciare v2 nel registry simulato, confrontare con soglia 0.02 e, se necessario, ripristinare v1. Lo script ricarica realmente il modello finale.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB05.rollback_versions
Get-Content .\LAB05\registry_before.json
Get-Content .\LAB05\registry.json
Get-Content .\LAB05\post_verification.json
```

- Cosa osservare / file: PRIMA v2; metrica v1/v2, calo e soglia; DOPO versione finale e accuracy rivalutata. Rollback solo se il calo supera 0.02.
- Screenshot: 05-02 gate; 05-03 registry prima/dopo; 05-04 verifica.
- Se fallisce: Se non c'e calo sufficiente lo script mantiene v2: descrivere nessun rollback. Non alterare accuracy. Hash/batch incoerenti: ricostruire con 05-01 e conservare evidenze precedenti.
- Passaggio successivo: 05-03.

### 05-03 — Leggere log autentico

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Leggere eventi append-only registrati durante la decisione, senza inventare nuovi timestamp.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB05.rollback_log
```

- Cosa osservare / file: Timestamp UTC con offset, run_id, versione iniziale/finale, soglia, calo e verifica.
- Screenshot: 05-05 log rollback.
- Se fallisce: Log assente: eseguire 05-01/02. Run ripetute aggiungono eventi: usare il run_id corrispondente alla propria evidenza.
- Passaggio successivo: 05-04.

### 05-04 — Test automatici

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Provare confini del gate e simulazioni isolate di ripristino/mantenimento con fixture.

```powershell
.\.venv-labs\Scripts\python.exe -m pytest .\LAB05\tests -q
```

- Cosa osservare / file: Esito pytest effettivo; le fixture non sono nuove metriche sperimentali.
- Screenshot: Facoltativo: esito test.
- Se fallisce: Conservare errori prima di modificare file; non confondere test delle fixture con la verifica post-rollback sui modelli allenati.
- Passaggio successivo: 05-05.

### 05-05 — Inventario per cleanup

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Controllare quali evidenze conservare; questi script terminano autonomamente, senza server.

```powershell
Get-ChildItem .\LAB05\artifacts
Get-Item .\LAB05\registry_before.json,.\LAB05\registry.json,.\LAB05\metrics.json,.\LAB05\post_verification.json,.\LAB05\rollback_events.jsonl
```

- Cosa osservare / file: Modelli e batch presenti per ripetere la verifica; nessun MLflow o tag Git creato dal codice.
- Screenshot: 05-06 inventario cleanup: dichiarare conservati se non eliminati.
- Se fallisce: Non cancellare artefatti se vuoi ripetere 05-02; per rigenerare usare 05-01, poi 05-02.
- Passaggio successivo: 06-01.

## LAB06

### 06-01 — Generare scenario condiviso

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Generare train, reference, 30 batch storici e 5 recenti; addestrare il modello sintetico e salvare predizioni/etichette reali simulate.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB06.simulate
```

- Cosa osservare / file: LAB06/data/manifest.json, model.pkl, training.npz, reference.npz, history-00..29.npz e recent-00..04.npz. Ogni batch ha ID, ruolo, timestamp e accuracy misurata.
- Screenshot: 06-01 dati e storico.
- Se fallisce: Se data non vuota lo script si ferma per proteggere le evidenze. Se la simulazione e completa prosegui a monitor. Se incompleta archivia/rinomina la cartella prima di ripetere; non mischiare file di due run.
- Passaggio successivo: 06-02.

### 06-02 — Calibrare e monitorare

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Ricavare soglie dai soli batch storici, valutare recenti, applicare attenzione/alert con 2 superamenti consecutivi e reset.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB06.monitor
Get-Content .\LAB06\output\dashboard.md
```

- Cosa osservare / file: CALIBRAZIONE STORICA, PSI, soglia, accuracy, stati, responsabilita, canale simulato e azione. output/monitoring.json, alerts.jsonl, dashboard.md, monitoring.png.
- Screenshot: 06-02 calibrazione; 06-03 serie/sotto soglia; 06-04 alert simulato.
- Se fallisce: Se nessun alert viene misurato annotarlo. Non spostare la soglia per far apparire un alert. Se hash differente evitare dati modificati e rigenerare una simulazione coerente dopo archiviazione.
- Passaggio successivo: 06-03.

### 06-03 — Aprire grafico e log

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Aprire l'immagine realmente generata e leggere log, senza invio Slack.

```powershell
Invoke-Item .\LAB06\output\monitoring.png
Get-Content .\LAB06\output\alerts.jsonl
```

- Cosa osservare / file: Grafico PSI e accuracy con soglie e assi; notification_sent=false. ATTENZIONE al primo superamento, ALERT dal secondo, reset al ritorno.
- Screenshot: 06-05 grafico di monitoring; completare 06-04 con causa/canale/owner.
- Se fallisce: Se il PNG manca controllare errori di 06-02 e permessi della cartella. Il backend Agg salva senza finestra interattiva; Invoke-Item richiede associazione immagini Windows.
- Passaggio successivo: 06-04.

### 06-04 — Test PSI e persistenza

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Verificare casi semplici PSI, bin vuoti, distribuzione stabile, drift e reset.

```powershell
.\.venv-labs\Scripts\python.exe -m pytest .\LAB06\tests -q
```

- Cosa osservare / file: Esito effettivo pytest, senza sostituire la serie temporale sperimentale.
- Screenshot: Facoltativo: test.
- Se fallisce: Non considerare completato un checkpoint se il comando non e stato eseguito o fallisce.
- Passaggio successivo: 06-05.

### 06-05 — Conservare dati per LAB07

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Controllare prerequisiti del LAB07. Conservare tutta LAB06/data e output, non soltanto questi quattro file.

```powershell
Get-Item .\LAB06\data\manifest.json,.\LAB06\data\model.pkl,.\LAB06\output\monitoring.json,.\LAB06\output\monitoring.png
```

- Cosa osservare / file: File esistenti. Nessun exporter, Grafana o servizio esterno e stato avviato dagli script.
- Screenshot: 06-06 inventario cleanup, con conservazione motivata per LAB07.
- Se fallisce: Non cancellare dati o modello prima di LAB07. Il processo monitor termina da solo, chiudere solo il visualizzatore del grafico se necessario.
- Passaggio successivo: 07-01.

## LAB07

### 07-01 — Spiegare un batch segnalato

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Leggere il segnale reale della simulazione LAB06; selezionare 3 casi; spiegare il primo con SHAP e LIME per la stessa classe.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB07.explain_case
```

- Cosa osservare / file: SEGNALE con timestamp/batch/accuracy/soglia; casi con feature/predetto/reale/confidenza/motivo; contributi, classe, confronto e PSI delle feature influenti. LAB07/output contiene cases.json, comparison.json, summary.md, shap_waterfall.png, lime.png, lime.html.
- Screenshot: 07-01 segnale; 07-02 casi; 07-03 SHAP; 07-05 LIME; 07-06 confronto.
- Se fallisce: Prima eseguire 06-01/02. Nessuna accuracy sotto soglia: il programma si ferma, non si inventa un alert. Se SHAP/LIME fallisce restano segnale/casi (se gia scritti), ma spiegazioni non completate: usare troubleshooting e non dichiarare il LAB verificato.
- Passaggio successivo: 07-02.

### 07-02 — Aprire grafici e interpretazione

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Consultare artefatti per lo stesso caso/classe, confrontare ranking e verificare PSI delle top feature.

```powershell
Invoke-Item .\LAB07\output\shap_waterfall.png
Invoke-Item .\LAB07\output\lime.png
Invoke-Item .\LAB07\output\lime.html
Get-Content .\LAB07\output\summary.md
Get-Content .\LAB07\output\comparison.json
```

- Cosa osservare / file: SHAP base+contributi ricostruisce probabilita; LIME riporta pesi e R2 locale. Concordanza calcolata dagli indici feature, non imposta. Nota business con rischi e azioni.
- Screenshot: 07-04 waterfall; 07-05b grafico LIME; 07-06 tabella e conclusione.
- Se fallisce: Se R2 LIME basso discutere fedelta limitata; non presentare il peso LIME come valore SHAP o causalita. Se HTML non si apre usare lime.png e registrare fallback.
- Passaggio successivo: 07-03.

### 07-03 — Test normalizzazione e selezione

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Eseguire test isolati sui formati SHAP e sulla priorita dei casi.

```powershell
.\.venv-labs\Scripts\python.exe -m pytest .\LAB07\tests -q
```

- Cosa osservare / file: Esito pytest effettivo. Questi test non sostituiscono il calcolo reale SHAP/LIME di 07-01.
- Screenshot: Facoltativo: risultato test.
- Se fallisce: Formato SHAP non supportato/additivita fallita: non cambiare classe arbitrariamente; salvare traceback e versioni installate.
- Passaggio successivo: 07-04.

### 07-04 — Cleanup conservativo

- Directory: root della repository, terminale A salvo indicazione.
- Scopo: Dopo gli screenshot chiudere visualizzatori immagini/browser. Gli script SHAP/LIME terminano senza server o kernel; conservare i grafici finali come evidenze.

```powershell
Get-ChildItem .\LAB07\output
Get-Item .\LAB06\data\manifest.json,.\LAB06\output\monitoring.json
```

- Cosa osservare / file: Elenco degli artefatti che decidi di mantenere. Annotare cosa e stato mantenuto e perche; questo comando non cancella nulla.
- Screenshot: 07-07 inventario e cleanup documentato.
- Se fallisce: Eliminare soltanto copie temporanee non necessarie; non eliminare lime.html se e parte della consegna. Vedere sezione cleanup dopo il backup.
- Passaggio successivo: F-01.

## F-01 — Compilare i report senza perdere evidenze

Directory: root. Dopo l'ultimo comando di calcolo eseguire:

```powershell
.\.venv-labs\Scripts\python.exe -m pip freeze
Get-Date -Format o
git status --short
```

Scopo: registrare ambiente effettivo, data e file da rivedere. Screenshot facoltativo; riportare versioni e data nei report. Se il comando pip usa un altro ambiente tornare a S-04. Passaggio successivo: compilare REPORT_LAB04.md, REPORT_LAB05.md, REPORT_LAB06.md, REPORT_LAB07.md in VS Code, inserendo i propri valori e le immagini secondo PIANO_SCREENSHOT.md. Non spuntare checkpoint non verificati.

I numeri della vecchia relazione sono storici: LAB04 v2 0.8889, v3 0.5; LAB05 v1 0.9474, v2 0.9123, calo 0.0351. Le nuove accuracy possono differire con ambiente e convergenza. Nessuna differenza deve essere corretta manualmente per ottenere lo stesso numero.

In LAB05 il dataset e medico per continuita col lavoro precedente. Lo scenario di feature mismatch/5xx resta una motivazione didattica; il codice misura modelli di diversa complessita, senza introdurre un vero mismatch e senza misurare HTTP 5xx. La latenza e solo locale di predict, in millisecondi per singola osservazione: non e latenza API, p95 o SLA.

In LAB06 i timestamp registrano l'esecuzione reale UTC; la successione e data dagli ID/sequence dei batch. Non sono settimane realmente trascorse. La soglia e una regola empirica su dati sintetici, non una garanzia di falsi positivi. L'accuratezza e disponibile soltanto perche le etichette sono simulate e note.

In LAB07 il grafico e un'analisi del modello per la classe indicata, non una prova di discriminazione o causalita. Confrontare segni, ranking e R2 LIME; riportare anche un eventuale disaccordo. La nota business generata in output/summary.md e una base da rileggere, e va collegata alle proprie osservazioni prima di copiarla in Google Docs. Il documento Google non viene modificato automaticamente.

## F-02 — Backup prima del cleanup

Directory: root; screenshot facoltativo dell'archivio creato.

```powershell
Stop-Transcript
Compress-Archive -Path .\LAB04,.\LAB05,.\LAB06,.\LAB07,.\evidenze -DestinationPath (Join-Path $env:USERPROFILE ('Desktop\ModelOps-evidenze-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.zip'))
```

Scopo: chiudere il transcript e conservare sorgenti, modelli, dati, registry, grafici, HTML e screenshot prima di rimuovere file. Se non avevi aperto un transcript, salta Stop-Transcript. Chiudi anche l'eventuale transcript B dopo aver fermato Uvicorn. Osservare il file ZIP sul Desktop; aprirlo e verificare che contenga i file necessari. Se Compress-Archive fallisce per file aperti chiudere server/visualizzatori e riprovare con un nome nuovo. Passaggio successivo: cleanup opzionale F-03 oppure conservazione motivata.

## F-03 — Cleanup dopo verifiche e screenshot

Non e stata effettuata alcuna cancellazione durante la preparazione. **Stato cleanup: [DA COMPILARE DOPO ESECUZIONE].** Le rimozioni sotto sono opzionali e vanno fatte soltanto dopo backup verificato.

| Categoria | Azione |
|---|---|
| Sorgenti, requirements, Dockerfile, test, guide e report | Conservare |
| Dataset originali LAB01–03 | Conservare, non toccare |
| Registry, metadati JSON, log JSONL, tabelle e report | Conservare come evidenze |
| Modelli LAB04 | Conservare fino ai test locali e Docker; rigenerabili con 04-01, poi obbligatoriamente 04-02 |
| Modelli e batch LAB05 | Conservare fino a post-verifica; rigenerabili con 05-01/02 |
| Tutta LAB06/data | Conservare almeno fino al termine LAB07; manifest, modello, training, reference e batch devono restare coerenti |
| LAB06/output e LAB07/output | Conservare immagini/HTML/JSON finali; rimuovere solo copie temporanee non usate |
| Cache __pycache__, .pytest_cache | Ignorate da Git; nessuna rimozione automatica. Se mantenute, dichiararlo |
| Ambiente .venv-labs | Conservare per riesecuzione; ignorato da Git |
| Server Uvicorn | Ctrl+C in B, verificare shutdown e porta con 04-06 |
| Container/immagine del LAB04 | Usare D-05 soltanto se effettivamente creati |
| Exporter/Grafana/MLflow | Non avviati da questi script: non dichiarare di averli spenti |

Per alleggerire soltanto gli artefatti LAB04/05, dopo aver verificato la root come S-01 e il backup, eseguire in root i comandi seguenti **solo se non servono altre verifiche**:

```powershell
Remove-Item -LiteralPath '.\LAB04\artifacts\model_v2.pkl','.\LAB04\artifacts\model_v3.pkl'
Remove-Item -LiteralPath '.\LAB05\artifacts\model-1.0.0.pkl','.\LAB05\artifacts\model-2.0.0.pkl'
Get-ChildItem .\LAB04\artifacts
Get-ChildItem .\LAB05\artifacts
```

Scopo: rimuovere file riproducibili nominati esattamente; nessuna cancellazione ricorsiva. Osservare che i metadati e il batch LAB05 restano, i modelli elencati no. Se un file non esiste leggere l'errore e non ampliare i percorsi di rimozione. Screenshot cleanup: 04-07/05-06 dopo il comando, specificando cosa e stato rimosso. Passaggio successivo: aggiornare la sezione cleanup dei report.

Per LAB06 e LAB07 la conservazione dei dataset/grafici e motivata dal collegamento tra laboratori e dalla consegna: annotare questa scelta invece di cancellare evidenze necessarie. Non eseguire prune, git clean, reset --hard o cancellazioni globali di processi/cache.

## Troubleshooting comune

- **Python non trovato:** usare py -0p; installare Python 3.12 x64 e il Launcher se manca. Riavviare VS Code. Il percorso esplicito dell'ambiente e obbligatorio per evitare il 3.14 predefinito.
- **Ambiente non attivabile:** non serve attivarlo; usare sempre .\.venv-labs\Scripts\python.exe. Se il file manca, creare l'ambiente con S-03.
- **Dipendenze mancanti:** ripetere S-05 con l'interprete dell'ambiente. Non installare globalmente e non cambiare pin isolati. pip check verifica dipendenze dichiarate, non la funzionalita.
- **Artefatto .pkl assente:** LAB04 04-01 poi 04-02; LAB05 05-01; LAB06 06-01 solo dopo archiviazione di eventuale simulazione incompleta. Non scaricare pickle ignoti.
- **Porta 8000 occupata:** in root eseguire Get-NetTCPConnection -LocalPort 8000 -State Listen e identificare OwningProcess con Get-Process -Id NUMERO (sostituire NUMERO con il PID osservato). Fermare con Ctrl+C soltanto il proprio server. Alternativa: avviare Uvicorn con --port 8001 e client con --url http://127.0.0.1:8001; per Docker usare -p 127.0.0.1:8001:8000. Documentare la variante.
- **Server non avviato:** leggere tutto il log di B, verificare startup complete. Non chiudere B mentre esegui il client. Usare la root come directory per -m uvicorn LAB04.app:app.
- **Docker non disponibile:** usare il ramo locale 04-03/04-04; indicare Docker NON VERIFICATO e il motivo. Nessun risultato Docker puo essere dedotto dal Dockerfile.
- **SHAP/LIME incompatibili:** raccogliere pip freeze e traceback, controllare Python e pin. Per un nuovo ambiente 3.11/3.12 reinstallare tutti i requirements. La funzione normalize_shap supporta lista per classe e array (1,feature,classi); altri formati vengono rifiutati. Non cambiare class_index per eliminare un errore.
- **SHAP lento:** il codice spiega una sola riga con TreeExplainer; LIME usa 5000 perturbazioni su 4 feature. Attendere la conclusione o interrompere con Ctrl+C e documentare il passaggio non completato. Il fallback tabella/casi e parziale, non una spiegazione completata.
- **Dati monitoring mancanti:** eseguire nell'ordine 06-01 e 06-02, poi 07-01. Conservare tutta LAB06/data, non copiare un solo batch isolato. Hash/run_id proteggono da dati mescolati.
- **Grafici mancanti:** leggere l'eventuale traceback prima del messaggio finale, verificare permessi di scrittura. Le directory output sono create dagli script; Agg salva senza GUI. Usare i percorsi assoluti indicati nei messaggi.
- **Alert assente:** non impostare a mano il flag; conservare dati/metriche e dichiarare mancata riproduzione. La soglia deriva dallo storico, mai dal batch problematico.
- **PowerShell interrompe un comando esterno:** controllare $LASTEXITCODE subito dopo Python/Docker. Se diverso da 0 non continuare allo step successivo.

## Git: preparazione della consegna, solo su successiva decisione dello studente

Directory: root. Questi controlli sono di sola lettura:

```powershell
git status --short
git diff --stat
git diff -- .gitignore README.md
git ls-files --others --exclude-standard
```

Scopo: rivedere modifiche e file nuovi. git diff non mostra il contenuto dei file ancora non tracciati: aprirli in VS Code prima di selezionarli. Screenshot facoltativo; se compaiono file estranei non includerli. Passaggio successivo, soltanto quando decidi di preparare il commit:

```powershell
git add -- .gitignore README.md ANALISI_INIZIALE.md GUIDA_ESECUZIONE_LAB04-07.md PIANO_SCREENSHOT.md LAB04 LAB05 LAB06 LAB07
git diff --cached --stat
git diff --cached
```

Osservare l'intero contenuto in staging, inclusi eventuali file generati. .venv-labs, cache, evidenze locali, pickle nuovi e LAB06/data sono ignorati. I piccoli JSON/Markdown generati e i grafici in output possono essere inclusi se li hai rivisti e se sono le evidenze autentiche che vuoi consegnare. Non pubblicare dataset/modelli grandi, screenshot non pertinenti o informazioni personali. Per togliere dallo staging un file indesiderato, usare git restore --staged -- PERCORSO dopo aver sostituito PERCORSO con il singolo file osservato: il contenuto locale viene mantenuto.

**Non e stato eseguito alcun commit o push.** Soltanto dopo la tua successiva decisione/autorizzazione, esegui personalmente:

```powershell
git commit -m "feat: prepara laboratori ModelOps 04-07 e guide manuali"
git push origin main
git status --short --branch
```

Se il push viene rifiutato, leggere il motivo e non usare --force; non sovrascrivere lavoro remoto. Aprire la propria repository GitHub, verificare il commit e le cartelle LAB04–07, i report e le guide. I modelli ignorati non appariranno: i comandi di rigenerazione devono restare documentati. Conservare separatamente lo ZIP delle evidenze e salvare i report prima di chiudere VS Code.
