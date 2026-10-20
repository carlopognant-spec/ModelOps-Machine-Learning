# Analisi iniziale e scelte di ricostruzione

Data dell'ispezione: 21 ottobre 2026. Studente: Carlo Pognant.

## Workspace e Git

Root: `C:\Users\carlo\Desktop\ModelOps-Machine-Learning`.
Prima delle modifiche: `git status --short --branch` restituisce solo
`## main...origin/main`, senza modifiche locali segnalate da Git.
HEAD locale: `7635f56`. Remote origin: repository personale indicato nella richiesta.
Non e stato effettuato pull: lo stato rispetto al server non e stato dedotto dal solo tracking locale.
I buffer non salvati dell'editor non sono accessibili all'ispezione del filesystem.
Nessun commit o push effettuato.

Struttura esaminata:

- LAB01: data_loader.py, train.py, CSV/data.csv, LAB01_REPORT.md; regressione logistica in Python standard.
- LAB02: data_loader.py, pipeline.py, run_pipeline.sh, csv/data.csv, tests (conftest, test_data, test_pipeline), LAB02_REPORT.md.
- LAB03: data_loader.py, pipeline.py, service.py, requirements.txt, Dockerfile, .dockerignore, model.pkl, csv/data.csv, tests/test_service.py, LAB03_REPORT.md.
- Root: README.md, .gitignore; .github/agents con profili; agent-output con resoconti precedenti.
- LAB04 e LAB05 assenti prima dell'intervento; anche LAB06 e LAB07 assenti.
- Nessun AGENTS.md rilevato nella struttura o nei percorsi antenati controllati.

LAB01–03 e i precedenti resoconti non sono stati modificati.
Si mantengono nomi LABnn, commenti e documentazione in italiano,
entrypoint main e percorsi basati su pathlib. I nuovi modelli richiedono scikit-learn,
mentre LAB01–02 usavano una implementazione con libreria standard.
LAB03 usa FastAPI 0.115.6 e Pydantic 2.10.4: le stesse versioni sono fissate in LAB04.

## Verifica del materiale ufficiale

