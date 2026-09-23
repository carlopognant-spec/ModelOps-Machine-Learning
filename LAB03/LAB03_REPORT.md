# LAB03 - API, Docker e strategie di deploy

## Confronto delle strategie

| Opzione | Controllo sui dati | Costo iniziale | Competenze richieste | Tempo di attivazione | Rischio principale nello scenario |
|---|---|---|---|---|---|
| Cloud pubblico | Alto con rete privata, cifratura e policy, ma dipendente dal provider | Basso/medio, consumo a richiesta | Basse/medie; serve configurazione sicurezza e compliance | Ore/giorni | Configurazione errata può esporre dati sanitari |
| On-prem del cliente | Massimo controllo fisico e operativo | Alto, richiede hardware e gestione | Alte; il cliente non ha team infrastrutturale | Settimane/mesi | Budget e competenze insufficienti ritardano il servizio |
| SaaS gestito | Controllo più limitato e dipendenza dal fornitore | Basso/medio, abbonamento | Basse, ma serve verifica di compliance e contratto dati | Ore/giorni | Dati sanitari affidati a policy e certificazioni di terzi |

## Decisione

Scelgo il cloud pubblico con un servizio containerizzato in una rete privata, cifratura in transito e a riposo, logging senza dati sanitari e accesso autenticato. Rispetto all'on-prem riduce il costo iniziale e la necessità di un team infrastrutturale; rispetto a un SaaS generico permette maggiore controllo su regione, retention e configurazione di sicurezza. Prima della produzione servirebbero comunque verifica normativa, gestione segreti e controllo degli accessi.

## Contratto API

### `POST /predict`

Input JSON obbligatorio:

```json
{
  "f1": 1.0,
  "f2": 2.0
}
```

- `f1`: numero reale obbligatorio;
- `f2`: numero reale obbligatorio;
- `f1` e `f2` devono essere finiti: `NaN`, `Infinity` e `-Infinity` restituiscono `422`;
- nessun dato identificativo o sanitario in chiaro deve essere inserito nel payload didattico.

Risposta `200 OK`:

```json
{
  "label": 1,
  "score": 0.834221
}
```

- `label`: intero `0` o `1`;
- `score`: probabilità numerica tra `0` e `1`.

Risposta `422 Unprocessable Entity` per input mancante o non numerico:

```json
{
  "detail": [
    {
      "loc": ["body", "f1"],
      "msg": "Input should be a valid number"
    }
  ]
}
```

## Docker

Contenuto del `Dockerfile` minimale:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service.py pipeline.py data_loader.py ./
COPY model.pkl ./

EXPOSE 8000
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8000"]
```

Comandi previsti:

```powershell
docker build -t lab03-scoring .
docker run --rm -p 8000:8000 lab03-scoring
```

Verifica API locale:

```powershell
Invoke-RestMethod http://localhost:8000/predict -Method Post -ContentType 'application/json' -Body '{"f1":1.0,"f2":2.0}'
```

## Verifica e cleanup

- Verifica API locale: `POST /predict` con payload valido passa; payload non numerico restituisce `422`.
- Verifica API negativa: `NaN` e valori infiniti restituiscono `422` senza errore di serializzazione.
- Docker CLI rilevata, ma `docker build` non è stato eseguito perché il daemon Docker Desktop non era attivo (`dockerDesktopLinuxEngine` non disponibile). È stato usato il fallback locale previsto dalla traccia.
- Verifica manuale del Dockerfile: base image, installazione da `requirements.txt`, copia di codice/dataset/modello, porta `8000` e comando Uvicorn sono presenti e coerenti con il contratto API.
- Nessuna immagine o container di prova è stato creato durante la preparazione.
- Nessun log temporaneo o dataset modificato è stato lasciato.
- `model.pkl` è un artefatto necessario al servizio e resta nel deliverable; non è un file temporaneo.
- Se viene eseguita una build locale, rimuovere con `docker rmi lab03-scoring` e verificare i container con `docker ps -a`.
- Cleanup completato: nessuna immagine, container o file temporaneo rimasto.