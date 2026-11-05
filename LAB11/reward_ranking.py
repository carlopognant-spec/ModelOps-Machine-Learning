"""Compare simple reward scores with simulated preferences."""
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Answer:
    text: str
    correctness: float
    bad_tone: bool = False


def reward(answer: Answer) -> float:
    return answer.correctness - 0.01 * len(answer.text.split()) - 0.5 * float(answer.bad_tone)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path(__file__).resolve().parent / "data" / "11_dataset_preferenze_simulate.csv")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "output" / "preference_comparison.json")
    args = parser.parse_args()

    with args.data.open(newline="", encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    if not records:
        raise ValueError("Empty preferences CSV")

    pairs: dict[str, dict[str, dict[str, str]]] = {}
    for record in records:
        pair = pairs.setdefault(record["pair_id"], {})
        if record["response_id"] in pair:
            raise ValueError("Duplicated response in pair")
        if not 0 <= float(record["correctness"]) <= 1:
            raise ValueError("Correctness must be in [0,1]")
        if record["bad_tone"] not in {"0", "1"}:
            raise ValueError("bad_tone must be 0/1")
        pair[record["response_id"]] = record

    rows = []
    for pair_id, pair in pairs.items():
        if set(pair) != {"A", "B"}:
            raise ValueError("Each pair must contain A and B")
        row_a, row_b = pair["A"], pair["B"]
        if row_a["question"] != row_b["question"]:
            raise ValueError("Question mismatch inside pair")

        a = Answer(row_a["text"], float(row_a["correctness"]), row_a["bad_tone"] == "1")
        b = Answer(row_b["text"], float(row_b["correctness"]), row_b["bad_tone"] == "1")
        reward_a, reward_b = reward(a), reward(b)
        chosen = "A" if reward_a > reward_b else ("B" if reward_b > reward_a else "pari")

        rows.append(
            {
                "pair": pair_id,
                "question": row_a["question"],
                "reward_A": reward_a,
                "reward_B": reward_b,
                "reward_choice": chosen,
                "human_choice_simulated": row_a["preferred_reference"],
                "reason": row_a["reason_reference"],
                "agreement": chosen == row_a["preferred_reference"],
            }
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(rows, indent=2, ensure_ascii=False))
    print(f"Accordo: {sum(r['agreement'] for r in rows)} / {len(rows)}")


if __name__ == "__main__":
    main()
