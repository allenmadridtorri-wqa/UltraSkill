#!/usr/bin/env python3
"""Audit weapon, enemy, and item stat tables for missing IDs, broken references, and TTK/DPS outliers."""

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List, Tuple


def validate_stat_tables(data: Dict[str, Any]) -> Tuple[bool, List[str], List[Dict[str, Any]]]:
    errors: List[str] = []
    report: List[Dict[str, Any]] = []

    weapons = data.get("weapons", {})
    enemies = data.get("enemies", {})
    items = data.get("items", {})

    if not weapons:
        errors.append("Stat table must define at least one weapon in 'weapons'.")
    if not enemies:
        errors.append("Stat table must define at least one enemy in 'enemies'.")

    # 1. Validate Weapons
    weapon_dps: Dict[str, float] = {}
    for wid, w in weapons.items():
        dmg = w.get("base_damage", 0)
        rate = w.get("attack_speed_hz", 0.0)
        startup_f = w.get("startup_frames", 0)
        active_f = w.get("active_frames", 0)
        recovery_f = w.get("recovery_frames", 0)

        if dmg <= 0 or rate <= 0:
            errors.append(f"Weapon '{wid}' has non-positive damage ({dmg}) or attack_speed_hz ({rate}).")
        if startup_f < 2 or active_f < 1 or recovery_f < 4:
            errors.append(
                f"Weapon '{wid}' frame window invalid (startup={startup_f}, active={active_f}, recovery={recovery_f})."
            )
        dps = round(dmg * rate, 2)
        weapon_dps[wid] = dps

    # 2. Validate Enemies & TTK ratios against median weapon DPS
    dps_values = sorted(weapon_dps.values())
    baseline_dps = dps_values[len(dps_values) // 2] if dps_values else 1.0

    for eid, e in enemies.items():
        hp = e.get("hp", 0)
        tier = e.get("tier", "grunt")
        loot_table = e.get("drops", [])
        if hp <= 0:
            errors.append(f"Enemy '{eid}' has non-positive hp ({hp}).")
        ttk = round(hp / baseline_dps, 2) if baseline_dps > 0 else 0.0

        # Check TTK bounds by tier
        bounds = {
            "fodder": (0.4, 3.0),
            "grunt": (1.5, 8.0),
            "elite": (6.0, 25.0),
            "boss": (30.0, 180.0),
        }.get(tier, (0.4, 180.0))

        if not (bounds[0] <= ttk <= bounds[1]):
            errors.append(
                f"Enemy '{eid}' (tier={tier}) TTK={ttk}s against baseline DPS ({baseline_dps}) outside {bounds}s."
            )

        for drop_id in loot_table:
            if drop_id not in items and drop_id not in weapons:
                errors.append(f"Enemy '{eid}' references undefined drop item '{drop_id}'.")

        report.append({"enemy_id": eid, "tier": tier, "hp": hp, "baseline_ttk_sec": ttk})

    return len(errors) == 0, errors, report


def run_self_test() -> int:
    sample_data = {
        "weapons": {
            "iron_sword": {
                "base_damage": 25,
                "attack_speed_hz": 1.6,
                "startup_frames": 7,
                "active_frames": 4,
                "recovery_frames": 12,
            },
            "great_hammer": {
                "base_damage": 65,
                "attack_speed_hz": 0.7,
                "startup_frames": 18,
                "active_frames": 5,
                "recovery_frames": 24,
            },
        },
        "items": {
            "scrap_metal": {"max_stack": 50, "sell_value": 5},
            "healing_herb": {"max_stack": 10, "sell_value": 12},
        },
        "enemies": {
            "scout_drone": {"tier": "fodder", "hp": 45, "drops": ["scrap_metal"]},
            "shield_trooper": {"tier": "grunt", "hp": 140, "drops": ["scrap_metal", "healing_herb"]},
            "warden_mech": {"tier": "elite", "hp": 520, "drops": ["iron_sword"]},
        },
    }
    ok, errs, rep = validate_stat_tables(sample_data)
    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print(f"Self-test PASSED: validated {len(rep)} enemy TTK profiles and all loot references.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, help="Path to JSON stat table")
    parser.add_argument("--self-test", action="store_true", help="Run built-in stat table verification test")
    args = parser.parse_args()

    if args.self_test or args.input is None:
        return run_self_test()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    ok, errs, rep = validate_stat_tables(data)
    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "ok", "enemy_ttk_profiles": rep}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
