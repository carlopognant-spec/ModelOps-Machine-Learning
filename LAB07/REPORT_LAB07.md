# LAB07 — Laboratorio Monitoring e Explainability SHAP/LIME

Studente: Carlo Pognant.

Modulo: ModelOps e Machine Learning — ITS ICT Piemonte, Gen AI Specialist.

Data e ora dell'esecuzione: [INSERIRE DATA E ORA DEL TEST].

Ambiente Python / dipendenze effettive: [DA COMPILARE DOPO ESECUZIONE].

## Stato della relazione

**Codice predisposto, esecuzione ancora da svolgere.** Tutte le verifiche e il cleanup sono [DA COMPILARE DOPO ESECUZIONE]. Le sezioni descrivono il metodo implementato, non un'attivita gia verificata. Dopo l'esecuzione indicare separatamente comportamento previsto, risultato osservato ed eventuale fallback.

## Scenario e obiettivo

La simulazione di credito del LAB06 ha un batch con accuracy sotto una soglia calibrata sullo storico. Prima di proporre un rollback si isolano casi e si spiegano le predizioni del modello condiviso. Se nessun batch ha accuracy sotto soglia il programma si ferma senza inventare il segnale.

## Struttura del progetto

explain_case.py, tests/test_explanations.py, requirements.txt. Dipende da tutti i dati LAB06/data e LAB06/output/monitoring.json. Generati in output/: cases.json, comparison.json, summary.md, shap_waterfall.png, lime.png e lime.html.

## Ricostruzione e differenze

Laboratorio nuovo. Si usa credito sintetico coerente col LAB06; il dataset medico del riferimento tecnico non viene rinominato credito. Si richiedono entrambi SHAP e LIME sullo stesso caso e sulla stessa classe.

## Passaggi e comandi da eseguire

Directory: root della repository. Seguire gli step LAB07 della [guida manuale](../GUIDA_ESECUZIONE_LAB04-07.md), inclusi setup e gestione terminali. Non incollare tutti i comandi insieme se e previsto un server in primo piano.

```powershell
.\.venv-labs\Scripts\python.exe -m LAB07.explain_case
.\.venv-labs\Scripts\python.exe -m pytest .\LAB07\tests -q
```

## Metriche ed evidenze osservate

