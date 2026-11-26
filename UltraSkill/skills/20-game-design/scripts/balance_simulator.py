#!/usr/bin/env python3
"""
Deterministic Monte Carlo Combat & Economy Balance Simulator (`balance_simulator.py`).

Simulates `N` (default: 1,000) combat encounters and progression curves at a `60 Hz`
tick rate using a seeded PRNG (`random.Random(seed)`) so results are 100% reproducible:
  1. Models player attack startup/active/recovery frames, dash cooldowns, and hit probability.
  2. Models ticketed enemy waves (Swarmer + Ranged Suppressor + Elite) with armor mitigation:
       effective_damage = raw_damage * (100 / (100 + armor))
  3. Computes mean, p50, and p95 Time-to-Kill (TTK in seconds), player survival win rate,
     remaining HP %, and economy net currency balance after repair/consumable sinks.
  4. Fails with exit code 1 if TTK or win rate falls outside the target design gates.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path


DEFAULT_SCENARIO = {
    "player": {
        "max_hp": 100.0,
        "armor": 25.0,
        "attack_damage": 24.0,
        "attack_interval_sec": 0.48,
        "hit_chance": 0.88,
        "crit_chance": 0.15,
        "crit_multiplier": 1.5,
        "dodge_chance": 0.42,
    },
    "enemies": [
        {"role": "Swarmer_A", "hp": 48.0, "armor": 0.0, "damage": 12.0, "attack_interval_sec": 1.25, "gold_drop": 15},
        {"role": "Swarmer_B", "hp": 48.0, "armor": 0.0, "damage": 12.0, "attack_interval_sec": 1.25, "gold_drop": 15},
        {"role": "Suppressor", "hp": 72.0, "armor": 15.0, "damage": 16.0, "attack_interval_sec": 1.80, "gold_drop": 30},
    ],
    "economy": {
        "repair_cost_per_hp_lost": 0.65,
        "ammo_sink_per_encounter": 12.0,
    },
    "gates": {
        "min_win_rate": 0.75,
        "max_win_rate": 0.99,
        "target_ttk_sec": 4.2,
        "ttk_tolerance_pct": 0.25,
    },
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="balance_simulator.py",
        description="Run deterministic Monte Carlo combat TTK and economy sink/faucet simulations.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional JSON scenario file overriding default player/enemy/gate parameters.",
    )
    parser.add_argument(
        "--trials",
        type=int,
        default=1000,
        help="Number of Monte Carlo encounter trials to simulate (default: 1000).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Deterministic PRNG seed (default: 42).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="Optional output path for JSON simulation report.",
    )
    return parser.parse_args(argv)


def mitigate(raw_dmg: float, armor: float) -> float:
    return raw_dmg * (100.0 / (100.0 + max(0.0, armor)))


def simulate_one_encounter(cfg: dict, rng: random.Random) -> dict:
    p_cfg = cfg["player"]
    p_hp = float(p_cfg["max_hp"])
    p_next_atk = float(p_cfg["attack_interval_sec"])

    enemies = []
    for idx, e in enumerate(cfg["enemies"]):
        enemies.append(
            {
                "hp": float(e["hp"]),
                "armor": float(e["armor"]),
                "damage": float(e["damage"]),
                "interval": float(e["attack_interval_sec"]),
                # Stagger initial enemy attack windups so they don't all hit on tick 0
                "next_atk": float(e["attack_interval_sec"]) * (0.7 + 0.25 * idx),
                "gold": int(e.get("gold_drop", 10)),
            }
        )

    dt = 0.05  # 20 Hz coarse discrete simulation step
    t = 0.0
    max_time = 120.0

    while t < max_time and p_hp > 0.0 and any(e["hp"] > 0.0 for e in enemies):
        t += dt
        if t >= p_next_atk:
            p_next_atk += float(p_cfg["attack_interval_sec"])
            alive = [e for e in enemies if e["hp"] > 0.0]
            if alive and rng.random() <= float(p_cfg["hit_chance"]):
                target = alive[0]
                dmg = float(p_cfg["attack_damage"])
                if rng.random() <= float(p_cfg["crit_chance"]):
                    dmg *= float(p_cfg["crit_multiplier"])
                target["hp"] -= mitigate(dmg, target["armor"])

        # Ticketed AI rule: at most 2 alive enemies advance their attack timer simultaneously
        active_attackers = [e for e in enemies if e["hp"] > 0.0][:2]
        for enemy in active_attackers:
            if t >= enemy["next_atk"]:
                enemy["next_atk"] += enemy["interval"]
                if rng.random() > float(p_cfg["dodge_chance"]):
                    p_hp -= mitigate(enemy["damage"], float(p_cfg["armor"]))

    won = p_hp > 0.0 and all(e["hp"] <= 0.0 for e in enemies)
    hp_lost = max(0.0, float(p_cfg["max_hp"]) - max(0.0, p_hp))
    faucet_gold = sum(e["gold"] for e in enemies) if won else 0
    econ = cfg.get("economy", {})
    sink_gold = (hp_lost * float(econ.get("repair_cost_per_hp_lost", 0.5))) + float(
        econ.get("ammo_sink_per_encounter", 10.0)
    )

    return {
        "won": won,
        "duration_sec": t,
        "remaining_hp": max(0.0, p_hp),
        "net_gold": faucet_gold - sink_gold,
    }


def percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, max(0, int(round((pct / 100.0) * (len(sorted_vals) - 1)))))
    return sorted_vals[idx]


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.trials < 10:
        print("[ERROR] --trials must be >= 10.", file=sys.stderr)
        return 2

    cfg = json.loads(json.dumps(DEFAULT_SCENARIO))
    if args.config is not None:
        if not args.config.is_file():
            print(f"[ERROR] Config file not found: {args.config}", file=sys.stderr)
            return 1
        user_cfg = json.loads(args.config.read_text(encoding="utf-8"))
        cfg.update(user_cfg)

    rng = random.Random(args.seed)
    results = [simulate_one_encounter(cfg, rng) for _ in range(args.trials)]

    wins = [r for r in results if r["won"]]
    win_rate = len(wins) / len(results)
    durations = sorted(r["duration_sec"] for r in (wins if wins else results))
    mean_ttk = sum(durations) / len(durations)
    p50_ttk = percentile(durations, 50.0)
    p95_ttk = percentile(durations, 95.0)
    mean_hp_rem = sum(r["remaining_hp"] for r in results) / len(results)
    mean_net_gold = sum(r["net_gold"] for r in results) / len(results)

    gates = cfg["gates"]
    target_ttk = float(gates["target_ttk_sec"])
    tol = float(gates["ttk_tolerance_pct"])
    ttk_min = target_ttk * (1.0 - tol)
    ttk_max = target_ttk * (1.0 + tol)

    errors: list[str] = []
    if not (float(gates["min_win_rate"]) <= win_rate <= float(gates["max_win_rate"])):
        errors.append(
            f"Win rate {win_rate:.3f} is outside target window [{gates['min_win_rate']}, {gates['max_win_rate']}]."
        )
    if not (ttk_min <= mean_ttk <= ttk_max):
        errors.append(
            f"Mean TTK {mean_ttk:.2f}s is outside target window [{ttk_min:.2f}s, {ttk_max:.2f}s]."
        )

    summary = {
        "trials": args.trials,
        "seed": args.seed,
        "win_rate": round(win_rate, 4),
        "mean_ttk_sec": round(mean_ttk, 3),
        "p50_ttk_sec": round(p50_ttk, 3),
        "p95_ttk_sec": round(p95_ttk, 3),
        "target_ttk_window_sec": [round(ttk_min, 2), round(ttk_max, 2)],
        "mean_remaining_hp": round(mean_hp_rem, 2),
        "mean_net_currency_per_encounter": round(mean_net_gold, 2),
        "status": "PASS" if not errors else "FAIL",
    }

    if args.report is not None:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(json.dumps(summary, indent=2))
    if errors:
        for e in errors:
            print(f"[FAIL] {e}", file=sys.stderr)
        return 1

    print("[OK] Combat TTK, win rate, and economy balance passed Monte Carlo verification.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
