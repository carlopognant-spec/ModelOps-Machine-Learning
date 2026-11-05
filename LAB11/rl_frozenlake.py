"""Train, save, reload and observe a tabular Q-learning agent in Gymnasium."""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import gymnasium as gym
import numpy as np

MAP = ["SFFF", "FHFH", "FFFH", "HFFG"]


def make_env(slippery: bool = False, render_mode: str | None = None):
    return gym.make(
        "FrozenLake-v1",
        desc=MAP,
        is_slippery=slippery,
        max_episode_steps=100,
        render_mode=render_mode,
    )


def save_csv(path: Path, rows: list[dict]):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def evaluate(q: np.ndarray, slippery: bool, episodes: int = 200, seed: int = 10000):
    """Same evaluation protocol for random actions and a frozen greedy policy."""
    env = make_env(slippery)
    rows, summary = [], {}
    try:
        for policy in ["random", "q_learning"]:
            rng = np.random.default_rng(seed)
            scores, lengths = [], []
            for episode in range(episodes):
                state, _ = env.reset(seed=seed + episode)
                total, steps = 0.0, 0
                while True:
                    action = int(rng.integers(4)) if policy == "random" else int(np.argmax(q[state]))
                    state, reward, terminated, truncated, _ = env.step(action)
                    total += float(reward)
                    steps += 1
                    if terminated or truncated:
                        break
                scores.append(total)
                lengths.append(steps)
                rows.append(
                    {
                        "policy": policy,
                        "episode": episode,
                        "seed": seed + episode,
                        "return": total,
                        "length": steps,
                        "success": int(total > 0),
                        "terminated": terminated,
                        "truncated": truncated,
                    }
                )
            summary[policy] = {
                "success_rate": float(np.mean(np.asarray(scores) > 0)),
                "mean_return": float(np.mean(scores)),
                "mean_episode_length": float(np.mean(lengths)),
                "episodes": episodes,
            }
    finally:
        env.close()
    return rows, summary