| Segnale monitoring | Batch | Caso | Feature SHAP | Feature LIME | Interpretazione | Azione |
|---|---|---|---|---|---|---|
| [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |

Output effettivo: [INSERIRE OUTPUT DEL TERMINALE].

Esito dei test eseguiti manualmente: [DA COMPILARE DOPO ESECUZIONE].

## Segnale e casi selezionati

Prerequisiti manuali: LAB06.simulate e LAB06.monitor, nell'ordine. L'analisi verifica manifest/hash, modello/versione, predizioni e accuracy del batch. Preferisce un batch con accuracy sotto soglia e alert PSI persistente; se non esiste questa combinazione sceglie un batch realmente sotto soglia accuracy e riporta lo stato PSI effettivo.

Timestamp, batch, metrica, valore, soglia e motivo: [DA COMPILARE DOPO ESECUZIONE].

| Caso | Input completo | Predetto | Classe reale simulata | Confidenza | Motivo / errore o sospetto |
|---|---|---|---|---|---|
| [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |
| [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |
| [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] | [DA COMPILARE DOPO ESECUZIONE] |

Gli errori sono ordinati per confidenza decrescente; se non bastano si aggiungono casi corretti a bassa confidenza, esplicitamente indicati come sospetti. Si spiegano localmente il primo caso e la sua classe predetta. Classe 1 = credito approvato nella sola simulazione.

## SHAP e LIME

TreeExplainer con tree_path_dependent usa la distribuzione di training registrata negli alberi. Il normalizzatore supporta lista per classe e array (1,feature,classi); formati sconosciuti interrompono il programma. Base + contributi deve ricostruire la probabilita della classe predetta prima del salvataggio del waterfall.

LIME usa lo stesso caso/classe, training originale come riferimento, random_state=42 e 5000 perturbazioni. Conserva regole con pesi, HTML, PNG e R2 della regressione locale. Il ranking viene confrontato tramite indici reali delle feature; un disaccordo viene riportato senza modifiche. I pesi dei due metodi non hanno necessariamente la stessa interpretazione.

Classe e probabilita spiegate: [DA COMPILARE DOPO ESECUZIONE].
Top SHAP, segno e contributo: [DA COMPILARE DOPO ESECUZIONE].
Top LIME, peso e R2 locale: [DA COMPILARE DOPO ESECUZIONE].
Concordanza/differenza osservata e implicazioni: [DA COMPILARE DOPO ESECUZIONE].

## Collegamento con il drift

comparison.json riporta PSI, soglia e superamento delle feature principali SHAP/LIME nello stesso batch. Una feature influente puo non mostrare drift. Anche se entrambe le condizioni sono osservate, si tratta di associazione. Nel generatore cambiano anche le etichette tramite policy, quindi la causalita del solo drift dell'eta non e dimostrata.

Associazione effettivamente osservata: [DA COMPILARE DOPO ESECUZIONE].
Possibile causa da verificare: [DA COMPILARE DOPO ESECUZIONE].
Causalita dimostrata: NO, non dimostrata da questa analisi.

## Nota di impatto business

Usare output/summary.md come base generata dai risultati effettivi e rileggerla. Descrivere batch degradato, casi analizzati e feature da controllare: [DA COMPILARE DOPO ESECUZIONE]. Rischio simulato: approvazioni/rifiuti errati. Destinatari: responsabile rischio credito, responsabile dati e Data Scientist on-call. Azione proposta: audit di feature, policy ed etichette e valutazione per sottogruppi. Prima di rollback/retraining confrontare una baseline sugli stessi batch, verificare la disponibilita delle etichette, validare il rimedio e stabilire criteri di rilascio. Nessuna comunicazione esterna o decisione reale eseguita.

## Fallback

Dataset ridotto a quattro feature e spiegazione di una sola riga per contenere i tempi, grafici/HTML locali al posto di servizi cloud. Se import/calcolo SHAP/LIME fallisce, segnale e casi possono essere conservati ma la spiegazione resta NON COMPLETATA. Ripristinare l'ambiente dai requirements e rieseguire manualmente; non sostituire con valori inventati.

## Screenshot da inserire

- [INSERIRE SCREENSHOT 07-01 segnale]
- [INSERIRE SCREENSHOT 07-02 casi]
- [INSERIRE SCREENSHOT 07-03 contributi SHAP]
- [INSERIRE SCREENSHOT 07-04 waterfall]
- [INSERIRE SCREENSHOT 07-05 pesi e grafico LIME]
- [INSERIRE SCREENSHOT 07-06 confronto/nota business]
- [INSERIRE SCREENSHOT 07-07 cleanup]

Consultare [PIANO_SCREENSHOT.md](../PIANO_SCREENSHOT.md) per comandi e didascalie.

## Limiti

SHAP descrive il comportamento del modello, non la verita delle etichette o una causa del danno. LIME approssima localmente e dipende dalle perturbazioni; un R2 basso limita la fedelta. Singolo caso spiegato, tre casi selezionati e dati sintetici non dimostrano un comportamento generale o equita. Politica etichette e eta cambiano insieme.

## Cleanup

Gli script terminano senza server o kernel. Chiudere immagini/browser; conservare waterfall, LIME PNG/HTML finali, cases/comparison/summary e dati LAB06 necessari alla riproducibilita. Rimuovere soltanto copie temporanee dopo backup e screenshot. Nessuna dashboard remota o regola esterna creata.

Stato effettivo: [DA COMPILARE DOPO ESECUZIONE].

Risorse fermate/rimosse: [DA COMPILARE DOPO ESECUZIONE].

File conservati e motivazione: [DA COMPILARE DOPO ESECUZIONE].

## Checkpoint della traccia

- [ ] Segnale numerico effettivo del LAB06 confermato.
- [ ] Batch, modello e input dei casi identificabili.
- [ ] Errori distinti da predizioni soltanto sospette.
- [ ] SHAP waterfall per classe corretta con verifica probabilita.
- [ ] LIME sullo stesso caso e classe, pesi e fedelta consultati.
- [ ] Confronto e eventuale disaccordo riportati.
- [ ] PSI delle feature influenti confrontato senza deduzioni causali.
- [ ] Nota business comprensibile con destinatari e verifiche proposte.
- [ ] Limiti, fallback e cleanup documentati.

Spuntare soltanto dopo osservazione effettiva. Se un passaggio non e stato svolto scrivere NON VERIFICATO e il motivo.
