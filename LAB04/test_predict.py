"""Client HTTP manuale: server gia avviato, nessun training implicito."""
import argparse
import json
from pathlib import Path

import httpx

FEATURES = [13.2, 1.78, 2.14, 11.2, 100.0, 2.65, 2.76, 0.26, 1.28, 4.38, 1.05, 3.4, 1050.0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    registry = json.loads((Path(__file__).resolve().parent / "registry.json").read_text(encoding="utf-8"))
    cases = [("valida", {"features": FEATURES}, 200), ("campo mancante", {}, 422),
             ("non numerica", {"features": ["abc"] + FEATURES[1:]}, 422),
             ("numero stringa", {"features": ["13.2"] + FEATURES[1:]}, 422),
             ("lunghezza errata", {"features": [1.0]}, 422),
             ("booleano", {"features": [True] + FEATURES[1:]}, 422)]
    with httpx.Client(timeout=10) as client:
        for name, payload, expected in cases:
            response = client.post(args.url + "/predict", json=payload)
            print(f"{name}: HTTP {response.status_code} {response.text}")
            assert response.status_code == expected, name
            if expected == 200:
                assert response.json()["model_version"] == registry["active_version"]
            else:
                assert "prediction" not in response.json()
        for token in ("NaN", "Infinity", "-Infinity"):
            body = '{"features":[' + token + ',' + ','.join(map(str, FEATURES[1:])) + ']}'
            response = client.post(args.url + "/predict", content=body, headers={"Content-Type": "application/json"})
            print(f"{token}: HTTP {response.status_code} {response.text}")
            assert response.status_code == 422
            assert "prediction" not in response.json()
    print("PASS: richieste e versione verificate in questa esecuzione")


if __name__ == "__main__":
    main()
