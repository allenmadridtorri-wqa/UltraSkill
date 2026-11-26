#!/usr/bin/env python3
"""
UltraSkill v1.0.0 Portable Installer.

Copies the UltraSkill package into a target workspace directory according to the
verified skill-loading convention of the chosen AI coding environment:
  - Antigravity IDE / CLI: <target>/.agents/skills/UltraSkill/
  - Claude Code / Claude Projects: <target>/.claude/skills/UltraSkill/
  - Google AI Studio: <target>/UltraSkill/
  - ChatGPT / Codex CLI: <target>/.agents/skills/UltraSkill/

Also prints exact, verified instructions for loading UltraSkill in all four tools
without exceeding context budgets.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


AGENT_PATHS = {
    "antigravity": Path(".agents") / "skills" / "UltraSkill",
    "claude": Path(".claude") / "skills" / "UltraSkill",
    "aistudio": Path("UltraSkill"),
    "chatgpt": Path(".agents") / "skills" / "UltraSkill",
}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="install.py",
        description=(
            "Install UltraSkill v1.0.0 into a project directory and display "
            "verified loading instructions for Antigravity IDE, Google AI Studio, "
            "Claude, and ChatGPT."
        ),
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="Target workspace or project root directory where UltraSkill should be copied.",
    )
    parser.add_argument(
        "--agent",
        choices=["antigravity", "aistudio", "claude", "chatgpt", "all"],
        default="all",
        help="Target AI tool convention to install for (default: all).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing destination directory if it already exists.",
    )
    parser.add_argument(
        "--guide-only",
        action="store_true",
        help="Print verified loading instructions for all four tools without copying files.",
    )
    return parser.parse_args(argv)


def verify_source_root(source_root: Path) -> dict:
    manifest_path = source_root / "MANIFEST.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(
            f"MANIFEST.json not found in {source_root}. Run install.py from inside UltraSkill/."
        )
    with manifest_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def copy_package(source_root: Path, dest_dir: Path, force: bool) -> int:
    source_resolved = source_root.resolve()
    dest_resolved = dest_dir.resolve()

    if source_resolved == dest_resolved:
        print(f"[SKIP] Source and destination are identical: {dest_resolved}")
        return 0

    if dest_resolved.exists():
        if not force:
            raise FileExistsError(
                f"Destination '{dest_resolved}' already exists. Pass --force to overwrite."
            )
        shutil.rmtree(dest_resolved)

    dest_resolved.parent.mkdir(parents=True, exist_ok=True)

    copied = 0
    for item in sorted(source_resolved.rglob("*")):
        if "__pycache__" in item.parts or item.name.endswith(".pyc"):
            continue
        rel = item.relative_to(source_resolved)
        target_item = dest_resolved / rel
        if item.is_dir():
            target_item.mkdir(parents=True, exist_ok=True)
        elif item.is_file():
            target_item.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target_item)
            copied += 1

    return copied


def print_loading_guide(target_base: Path | None) -> None:
    base_str = str(target_base.resolve()) if target_base else "<project-root>"
    guide = f"""
================================================================================
UltraSkill v1.0.0 — Verified Loading Conventions Across All Four Tools
================================================================================

1. ANTIGRAVITY IDE (Project & Global Agent Skills Standard)
   - Convention: Antigravity discovers skills via `<project>/.agents/skills/<skill-name>/SKILL.md`
     (with backward compatibility for `.agent/skills/`) or globally at
     `~/.gemini/config/skills/<skill-name>/SKILL.md`.
   - Installed Path: {base_str}/.agents/skills/UltraSkill/
   - How to load:
     * Keep `UltraSkill/SKILL.md` at the root of the installed folder so Antigravity
       indexes the YAML frontmatter (`name: ultraskill`).
     * You can also expose individual sub-skills directly by copying or symlinking
       `UltraSkill/skills/*` into `{base_str}/.agents/skills/`.
     * Prompt: "Use @ultraskill (or read .agents/skills/UltraSkill/SKILL.md) to route
       this task, start a 00-director round ledger, and load only the active skill."

2. GOOGLE AI STUDIO (Build Mode & Chat / System Instructions)
   - Convention: AI Studio Build mode reads files directly from the workspace tree;
     Chat mode accepts Markdown/script attachments or System Instructions.
   - Installed Path: {base_str}/UltraSkill/
   - How to load:
     * Build Mode: Keep `UltraSkill/` in the workspace root and instruct the agent:
       "Read UltraSkill/SKILL.md first and follow its progressive loading rules."
     * Chat Mode: Attach `UltraSkill/SKILL.md` and `UltraSkill/skills/00-director/SKILL.md`
       plus only the 1-2 sub-skill `SKILL.md` files needed for your task. Never attach
       all 288 files at once.

3. CLAUDE (Claude Code CLI & Claude Desktop / Web Projects)
   - Convention: Claude Code automatically discovers `<project>/.claude/skills/<name>/SKILL.md`
     (and global `~/.claude/skills/<name>/SKILL.md`).
   - Installed Path: {base_str}/.claude/skills/UltraSkill/
   - How to load:
     * Claude Code: Run `claude` in `{base_str}`. Claude indexes the `SKILL.md`
       frontmatter automatically and reads referenced files on demand via file tools.
     * Claude Web / Desktop Projects: Add `UltraSkill/SKILL.md` and the specific
       `skills/<id>/SKILL.md` for your current milestone to Project Knowledge.

4. CHATGPT (Codex CLI / Agent Mode & ChatGPT Projects / Code Interpreter)
   - Convention: OpenAI Codex CLI and `.agents`-compatible environments read
     `<project>/.agents/skills/<name>/SKILL.md` or project instruction files;
     ChatGPT Web/Desktop supports Project Files and Code Interpreter zip archives.
   - Installed Path: {base_str}/.agents/skills/UltraSkill/
   - How to load:
     * Codex / Local Agent: Point the agent at `.agents/skills/UltraSkill/SKILL.md`.
     * ChatGPT Web / Code Interpreter: Run `python3 tools/pack.py` to generate
       `UltraSkill-1.0.0.zip`, upload the zip to your conversation or Project, and
       prompt: "Inspect UltraSkill-1.0.0.zip, read SKILL.md first, and load only the
       skill required for my prompt."
================================================================================
"""
    print(guide.strip())


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_root = Path(__file__).resolve().parent

    try:
        manifest = verify_source_root(source_root)
    except Exception as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    if args.guide_only:
        print_loading_guide(args.target)
        return 0

    if args.target is None:
        print(
            "[ERROR] --target <directory> is required unless --guide-only is set.\n"
            "Run `python3 install.py --help` for usage.",
            file=sys.stderr,
        )
        return 2

    agents_to_install = (
        ["antigravity", "aistudio", "claude"]
        if args.agent == "all"
        else [args.agent]
    )

    installed_destinations: set[Path] = set()
    try:
        for agent_key in agents_to_install:
            rel_dest = AGENT_PATHS[agent_key]
            dest_dir = args.target / rel_dest
            if dest_dir.resolve() in installed_destinations:
                continue
            count = copy_package(source_root, dest_dir, args.force)
            installed_destinations.add(dest_dir.resolve())
            print(
                f"[OK] Installed {manifest['package']} v{manifest['version']} "
                f"({count} files) -> {dest_dir}"
            )
    except Exception as exc:
        print(f"[ERROR] Installation failed: {exc}", file=sys.stderr)
        return 1

    print_loading_guide(args.target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
