---
ID: 1
Origin: 1
UUID: c10f1ccd
Status: In Progress
---

# Piano: completamento LAB02 CI/CD e pipeline ML

**Target Release:** TBD: il repository non contiene roadmap, versione di progetto o release artifact da cui ricavare un numero semver.
**Epic Alignment:** Lab 02 - CI/CD, automazione workflow e pipeline
**Status:** In Progress

## Changelog

| Date | Handoff | Request | Summary |
|---|---|---|---|
| 2026-09-23 | Planner -> Implementer | Seguire il piano | Implementazione avviata: test di prerequisito, punto di ingresso dalla root e report in aggiornamento. |

## Value Statement and Business Objective

Come studente, voglio una pipeline ML eseguibile in modo riproducibile e con dipendenze tra gli stadi verificabili, così da dimostrare che dati non validi o metriche insufficienti impediscono la consegna dell'artefatto.

## Stato rilevato

Sono gia presenti:

- `LAB02/tests/test_data.py` con controlli su colonne attese, target non nullo e valori convertibili;
- `LAB02/pipeline.py` con gli stadi `validate`, `train` e `gate`;
- `LAB02/run_pipeline.sh` con `set -euo pipefail`, ordine degli stadi e log `run.log`;
- `LAB02/LAB02_REPORT.md` con una run valida, un fallimento intenzionale documentato, limiti e cleanup;
- un gate numerico con soglia predefinita `0.75`.

Verifiche eseguite:

- `pytest` dalla root del repository fallisce in raccolta perché i test importano `data_loader` come modulo locale di `LAB02`;
- la stessa sequenza eseguita dalla directory `LAB02` passa: 2 test, training con accuracy `0.833`, gate promosso;
- `train` può essere invocato autonomamente e produce un modello senza dimostrare che `validate` sia stato eseguito nella stessa run;
- non sono presenti roadmap, file di versione o release artifact nel repository.

## Obiettivo del piano

Portare il deliverable da una soluzione funzionante in condizioni locali specifiche a una consegna riproducibile, esplicita sulle dipendenze e completa nelle evidenze richieste dal laboratorio. Lo scope resta limitato a `LAB02` e alla documentazione necessaria.

## Assunzioni e vincoli

- Il dataset didattico e il modello semplice esistenti restano invariati salvo necessità emersa durante l’implementazione.
- L’ambiente primario può essere Windows, quindi i comandi documentati devono indicare chiaramente la directory di esecuzione e l’alternativa allo script Bash quando necessario.
- L’assenza di un servizio CI remoto è accettabile come fallback locale, purché la sequenza e i codici di uscita siano dimostrabili.
- Non esistono dipendenze applicative o packaging di progetto da versionare nel repository.
- Il piano non richiede l’introduzione di un framework CI remoto: YAGNI per il timebox del laboratorio.

## Lavoro da completare

### 1. Rendere riproducibile il punto di ingresso

**Obiettivo:** eliminare l’ambiguita sul contesto di esecuzione dei test e della pipeline.

**Attivita:**

1. Definire un unico punto di ingresso documentato per eseguire la sequenza completa dalla root oppure dichiarare formalmente `LAB02` come working directory obbligatoria.
2. Allineare i comandi nel report con il comportamento effettivo su Windows e con quello di `run_pipeline.sh`.
3. Assicurare che il log finale distingua chiaramente output dello stadio e risultato orchestrato (`PASS`/`FAIL`).

**Criteri di accettazione:**

- Un utente che segue i comandi del report non incontra l’errore di import osservato dalla root.
- La sequenza completa produce un log leggibile con `TEST`, `VALIDATE`, `TRAIN` e `GATE` in ordine.
- Il percorso dell’artefatto e la soglia usata sono visibili nel log.

**Dipendenze:** nessuna.
**Owner suggerito:** Implementer.

### 2. Rendere esplicita la dipendenza validate -> train

**Obiettivo:** garantire il requisito didattico secondo cui il training non parte su dati non validati, anche quando gli stadi vengono richiamati singolarmente.

**Attivita:**

