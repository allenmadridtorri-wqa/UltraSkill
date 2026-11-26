#!/usr/bin/env python3
"""
Append a validated iteration round to ROUNDS.md and enforce the 5-round studio cap.

Ensures that:
  1. Only a single weakest bar is targeted per round.
  2. The round number does not exceed the 5-round default maximum without
     raising an explicit cap warning requiring user escalation.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MAX_ROUNDS_DEFAULT = 5


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="log_round.py",
        description="Log a completed quality round into ROUNDS.md and enforce the 5-round cap.",
    )
    parser.add_argument(
        "--rounds-file",
        type=Path,
        required=True,
        help="Path to the project's ROUNDS.md file.",
    )
    parser.add_argument(
        "--round",
        type=int,
        dest="round_num",
        required=True,
        help="Round number (1 to 5).",
    )
    parser.add_argument(
        "--artifact",
        required=True,
        help="Real output artifact inspected (e.g., 'frame_0001_review.png' or 'test_report.json').",
    )
    parser.add_argument(
        "--scores",
        required=True,
        help="Summary of bar scores (e.g., 'BAR-01:5, BAR-02:3, BAR-03:4').",
    )
    parser.add_argument(
        "--weakest-bar",
        required=True,
        help="Single weakest bar ID targeted in this round (e.g., 'BAR-02' or 'NONE' if all passed).",
    )
    parser.add_argument(
        "--fix",
        required=True,
        help="Concrete single fix applied to address the weakest bar.",
    )
    parser.add_argument(
        "--verdict",
        choices=["CONTINUE", "PASS", "HALT_CAP_REACHED", "HALT_BLOCKER"],
        required=True,
        help="Round outcome verdict.",
    )
    return parser.parse_args(argv)


def validate_single_bar(weakest_bar: str) -> None:
    if "," in weakest_bar or ";" in weakest_bar or "/" in weakest_bar:
        raise ValueError(
            f"Invalid --weakest-bar '{weakest_bar}'. Fix only ONE weakest bar per round."
        )


def sanitize_cell(text: str) -> str:
    return text.replace("|", "/").replace("\n", " ").strip()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    if args.round_num < 1:
        print("[ERROR] --round must be >= 1.", file=sys.stderr)
        return 2

    try:
        validate_single_bar(args.weakest_bar)
    except ValueError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 2

    rounds_path: Path = args.rounds_file.resolve()
    if not rounds_path.is_file():
        print(f"[ERROR] ROUNDS.md not found at {rounds_path}", file=sys.stderr)
        return 1

    verdict = args.verdict
    if args.round_num >= MAX_ROUNDS_DEFAULT and verdict == "CONTINUE":
        verdict = "HALT_CAP_REACHED"
        print(
            f"[WARN] Round {args.round_num} reached the {MAX_ROUNDS_DEFAULT}-round studio cap. "
            "Overriding verdict to HALT_CAP_REACHED. Report status to the user now.",
            file=sys.stderr,
        )

    row = (
        f"| {args.round_num} | `{sanitize_cell(args.artifact)}` | "
        f"`{sanitize_cell(args.scores)}` | `{sanitize_cell(args.weakest_bar)}` | "
        f"{sanitize_cell(args.fix)} | {verdict} |\n"
    )

    content = rounds_path.read_text(encoding="utf-8")
    if not content.endswith("\n"):
        content += "\n"

    existing_rounds = re.findall(r"^\|\s*(\d+)\s*\|", content, flags=re.MULTILINE)
    if str(args.round_num) in existing_rounds:
        lines = content.splitlines(keepends=True)
        updated_lines = []
        for line in lines:
            if re.match(rf"^\|\s*{args.round_num}\s*\|", line):
                updated_lines.append(row)
            else:
                updated_lines.append(line)
        rounds_path.write_text("".join(updated_lines), encoding="utf-8")
        print(f"[OK] Updated Round {args.round_num} in {rounds_path} (verdict: {verdict}).")
    else:
        rounds_path.write_text(content + row, encoding="utf-8")
        print(f"[OK] Appended Round {args.round_num} to {rounds_path} (verdict: {verdict}).")

    if args.round_num > MAX_ROUNDS_DEFAULT:
        print(
            f"[ERROR] Round {args.round_num} exceeds the hard cap of {MAX_ROUNDS_DEFAULT}.",
            file=sys.stderr,
        )
        return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
