"""Visualizza eventi reali salvati; non inventa timestamp alla lettura."""
import json
from pathlib import Path


def main():
    path = Path(__file__).resolve().parent / "rollback_events.jsonl"
    if not path.exists():
        raise SystemExit("Log assente: eseguire prima evaluate.py e rollback_versions.py")
    for line in path.read_text(encoding="utf-8").splitlines():
        print(json.dumps(json.loads(line), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
