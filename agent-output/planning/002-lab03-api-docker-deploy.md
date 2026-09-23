---
ID: 2
Origin: 2
UUID: 7a4d2e91
Status: In Progress
---

# Piano: LAB03 API, Docker e strategie di deploy

**Target Release:** TBD/N/A: il repository non contiene roadmap, versione applicativa o release artifact.
**Epic Alignment:** Lab 03 - API Docker e strategie di deploy
**Status:** In Progress

## Changelog

| Date | Handoff | Request | Summary |
|---|---|---|---|
| 2026-09-23 | Planner -> Implementer | Eseguire il piano | Target release confermato come `N/A`; verifica e completamento di LAB03 avviati. |

## Value Statement and Business Objective

Come studente, voglio trasformare il modello validato in LAB02 in un servizio API containerizzabile e scegliere una strategia di deploy motivata, così da dimostrare come esporre uno scoring ML rispettando vincoli di dati sensibili, budget e competenze infrastrutturali limitate.

## Contesto e stato rilevato

La cartella `LAB03` è già presente nel workspace come materiale predisposto prima della formalizzazione di questo piano. Contiene:

- `service.py` con endpoint `GET /health` e `POST /predict` basati su FastAPI;
- `pipeline.py`, `data_loader.py`, `csv/data.csv` e `model.pkl` riutilizzati da LAB02;
- `requirements.txt`, `Dockerfile` e `.dockerignore`;
- `tests/test_service.py`;
- `LAB03_REPORT.md` con confronto cloud/on-prem/SaaS, decisione cloud pubblico, contratto API, Docker e cleanup.

Verifiche già disponibili nel materiale:

- suite locale: `2 passed`;
- validazione manuale del Dockerfile: base image, dipendenze, artefatto, porta e comando presenti;
- Docker CLI presente, ma Docker Desktop non era attivo e la build non è stata eseguita;
- nessuna immagine o container di prova lasciato;
- `model.pkl` mantenuto come artefatto runtime necessario.

## Obiettivo del piano

Portare il deliverable LAB03 a una consegna verificabile rispetto alla traccia, preservando il riuso del modello LAB02 e rendendo espliciti i limiti del fallback locale quando Docker non è disponibile.

## Assunzioni e vincoli

- Il modello didattico di LAB02 e il dataset sintetico restano la base del servizio.
- Il payload usa solo `f1` e `f2`; non devono essere introdotti dati sanitari o identificativi reali.
- La scelta cloud pubblico è didattica e non equivale ad approvazione per dati sanitari reali.
- La containerizzazione deve rimanere minimale: FastAPI, Uvicorn, dipendenze bloccate e artefatto modello.
- L’assenza del daemon Docker è gestita con verifica manuale e test locali, come previsto dal fallback della traccia.
- Non esiste una roadmap di release nel repository; non va inventato un numero di versione.

## Milestones

### 1. Formalizzare il riuso del modello LAB02

**Obiettivo:** rendere tracciabile quali file sono necessari per eseguire lo scoring.

**Attività:**

1. Confermare che preprocessing, pesi, riferimenti di standardizzazione e metrica provengano dallo stesso modello addestrato.
2. Mantenere separato il codice di servizio dal codice di training, evitando training a ogni richiesta.
3. Documentare `model.pkl` come artefatto runtime e non come file temporaneo.

**Criteri di accettazione:**

- Il servizio può caricare l’artefatto senza modificare LAB02.
- Il payload viene trasformato con gli stessi riferimenti usati durante il training.
- Il report elenca chiaramente file importati e file specifici di LAB03.

**Dipendenze:** nessuna.
**Owner suggerito:** Implementer.

### 2. Consolidare il contratto API

**Obiettivo:** definire un’interfaccia prevedibile per input valido, input non valido e disponibilità del modello.

**Attività:**

1. Mantenere `/predict` con schema numerico obbligatorio per `f1` e `f2`.
2. Esplicitare risposta di successo con `label` binaria e `score` numerico.
3. Distinguere errori di validazione richiesta da errori dell’artefatto runtime.
4. Mantenere `/health` come controllo di disponibilità del processo.

**Criteri di accettazione:**

- Il report contiene payload e risposte JSON coerenti con l’implementazione.
- Input mancante o non numerico produce un errore 4xx comprensibile.
- Un modello assente o invalido non viene trattato come predizione valida.

