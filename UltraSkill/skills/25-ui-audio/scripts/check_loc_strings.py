#!/usr/bin/env python3
"""Audit localization JSON/CSV string tables for missing translations, mismatched {placeholders}, and expansion overflows."""

import argparse
import csv
import io
import json
import pathlib
import re
import sys
from typing import Dict, List, Set, Tuple


PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z0-9_]+)\}")


def extract_placeholders(text: str) -> Set[str]:
    return set(PLACEHOLDER_RE.findall(text))


def audit_table(
    rows: List[Dict[str, str]],
    base_locale: str = "en",
    max_expansion_ratio: float = 2.2,
) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    if not rows:
        return False, ["Localization table is empty."]

    headers = list(rows[0].keys())
    if "key" not in headers or base_locale not in headers:
        return False, [f"Table must include 'key' and base locale '{base_locale}' columns (got {headers})."]

    locales = [h for h in headers if h != "key"]
    seen_keys: Set[str] = set()

    for line_idx, row in enumerate(rows, start=2):
        key = (row.get("key") or "").strip()
        if not key:
            errors.append(f"Row {line_idx}: empty localization key.")
            continue
        if key in seen_keys:
            errors.append(f"Row {line_idx}: duplicate localization key '{key}'.")
        seen_keys.add(key)

        base_text = (row.get(base_locale) or "").strip()
        if not base_text:
            errors.append(f"Key '{key}': missing base locale '{base_locale}' text.")
            continue

        base_tokens = extract_placeholders(base_text)

        for loc in locales:
            if loc == base_locale:
                continue
            val = (row.get(loc) or "").strip()
            if not val:
                errors.append(f"Key '{key}': missing translation for locale '{loc}'.")
                continue
            loc_tokens = extract_placeholders(val)
            if loc_tokens != base_tokens:
                errors.append(
                    f"Key '{key}' [{loc}]: placeholder mismatch (expected {sorted(base_tokens)}, got {sorted(loc_tokens)})."
                )
            if len(base_text) >= 8 and (len(val) / len(base_text)) > max_expansion_ratio:
                errors.append(
                    f"Key '{key}' [{loc}]: extreme text expansion ({len(val)} vs {len(base_text)} chars > {max_expansion_ratio}x)."
                )

    return len(errors) == 0, errors


def run_self_test() -> int:
    sample_csv = """key,en,de,es
UI_MAIN_START,Start Expedition,Expedition starten,Iniciar expedición
HUD_PROMPT_OPEN,Open {target},{target} öffnen,Abrir {target}
COMBAT_DMG_DEALT,{attacker} dealt {amount} damage,{attacker} verursachte {amount} Schaden,{attacker} infligió {amount} de daño
"""
    reader = list(csv.DictReader(io.StringIO(sample_csv.strip())))
    ok, errs = audit_table(reader)
    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print(f"Self-test PASSED: verified {len(reader)} localization keys across en/de/es.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, help="Path to localization .csv or .json file")
    parser.add_argument("--base-locale", default="en", help="Base locale code (default: en)")
    parser.add_argument("--self-test", action="store_true", help="Run built-in localization self-test")
    args = parser.parse_args()

    if args.self_test or args.input is None:
        return run_self_test()

    raw = args.input.read_text(encoding="utf-8")
    if args.input.suffix.lower() == ".json":
        rows = json.loads(raw)
    else:
        rows = list(csv.DictReader(io.StringIO(raw)))

    ok, errs = audit_table(rows, base_locale=args.base_locale)
    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print(f"Localization check PASSED ({len(rows)} keys).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
