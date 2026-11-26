#!/usr/bin/env python3
"""
Verify that a project ledger satisfies all UltraSkill quality gates before shipping.

Parses BARS.md and QUALITY.md in the specified ledger directory and verifies:
  1. At least one quality bar table row is defined in BARS.md.
  2. Every bar has a numeric score >= min_score (default: 4 out of 5) and status PASS.
  3. QUALITY.md reports 0 open Blockers (BLKR) and 0 open Major defects (MAJR),
     and Overall Gate Verdict is PASS.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="check_gates.py",
        description="Validate BARS.md and QUALITY.md before approving a deliverable to ship.",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        required=True,
        help="Directory containing BARS.md and QUALITY.md.",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=4,
        help="Minimum passing score for each quality bar on a 0-5 scale (default: 4).",
    )
    return parser.parse_args(argv)


def check_bars_file(bars_path: Path, min_score: int) -> list[str]:
    errors: list[str] = []
    if not bars_path.is_file():
        return [f"Missing BARS.md at {bars_path}"]

    text = bars_path.read_text(encoding="utf-8")
    bar_rows = 0

    for line_num, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 6:
            continue
        if cells[0].lower() in ("bar id", "id"):
            continue

        bar_id = cells[0].strip("` ")
        score_str = cells[4].strip("` ")
        status_str = cells[5].strip("` ").upper()
        bar_rows += 1

        try:
            score = int(score_str)
        except ValueError:
            errors.append(f"BARS.md:{line_num} ({bar_id}): non-integer score '{score_str}'")
            continue

        if score < min_score:
            errors.append(
                f"BARS.md:{line_num} ({bar_id}): score {score}/5 is below minimum threshold {min_score}/5"
            )
        if status_str != "PASS":
            errors.append(
                f"BARS.md:{line_num} ({bar_id}): status is '{status_str}' (expected 'PASS')"
            )

    if bar_rows == 0:
        errors.append("BARS.md contains zero parsed quality bar rows.")

    return errors


def check_quality_file(quality_path: Path) -> list[str]:
    errors: list[str] = []
    if not quality_path.is_file():
        return [f"Missing QUALITY.md at {quality_path}"]

    text = quality_path.read_text(encoding="utf-8")

    blkr_match = re.search(r"Open Blockers\s*\(`?BLKR`?\)\*\*:\s*`?(\d+)`?", text)
    if not blkr_match:
        errors.append("QUALITY.md: missing 'Open Blockers (`BLKR`): `<count>`' field.")
    elif int(blkr_match.group(1)) != 0:
        errors.append(f"QUALITY.md: {blkr_match.group(1)} open Blocker (BLKR) defects remain.")

    majr_match = re.search(r"Open Major Defects\s*\(`?MAJR`?\)\*\*:\s*`?(\d+)`?", text)
    if not majr_match:
        errors.append("QUALITY.md: missing 'Open Major Defects (`MAJR`): `<count>`' field.")
    elif int(majr_match.group(1)) != 0:
        errors.append(f"QUALITY.md: {majr_match.group(1)} open Major (MAJR) defects remain.")

    verdict_match = re.search(r"Overall Gate Verdict\*\*:\s*`?([A-Z_]+)`?", text)
    if not verdict_match:
        errors.append("QUALITY.md: missing 'Overall Gate Verdict: `<STATUS>`' field.")
    elif verdict_match.group(1) != "PASS":
        errors.append(
            f"QUALITY.md: Overall Gate Verdict is '{verdict_match.group(1)}' (expected 'PASS')."
        )

    return errors


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    ledger_dir: Path = args.ledger.resolve()

    errors: list[str] = []
    errors.extend(check_bars_file(ledger_dir / "BARS.md", args.min_score))
    errors.extend(check_quality_file(ledger_dir / "QUALITY.md"))

    if errors:
        print(f"[FAIL] Quality gate check failed for {ledger_dir}:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"[OK] All quality gates in {ledger_dir} passed (min_score={args.min_score}/5, 0 BLKR, 0 MAJR).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