Repository: [GAS-ModelOps-ML](https://github.com/its-javadizavieh/GAS-ModelOps-ML).
Albero remoto letto integralmente, non troncato, alla revisione
`3c173bcab9466897cf9b5910c11abe831c654e98`.
Letti README, tracce LAB04–07 e soluzioni corrispondenti in lab_solutions/.
Sono presenti file traccia e soluzione da 01 a 07. Non esistono file LAB08–15
in quell'albero, anche se il README li elenca: non sono stati inventati altri esercizi.
L'elenco puo cambiare in futuro; questa e una verifica della revisione indicata.

Le tracce sono i requisiti; le soluzioni hanno fornito i parametri di ricostruzione.
Non vengono trasferiti nei nuovi report gli output dichiarati verificati dal professore.

| Traccia | Requisiti coperti dai file predisposti | Verifica dello studente |
|---|---|---|
| [04](https://github.com/its-javadizavieh/GAS-ModelOps-ML/blob/3c173bcab9466897cf9b5910c11abe831c654e98/labs/04_serving_fastapi_docker_e_model_registry.md) | Due modelli, registry e gate, endpoint con versione, client, Docker/fallback, cleanup | [DA COMPILARE DOPO ESECUZIONE] |
| [05](https://github.com/its-javadizavieh/GAS-ModelOps-ML/blob/3c173bcab9466897cf9b5910c11abe831c654e98/labs/05_versioning_rollback_e_prime_metriche.md) | Accuracy e latenza, rilascio v2 simulato, decisione, ripristino e ricaricamento, log | [DA COMPILARE DOPO ESECUZIONE] |
| [06](https://github.com/its-javadizavieh/GAS-ModelOps-ML/blob/3c173bcab9466897cf9b5910c11abe831c654e98/labs/06_monitoring_logging_drift_e_notifiche.md) | PSI, calibrazione storica, persistenza, tabella/grafico, notifica simulata, cleanup | [DA COMPILARE DOPO ESECUZIONE] |
| [07](https://github.com/its-javadizavieh/GAS-ModelOps-ML/blob/3c173bcab9466897cf9b5910c11abe831c654e98/labs/07_laboratorio_monitoring_e_explainability_shap_lime.md) | Segnale di accuracy LAB06, casi, SHAP e LIME, confronto, PSI delle feature, nota business | [DA COMPILARE DOPO ESECUZIONE] |

## Differenze motivate

- LAB04: mantenuti wine, rumore RandomState(0) con deviazione 2, split 0.3 stratificato seed 42, RandomForest 200 alberi e 1 albero depth 1. Accuracy senza arrotondamenti prima del gate. La baseline deve superare 0.85; in caso contrario lo script si ferma. Se v3 supera realmente la soglia diventa attiva: nessun rifiuto imposto.
- LAB04: il servizio legge il registry e verifica hash, versione e schema dell'artefatto; il riferimento caricava v2 con costante. Il server va riavviato dopo ogni cambio di registry/modello.
- LAB05: mantenuti breast_cancer (dichiarato medico), split 0.3 stratificato seed 42, LogisticRegression(max_iter=5000) non scalata e DecisionTree(max_depth=1). Possibili warning di convergenza vanno conservati e discussi, non nascosti. Nessuna ricerca di parametri per replicare i numeri storici.
- LAB05: il riferimento chiamava rollback anche il blocco della candidata. Qui v2 viene davvero attivata nel registry locale prima del gate; solo il successivo cambio a v1 e un rollback simulato. Nessun servizio di produzione viene modificato. Il tempo di fix non e misurato: il fix e considerato non validato nel timebox.
- LAB06–07: dati di credito esclusivamente sintetici, modello e batch condivisi, niente dataset medico rinominato credito. Nei batch alterati cambiano eta e policy delle etichette: il solo PSI non dimostra una causa del calo di accuracy.
- Soglia PSI: q99 dei 30 batch storici normali x 1.25, floor numerico 1e-6. Non e fissata a 0.08 e non viene scelta osservando i batch recenti. Soglia accuracy: q05 storico meno 0.02. Sono regole didattiche da validare, non garanzie statistiche su dati reali.

## Ambiente e stato delle verifiche

`py -0p` ha rilevato Python 3.11 e 3.14; Python 3.12 non rilevato.
Usare 3.12 se installato, oppure il 3.11 disponibile. Non usare il 3.14 predefinito
con le versioni fissate. Docker usa Python 3.11 per allinearsi all'alternativa locale.
Le dipendenze scelte non costituiscono un lock completo delle transitive.

Riferimenti tecnici: [scikit-learn 1.5.2](https://pypi.org/project/scikit-learn/1.5.2/),
[SHAP 0.46.0](https://pypi.org/project/shap/0.46.0/),
[TreeExplainer](https://shap.readthedocs.io/en/stable/generated/shap.TreeExplainer.html),
[Numba 0.60.0](https://pypi.org/project/numba/0.60.0/).

Consentiti soltanto lettura, scrittura dei sorgenti e controllo statico.
Training, server, Docker, pipeline, test, benchmark, SHAP/LIME, installazioni e cleanup
non eseguiti durante la preparazione. Nessuna nuova metrica e stata ottenuta.

Controlli statici effettuati sui nuovi file: parsing AST di 20 file Python
con grammatica Python 3.11, risoluzione di 12 import locali e controllo di 11
link Markdown locali. Nessun problema rilevato in questi controlli.
`git diff --check` non ha segnalato errori di whitespace; Git segnala soltanto
la normale conversione LF/CRLF del README su questo checkout Windows.
Questi controlli non verificano l'importazione delle librerie, l'installazione,
la correttezza sperimentale o il funzionamento end-to-end.