1. Scegliere e documentare il contratto di orchestrazione: o `train` esegue/verifica un prerequisito di validazione, oppure accetta solo un marker/artefatto di validazione prodotto dallo stadio precedente.
2. Definire il comportamento in caso di prerequisito assente, dataset cambiato o validazione fallita: messaggio comprensibile e exit code diverso da zero.
3. Mantenere il gate dipendente da un modello effettivamente generato dal training corrente e da una metrica presente nell’artefatto.

**Criteri di accettazione:**

- Una validazione fallita impedisce il training nella sequenza orchestrata.
- Un invito diretto a `train` senza prerequisito non viene presentato come pipeline completa.
- Il gate non promuove un artefatto mancante, illeggibile o sotto soglia.

**Dipendenze:** lavoro 1 per poter verificare il contratto dai comandi documentati.
**Owner suggerito:** Implementer.

### 3. Chiudere la prova di fallimento e la documentazione

**Obiettivo:** rendere l’evidenza del blocco verificabile senza lasciare dati o modelli alterati.

**Attivita:**

1. Conservare nel report la procedura del fallimento intenzionale con dataset temporaneo senza target, messaggio e codice di uscita.
2. Esplicitare che dopo il fallimento il training non viene eseguito.
3. Aggiornare limiti e fallback: esecuzione locale, assenza di CI remoto, dataset sintetico e soglia didattica non basata su baseline produttiva.
4. Riportare il cleanup effettivamente eseguito, distinguendo `run.log` come evidenza finale dagli artefatti temporanei.

**Criteri di accettazione:**

- Il report contiene esiti `PASS`/`FAIL` per ogni stadio e una nota finale sui limiti.
- La prova negativa dimostra il blocco prima del training.
- Non restano nel repository CSV alterati o modelli generati solo per la prova.

**Dipendenze:** lavoro 2.
**Owner suggerito:** Implementer, con revisione del proprietario della consegna.

### 4. Aggiornare gli artefatti di release

**Obiettivo:** chiudere il piano con una decisione coerente sul versionamento del deliverable.

**Attivita:**

1. Verificare con il responsabile della roadmap quale release deve includere il completamento di LAB02.
2. Se il repository resta privo di versionamento applicativo, registrare esplicitamente questa scelta nel report o nella documentazione di progetto.
3. Se viene assegnata una release, aggiornare gli eventuali artefatti di versione e il changelog secondo le convenzioni del repository.

**Criteri di accettazione:**

- Il piano e il deliverable riportano la release assegnata oppure dichiarano formalmente che non è applicabile.
- Non vengono introdotti file di versione inventati solo per soddisfare il piano.

**Dipendenze:** decisione del Roadmap/owner; attualmente bloccata dall’assenza di roadmap nel repository.
**Owner suggerito:** Roadmap/DevOps o proprietario del corso.

## Validazione prevista

La consegna dovrà essere verificata con controlli eseguibili e circoscritti: sequenza valida completa, validazione negativa su schema non conforme, osservazione del mancato avvio del training dopo il fallimento, verifica del gate sopra e sotto soglia e controllo finale degli artefatti rimasti. I dettagli dei test e della strategia QA restano di competenza dell’agente QA.

## Rischi e mitigazioni

- **Import dipendente dalla directory corrente:** documentare un punto di ingresso stabile e usare invocazioni coerenti con esso.
- **Dipendenza solo procedurale:** introdurre un prerequisito verificabile tra validazione e training.
- **Accuracy instabile tra seed:** mantenere seed esplicito nel comando e dichiarare il limite; non trattare `0.75` come baseline produttiva.
- **Script Bash non nativo su Windows:** fornire comandi Python equivalenti o indicare l’ambiente Bash richiesto.
- **Release non assegnabile:** lasciare il campo TBD finché il responsabile della roadmap non conferma la release, senza inventare una versione.

## Handoff

Il piano è pronto per revisione Critic. Prima dell’implementazione va chiusa la seguente domanda:

**OPEN QUESTION:** quale target release deve essere associata a LAB02? Il repository non contiene una roadmap o un numero di versione. Se il progetto didattico non usa release semver, confermare che `Target Release: N/A` sia accettabile.

**Nota memoria:** le skill `document-lifecycle` e `memory-contract` richieste dalle istruzioni della modalità Planner non erano disponibili in questa sessione; il piano è stato creato senza memoria persistente e con identificativo locale `ID: 1`.
