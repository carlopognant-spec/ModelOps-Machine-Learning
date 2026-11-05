# LAB11 - Reinforcement learning e confronto preferenze

Studente: [INSERIRE NOME].

Data esecuzione: [INSERIRE DATA].

## Stato

Template creato. Compilare dopo esecuzione reale.

## Comandi principali

```powershell
.\.venv-labs\Scripts\python.exe -m pip install -r .\LAB11\requirements.txt
.\.venv-labs\Scripts\python.exe -m LAB11.rl_frozenlake train --out .\LAB11\output\rl_output --episodes 6000 --seeds 42 43 44
.\.venv-labs\Scripts\python.exe -m LAB11.rl_frozenlake evaluate --run .\LAB11\output\rl_output\seed_42
.\.venv-labs\Scripts\python.exe -m LAB11.reward_ranking
```

## Sezione screenshot (comando + evidenza)

| ID | Comando da lanciare | Cosa deve vedersi | Screenshot |
|---|---|---|---|
| 11-01 | `.\.venv-labs\Scripts\python.exe -m LAB11.rl_frozenlake train --out .\LAB11\output\rl_output --episodes 6000 --seeds 42 43 44` | Confronto random vs q_learning sui seed | [INSERIRE SCREENSHOT 11-01] |
| 11-02 | `Get-Content .\LAB11\output\rl_output\comparison.json` | Success rate per seed e policy | [INSERIRE SCREENSHOT 11-02] |
| 11-03 | `.\.venv-labs\Scripts\python.exe -m LAB11.rl_frozenlake evaluate --run .\LAB11\output\rl_output\seed_42` | Valutazione dopo reload della Q-table | [INSERIRE SCREENSHOT 11-03] |
| 11-04 | `.\.venv-labs\Scripts\python.exe -m LAB11.rl_frozenlake demo --run .\LAB11\output\rl_output\seed_42 --render ansi` | Replay episodio e log in `episode.txt` | [INSERIRE SCREENSHOT 11-04] |
| 11-05 | `.\.venv-labs\Scripts\python.exe -m LAB11.reward_ranking` | JSON preferenze con accordo reward vs riferimento | [INSERIRE SCREENSHOT 11-05] |

## Note da completare

- Differenza tra training con esplorazione e valutazione greedy: [DA COMPILARE]
- Almeno un disaccordo reward/preferenze: [DA COMPILARE]
- Cleanup: [DA COMPILARE]
