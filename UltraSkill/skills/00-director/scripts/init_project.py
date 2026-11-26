#!/usr/bin/env python3
"""
Initialize an UltraSkill studio project ledger directory.

Copies BRIEF.md, BARS.md, ROUNDS.md, DECISIONS.md, and QUALITY.md from
skills/00-director/templates/ into the target directory and stamps the
project slug and UTC date.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path


TEMPLATE_FILES = [
    "BRIEF.md",
    "BARS.md",
    "ROUNDS.md",
    "DECISIONS.md",
    "QUALITY.md",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="init_project.py",
        description="Scaffold a new UltraSkill studio ledger directory from 00-director templates.",
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Short project slug (e.g., 'chronometer-still' or 'arena-vertical-slice').",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Target directory where BRIEF.md, BARS.md, ROUNDS.md, DECISIONS.md, and QUALITY.md will be created.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing ledger files if present.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    templates_dir = Path(__file__).resolve().parent.parent / "templates"

    if not templates_dir.is_dir():
        print(f"[ERROR] Templates directory not found: {templates_dir}", file=sys.stderr)
        return 1

    output_dir: Path = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    created: list[Path] = []
    for filename in TEMPLATE_FILES:
        src = templates_dir / filename
        dst = output_dir / filename
        if not src.is_file():
            print(f"[ERROR] Missing template file: {src}", file=sys.stderr)
            return 1
        if dst.exists() and not args.force:
            print(
                f"[ERROR] '{dst}' already exists. Pass --force to overwrite.",
                file=sys.stderr,
            )
            return 2

        content = src.read_text(encoding="utf-8")
        content = content.replace("<PROJECT_SLUG>", args.name)
        content = content.replace("2026-11-26", today_utc)
        dst.write_text(content, encoding="utf-8")
        created.append(dst)

    print(f"[OK] Initialized project '{args.name}' ledger in {output_dir}:")
    for path in created:
        print(f"  - {path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
