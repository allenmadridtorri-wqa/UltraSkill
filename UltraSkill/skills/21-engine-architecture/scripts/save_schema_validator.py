#!/usr/bin/env python3
"""Validate game save JSON files, verify SHA-256 payload checksums, and test v1->vN migrations."""

import argparse
import copy
import hashlib
import json
import pathlib
import sys
from typing import Any, Callable, Dict, List, Tuple


SALT = "ultraskill-save-v1"
CURRENT_SCHEMA_VERSION = 3


def compute_payload_checksum(payload: Dict[str, Any], salt: str = SALT) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((salt + canonical).encode("utf-8")).hexdigest()


def migrate_v1_to_v2(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate flat string inventory to structured item dicts and add stamina_max."""
    player = payload.setdefault("player", {})
    inv = player.get("inventory", [])
    normalized_inv = []
    for entry in inv:
        if isinstance(entry, str):
            normalized_inv.append({"item_id": entry, "qty": 1, "durability": 100})
        elif isinstance(entry, dict):
            normalized_inv.append(entry)
    player["inventory"] = normalized_inv
    player.setdefault("stamina_max", 100)
    return payload


def migrate_v2_to_v3(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure world_flags and stats blocks exist."""
    payload.setdefault("world_flags", {})
    payload.setdefault("stats", {"deaths": 0, "enemies_defeated": 0})
    return payload


MIGRATIONS: Dict[int, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
    1: migrate_v1_to_v2,
    2: migrate_v2_to_v3,
}


def validate_and_migrate(
    doc: Dict[str, Any], verify_checksum: bool = True
) -> Tuple[bool, List[str], Dict[str, Any]]:
    errors: List[str] = []
    out = copy.deepcopy(doc)

    for req_key in ("schema_version", "game_version", "timestamp_utc", "playtime_seconds", "payload"):
        if req_key not in out:
            errors.append(f"Missing required envelope field: '{req_key}'")
    if errors:
        return False, errors, out

    version = out["schema_version"]
    if not isinstance(version, int) or version < 1:
        errors.append(f"Invalid schema_version: {version}")
        return False, errors, out

    if out["playtime_seconds"] < 0:
        errors.append(f"Negative playtime_seconds: {out['playtime_seconds']}")

    payload = out["payload"]
    if not isinstance(payload, dict):
        errors.append("Envelope 'payload' must be a JSON object")
        return False, errors, out

    if verify_checksum and "checksum_sha256" in out:
        expected = compute_payload_checksum(payload)
        if out["checksum_sha256"] != expected:
            errors.append(
                f"Checksum mismatch: file has {out['checksum_sha256']}, computed {expected}"
            )
            return False, errors, out

    while version < CURRENT_SCHEMA_VERSION:
        step_fn = MIGRATIONS.get(version)
        if step_fn is None:
            errors.append(f"No migration registered from version {version}")
            return False, errors, out
        payload = step_fn(payload)
        version += 1

    out["schema_version"] = version
    out["payload"] = payload
    out["checksum_sha256"] = compute_payload_checksum(payload)

    # Validate final v3 schema invariants
    player = payload.get("player", {})
    if not isinstance(player.get("level"), int) or player.get("level", 0) < 1:
        errors.append("payload.player.level must be an integer >= 1")
    if not isinstance(player.get("position"), list) or len(player.get("position", [])) != 3:
        errors.append("payload.player.position must be a 3-element [x, y, z] list")

    return len(errors) == 0, errors, out


def run_self_test() -> int:
    v1_payload = {
        "player": {
            "level": 5,
            "hp_current": 80,
            "hp_max": 100,
            "position": [4.0, 0.0, -8.5],
            "inventory": ["rusted_sword", "health_potion"],
        }
    }
    v1_doc = {
        "schema_version": 1,
        "game_version": "1.0.0",
        "timestamp_utc": "2026-01-10T12:00:00Z",
        "playtime_seconds": 3600,
        "checksum_sha256": compute_payload_checksum(v1_payload),
        "payload": v1_payload,
    }
    ok, errs, migrated = validate_and_migrate(v1_doc, verify_checksum=True)
    if not ok:
        print(f"Self-test failed: {errs}", file=sys.stderr)
        return 1
    assert migrated["schema_version"] == CURRENT_SCHEMA_VERSION
    assert migrated["payload"]["player"]["inventory"][0]["item_id"] == "rusted_sword"
    print(f"Self-test PASSED: v1 save migrated cleanly to v{CURRENT_SCHEMA_VERSION}.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, help="Input save JSON file to validate")
    parser.add_argument("--output", type=pathlib.Path, help="Optional path to write migrated save JSON")
    parser.add_argument("--skip-checksum", action="store_true", help="Skip input SHA-256 verification")
    parser.add_argument("--self-test", action="store_true", help="Run built-in migration self-test")
    args = parser.parse_args()

    if args.self_test or args.input is None:
        return run_self_test()

    doc = json.loads(args.input.read_text(encoding="utf-8"))
    ok, errors, migrated = validate_and_migrate(doc, verify_checksum=not args.skip_checksum)
    if not ok:
        for err in errors:
            print(f"[ERROR] {err}", file=sys.stderr)
        return 1

    if args.output:
        args.output.write_text(json.dumps(migrated, indent=2) + "\n", encoding="utf-8")
    print(f"Save valid and migrated to schema_version={migrated['schema_version']}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