**Dipendenze:** milestone 1.
**Owner suggerito:** Implementer.

### 3. Consolidare Dockerfile e deploy scelto

**Obiettivo:** produrre un’immagine minimale coerente con il servizio e con la decisione cloud pubblico.

**Attività:**

1. Mantenere una base Python slim, dipendenze pinned, working directory, copia dei file necessari, porta e comando Uvicorn.
2. Evitare di includere cache, test e log nel build context tramite `.dockerignore`.
3. Documentare configurazioni di sicurezza richieste per un deploy reale: rete privata, cifratura, autenticazione, gestione segreti, logging senza dati sensibili e regione di deployment.
4. Distinguere la validazione sintattica/manuale dalla build effettivamente eseguita con Docker.

**Criteri di accettazione:**

- Il Dockerfile contiene tutti gli elementi richiesti dalla traccia e nessun elemento superfluo rilevante.
- Il comando di avvio espone il servizio sulla porta documentata.
- Il report dichiara chiaramente se la build non è stata eseguita per assenza del daemon.

**Dipendenze:** milestone 2.
**Owner suggerito:** Implementer.

### 4. Chiudere evidenze e cleanup

**Obiettivo:** consegnare una prova riproducibile senza artefatti temporanei o ambiguità operative.

**Attività:**

1. Conservare nel report la tabella cloud/on-prem/SaaS con controllo dati, costi, competenze, tempi e rischio specifico.
2. Conservare la motivazione della scelta cloud rispetto a budget e assenza di team infrastrutturale.
3. Registrare test locali, stato Docker, immagini/container eventualmente rimossi e file mantenuti come deliverable.
4. Chiudere cache, log e output di prova non necessari.

**Criteri di accettazione:**

- Il report copre tutti gli output attesi e i checkpoint della traccia.
- Non restano immagini Docker o container di prova non necessari.
- Il dataset e il modello consegnati sono identificati come artefatti intenzionali.

**Dipendenze:** milestone 3.
**Owner suggerito:** Implementer, con verifica del proprietario della consegna.

### 5. Aggiornare gli artefatti di release

**Obiettivo:** allineare il deliverable al sistema di versionamento del repository senza inventare release.

**Attività:**

1. Verificare con il responsabile della roadmap se LAB03 appartiene a una release specifica.
2. Se il progetto didattico non usa release semver, registrare `Target Release: N/A` nel piano e nel passaggio di consegna.
3. Se viene assegnata una release, aggiornare solo gli artefatti di versione previsti dalle convenzioni del repository.

**Criteri di accettazione:**

- Il piano riporta una release confermata oppure una motivazione esplicita per `N/A`.
- Non vengono creati package version o changelog artificiali.

**Dipendenze:** decisione del responsabile roadmap/owner.
**Owner suggerito:** Roadmap/DevOps.

## Validazione prevista

La verifica dovrà coprire comportamento API valido e non valido, coerenza tra modello e preprocessing, correttezza del Dockerfile, disponibilità della porta e cleanup. Se Docker Desktop non è disponibile, la consegna dovrà usare la validazione manuale dichiarata nel report e non presentarla come una build riuscita.

## Rischi e mitigazioni

- **Dati sensibili:** usare dati sintetici, rete privata, cifratura e logging minimizzato; completare una revisione normativa prima della produzione.
- **Artefatto modello non valido:** controllare presenza e struttura prima dello scoring e restituire errore controllato.
- **Dipendenza da Docker Desktop:** mantenere un fallback locale documentato e ripetibile.
- **Immagine troppo permissiva:** mantenere base slim, dipendenze pinned e contesto Docker ridotto.
- **Drift tra LAB02 e LAB03:** documentare i file copiati e la provenienza del modello.

## Handoff

Il piano è pronto per revisione Critic. L’implementazione esistente in `LAB03` deve essere considerata materiale da verificare rispetto a questo piano, non automaticamente approvata.

**Decisione release:** `Target Release: N/A`, perché il progetto didattico non usa release applicative.

**Nota memoria:** le skill `document-lifecycle` e `memory-contract` richieste dalla modalità Planner non erano disponibili nella sessione; il piano è stato creato con identificativo locale `ID: 2`.