def train_one(folder: Path, seed: int, episodes: int, slippery: bool):
    folder.mkdir(parents=True, exist_ok=False)
    rng = np.random.default_rng(seed)
    env = make_env(slippery)
    q = np.zeros((env.observation_space.n, env.action_space.n), dtype=float)
    alpha, gamma = 0.1, 0.99
    rows = []
    try:
        for episode in range(episodes):
            epsilon = max(0.05, 1 - 0.95 * episode / max(1, 0.7 * episodes))
            state, _ = env.reset(seed=seed + episode)
            total, steps = 0.0, 0
            while True:
                if rng.random() < epsilon:
                    action = int(rng.integers(env.action_space.n))
                else:
                    candidates = np.flatnonzero(q[state] == q[state].max())
                    action = int(rng.choice(candidates))
                next_state, reward, terminated, truncated, _ = env.step(action)
                target = float(reward) + (0.0 if terminated else gamma * float(q[next_state].max()))
                q[state, action] += alpha * (target - q[state, action])
                state = next_state
                total += float(reward)
                steps += 1
                if terminated or truncated:
                    break
            rows.append(
                {
                    "episode": episode,
                    "return": total,
                    "length": steps,
                    "epsilon": epsilon,
                    "success": int(total > 0),
                    "terminated": terminated,
                    "truncated": truncated,
                }
            )
    finally:
        env.close()

    np.save(folder / "q_table.npy", q, allow_pickle=False)
    save_csv(folder / "training.csv", rows)
    evaluation, summary = evaluate(q, slippery)
    save_csv(folder / "evaluation.csv", evaluation)

    config = {
        "environment": "FrozenLake-v1",
        "map": MAP,
        "is_slippery": slippery,
        "max_episode_steps": 100,
        "seed": seed,
        "episodes": episodes,
        "alpha": alpha,
        "gamma": gamma,
        "epsilon_start": 1.0,
        "epsilon_min": 0.05,
        "epsilon_decay_episodes": 0.7 * episodes,
        "gymnasium": gym.__version__,
        "numpy": np.__version__,
        "nonzero_q_values": int(np.count_nonzero(q)),
        "evaluation_seed_start": 10000,
        "evaluation": summary,
    }
    (folder / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")

    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    window = min(100, episodes)
    moving = np.convolve([r["success"] for r in rows], np.ones(window) / window, mode="valid")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(np.arange(window - 1, episodes), moving)
    ax.set(xlabel="Training episode", ylabel=f"Success rate, window {window}", ylim=(0, 1.05))
    ax.set_title(f"Q-learning, seed={seed}, slippery={slippery}")
    fig.tight_layout()
    fig.savefig(folder / "learning_curve.png", dpi=150)
    plt.close(fig)

    return {"seed": seed, "nonzero_q_values": config["nonzero_q_values"], **summary}


def wait_for_window(seconds: float) -> bool:
    import pygame

    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if any(event.type == pygame.QUIT for event in pygame.event.get()):
            return False
        time.sleep(0.02)
    return True


def replay(folder: Path, render_mode: str = "human", delay: float = 0.5):
    if not np.isfinite(delay) or not 0.05 <= delay <= 5:
        raise ValueError("--delay must be between 0.05 and 5 seconds")

    config = json.loads((folder / "config.json").read_text(encoding="utf-8"))
    q = np.load(folder / "q_table.npy", allow_pickle=False)
    if q.shape != (16, 4) or not np.isfinite(q).all():
        raise ValueError("Invalid Q-table")

    env = make_env(config["is_slippery"], render_mode=render_mode)
    text = [f"render_mode={render_mode}, seed=10000, delay={delay}"]
    try:
        state, _ = env.reset(seed=10000)
        text.append(f"initial_state={state}")
        if render_mode == "ansi":
            text.append(env.render())
        else:
            print("Graphical demo: close the window or press Ctrl+C to stop")
        while True:
            if render_mode == "human" and not wait_for_window(delay):
                text.append("Demo interrupted: window closed by user")
                break
            action = int(np.argmax(q[state]))
            state, reward, terminated, truncated, _ = env.step(action)
            text.append(
                f"action={action}, state={state}, reward={reward}, terminated={terminated}, truncated={truncated}"
            )
            if render_mode == "ansi":
                text.append(env.render())
            if terminated or truncated:
                if render_mode == "human":
                    wait_for_window(2.0)
                break
    except KeyboardInterrupt:
        text.append("Demo interrupted with Ctrl+C")
    finally:
        env.close()
        result = "\n".join(text)
        (folder / "episode.txt").write_text(result, encoding="utf-8")
        print(result)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    train_parser = sub.add_parser("train")
    train_parser.add_argument("--out", type=Path, default=Path("rl_output"))
    train_parser.add_argument("--episodes", type=int, default=6000)
    train_parser.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44])
    train_parser.add_argument("--slippery", action="store_true")

    eval_parser = sub.add_parser("evaluate")
    eval_parser.add_argument("--run", type=Path, required=True)

    demo_parser = sub.add_parser("demo")
    demo_parser.add_argument("--run", type=Path, required=True)
    demo_parser.add_argument("--render", choices=["human", "ansi"], default="human")
    demo_parser.add_argument("--delay", type=float, default=0.5)

    args = parser.parse_args()
    if args.command == "train":
        if args.episodes < 1 or len(set(args.seeds)) != len(args.seeds):
            raise ValueError("Use positive episodes and unique seeds")
        args.out.mkdir(parents=True, exist_ok=False)
        results = [train_one(args.out / f"seed_{seed}", seed, args.episodes, args.slippery) for seed in args.seeds]
        (args.out / "comparison.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(json.dumps(results, indent=2))
    elif args.command == "evaluate":
        config = json.loads((args.run / "config.json").read_text(encoding="utf-8"))
        q = np.load(args.run / "q_table.npy", allow_pickle=False)
        rows, summary = evaluate(q, config["is_slippery"])
        save_csv(args.run / "evaluation_reloaded.csv", rows)
        (args.run / "evaluation_reloaded.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, indent=2))
    else:
        replay(args.run, args.render, args.delay)


if __name__ == "__main__":
    main()
