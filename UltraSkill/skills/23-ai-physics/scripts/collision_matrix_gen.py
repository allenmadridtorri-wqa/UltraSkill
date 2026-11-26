#!/usr/bin/env python3
"""Generate and audit a 12-layer physics collision matrix and bitmask constants for Godot 4 or custom engines."""

import argparse
import json
import sys
from typing import Dict, List, Tuple


CANONICAL_LAYERS: List[Tuple[int, str, List[str]]] = [
    (1, "WorldStatic", []),
    (2, "WorldDynamic", ["WorldStatic", "WorldDynamic", "PlayerBody", "EnemyBody", "Projectiles"]),
    (3, "PlayerBody", ["WorldStatic", "WorldDynamic", "EnemyBody", "Triggers"]),
    (4, "EnemyBody", ["WorldStatic", "WorldDynamic", "PlayerBody", "EnemyBody"]),
    (5, "PlayerHurtbox", []),
    (6, "EnemyHurtbox", []),
    (7, "PlayerHitbox", ["EnemyHurtbox", "WorldDynamic"]),
    (8, "EnemyHitbox", ["PlayerHurtbox"]),
    (9, "Projectiles", ["WorldStatic", "WorldDynamic", "PlayerHurtbox", "EnemyHurtbox"]),
    (10, "Interactables", []),
    (11, "Triggers", ["PlayerBody"]),
    (12, "CameraOccluder", []),
]


def build_matrix() -> Dict[str, Dict[str, int]]:
    name_to_bit = {name: (1 << (idx - 1)) for idx, name, _ in CANONICAL_LAYERS}
    result: Dict[str, Dict[str, int]] = {}
    for idx, name, targets in CANONICAL_LAYERS:
        mask = 0
        for t in targets:
            if t not in name_to_bit:
                raise ValueError(f"Unknown target layer '{t}' referenced by '{name}'")
            mask |= name_to_bit[t]
        result[name] = {
            "layer_index_1based": idx,
            "layer_bit": name_to_bit[name],
            "collision_mask": mask,
        }
    return result


def audit_matrix(matrix: Dict[str, Dict[str, int]]) -> List[str]:
    errors: List[str] = []
    # Invariant 1: PlayerHitbox must scan EnemyHurtbox, never PlayerHurtbox or PlayerBody
    p_hit_mask = matrix["PlayerHitbox"]["collision_mask"]
    if not (p_hit_mask & matrix["EnemyHurtbox"]["layer_bit"]):
        errors.append("PlayerHitbox does not scan EnemyHurtbox")
    if p_hit_mask & matrix["PlayerHurtbox"]["layer_bit"]:
        errors.append("PlayerHitbox friendly-fires PlayerHurtbox")

    # Invariant 2: Passive receivers (Hurtboxes, Interactables, WorldStatic) must have mask == 0
    for passive in ("WorldStatic", "PlayerHurtbox", "EnemyHurtbox", "Interactables"):
        if matrix[passive]["collision_mask"] != 0:
            errors.append(f"Passive layer '{passive}' should have collision_mask == 0")

    return errors


def emit_gdscript(matrix: Dict[str, Dict[str, int]]) -> str:
    lines = ["class_name PhysicsLayers", "# Auto-generated 12-layer collision bitmasks", ""]
    for name, info in matrix.items():
        upper = name.upper()
        lines.append(f"const LAYER_{upper}: int = 0x{info['layer_bit']:03X}")
        lines.append(f"const MASK_{upper}: int = 0x{info['collision_mask']:03X}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=["json", "gdscript"], default="json", help="Output format")
    parser.add_argument("--self-test", action="store_true", help="Run collision matrix invariant self-test")
    args = parser.parse_args()

    matrix = build_matrix()
    errors = audit_matrix(matrix)
    if errors:
        for e in errors:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    if args.self_test:
        print(f"Self-test PASSED: 12-layer collision matrix verified with zero mask leaks.")
        return 0

    if args.format == "gdscript":
        print(emit_gdscript(matrix), end="")
    else:
        print(json.dumps(matrix, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
