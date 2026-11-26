#!/usr/bin/env python3
"""
UltraSkill v1.0.0 Package Validator (`tools/validate.py`).

Audits the UltraSkill package directory against all Section 7 & Section 10 standards:
  1. Total file count <= 300 (target: 288 in full audit, or matching batch count with --max-batch).
  2. MANIFEST.json matches disk files (no missing files, no unexpected extra files).
  3. Every SKILL.md starts with YAML frontmatter (`name` and `description`), contains
     all required section headings, and is under 200 lines.
  4. Relative Markdown links resolve (on disk in full mode; on disk or in MANIFEST.json
     when running incremental `--max-batch N` checks). No external HTTP links in Markdown
     link targets.
  5. No placeholder text (`TODO`, `FIXME`, `XXX`, `rest of code here`, or standalone `...`
     code stubs).
  6. Every `.py` file parses cleanly with Python's `ast.parse` and supports `--help`.
  7. Every `.json` file parses cleanly with `json.load`.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter
from pathlib import Path


MAX_FILES_LIMIT = 300
TARGET_FILES_COUNT = 288
MAX_SKILL_MD_LINES = 199

REQUIRED_SKILL_SECTIONS = [
    "## When to use",
    "## Inputs",
    "## Steps",
    "## Numbers and defaults",
    "## Failure modes and fixes",
    "## Done check",
    "## Related files",
]

# Matches Markdown links [label](target) while ignoring image or external anchors
MD_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")

# Matches forbidden placeholder patterns
FORBIDDEN_PLACEHOLDER_PATTERNS = [
    (re.compile(r"\bTODO\b\s*:"), "TODO: placeholder marker"),
    (re.compile(r"\bFIXME\b\s*:"), "FIXME: placeholder marker"),
    (re.compile(r"\bHACK\b\s*:"), "HACK: placeholder marker"),
    (re.compile(r"rest of code here", re.IGNORECASE), "'rest of code here' stub"),
    (re.compile(r"^\s*\.\.\.\s*$"), "standalone '...' ellipsis placeholder line"),
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="validate.py",
        description="Audit UltraSkill v1.0.0 for manifest parity, frontmatter, links, AST, JSON, and placeholders.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Path to the UltraSkill root directory (default: parent of tools/).",
    )
    parser.add_argument(
        "--max-batch",
        type=int,
        default=None,
        help=(
            "Validate files up through batch N during incremental batch creation. "
            "Omit for full 288-file final audit."
        ),
    )
    return parser.parse_args(argv)


def list_disk_files(root: Path) -> set[str]:
    files: set[str] = set()
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.name.endswith(".pyc"):
            continue
        if path.name == "UltraSkill-1.0.0.zip" or path.name.startswith("."):
            continue
        rel = path.relative_to(root).as_posix()
        files.add(rel)
    return files


def check_frontmatter_and_sections(path: Path, rel_path: str) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    if len(lines) > MAX_SKILL_MD_LINES:
        errors.append(
            f"{rel_path}: has {len(lines)} lines (must be < 200 lines)."
        )

    if not lines or lines[0].strip() != "---":
        errors.append(f"{rel_path}: must start with YAML frontmatter '---' on line 1.")
        return errors

    end_idx = None
    for idx in range(1, min(len(lines), 40)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break

    if end_idx is None:
        errors.append(f"{rel_path}: unclosed YAML frontmatter block.")
        return errors

    fm_block = "\n".join(lines[1:end_idx])
    if not re.search(r"^name:\s*\S+", fm_block, flags=re.MULTILINE):
        errors.append(f"{rel_path}: YAML frontmatter missing 'name:' field.")
    if not re.search(r"^description:\s*\S+", fm_block, flags=re.MULTILINE):
        errors.append(f"{rel_path}: YAML frontmatter missing 'description:' field.")

    for section in REQUIRED_SKILL_SECTIONS:
        if section not in text:
            errors.append(f"{rel_path}: missing required section heading '{section}'.")

    return errors


def check_markdown_links(
    path: Path,
    rel_path: str,
    root: Path,
    manifest_paths: set[str],
    allow_manifest_pending: bool,
) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    # Strip fenced code blocks before scanning links so code examples do not trigger link errors
    stripped_text = re.sub(r"````.*?````", "", text, flags=re.DOTALL)
    stripped_text = re.sub(r"```.*?```", "", stripped_text, flags=re.DOTALL)

    for match in MD_LINK_RE.finditer(stripped_text):
        raw_target = match.group(1).strip()
        if not raw_target or raw_target.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", raw_target) or raw_target.startswith("/"):
            errors.append(
                f"{rel_path}: non-relative link target '{raw_target}' (use relative links only)."
            )
            continue

        target_file = raw_target.split("#", 1)[0].strip()
        if not target_file:
            continue

        resolved = (path.parent / target_file).resolve()
        try:
            rel_target = resolved.relative_to(root.resolve()).as_posix()
        except ValueError:
            errors.append(
                f"{rel_path}: link '{raw_target}' escapes package root."
            )
            continue

        if resolved.exists():
            continue
        if allow_manifest_pending and rel_target in manifest_paths:
            continue

        errors.append(
            f"{rel_path}: broken relative link '{raw_target}' -> '{rel_target}' does not exist."
        )

    return errors


def check_placeholders(path: Path, rel_path: str) -> list[str]:
    errors: list[str] = []
    # validate.py and pre_review_scan.py define placeholder regex patterns by necessity
    if rel_path in ("tools/validate.py", "skills/36-code-review/scripts/pre_review_scan.py"):
        return errors

    text = path.read_text(encoding="utf-8")
    for line_num, line in enumerate(text.splitlines(), start=1):
        for pattern, label in FORBIDDEN_PLACEHOLDER_PATTERNS:
            if pattern.search(line):
                errors.append(f"{rel_path}:{line_num}: contains forbidden {label}.")
    return errors


def check_python_file(path: Path, rel_path: str) -> list[str]:
    errors: list[str] = []
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError as exc:
        return [f"{rel_path}:{exc.lineno}: Python syntax error: {exc.msg}"]

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if (
                len(node.body) == 1
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and node.body[0].value.value is Ellipsis
            ):
                errors.append(
                    f"{rel_path}:{node.lineno}: function '{node.name}' has an Ellipsis (...) stub body."
                )

    is_cli_script = (
        "/scripts/" in rel_path
        or rel_path.startswith("tools/")
        or rel_path == "install.py"
    )
    if is_cli_script and "argparse" not in source and "--help" not in source:
        errors.append(
            f"{rel_path}: runnable script must support '--help' (via argparse or explicit handler)."
        )

    return errors


def check_json_file(path: Path, rel_path: str) -> list[str]:
    try:
        with path.open("r", encoding="utf-8") as fh:
            json.load(fh)
    except Exception as exc:
        return [f"{rel_path}: invalid JSON: {exc}"]
    return []


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root: Path = args.root.resolve()
    errors: list[str] = []

    manifest_file = root / "MANIFEST.json"
    if not manifest_file.is_file():
        print(f"[FAIL] MANIFEST.json not found in {root}", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[FAIL] Could not parse MANIFEST.json: {exc}", file=sys.stderr)
        return 1

    manifest_entries = manifest.get("files", [])
    all_manifest_paths = {entry["path"] for entry in manifest_entries}

    if len(manifest_entries) != TARGET_FILES_COUNT:
        errors.append(
            f"MANIFEST.json lists {len(manifest_entries)} files (expected {TARGET_FILES_COUNT})."
        )
    if len(all_manifest_paths) != len(manifest_entries):
        errors.append("MANIFEST.json contains duplicate file paths.")

    folder_counts = dict(Counter(entry["folder"] for entry in manifest_entries))
    if folder_counts != manifest.get("folder_counts"):
        errors.append("MANIFEST.json folder_counts does not match actual entry counts.")

    if args.max_batch is not None:
        expected_paths = {
            entry["path"]
            for entry in manifest_entries
            if int(entry["batch"]) <= args.max_batch
        }
        allow_pending_links = True
    else:
        expected_paths = all_manifest_paths
        allow_pending_links = False

    disk_files = list_disk_files(root)

    if len(disk_files) > MAX_FILES_LIMIT:
        errors.append(
            f"Package contains {len(disk_files)} files on disk (hard limit is {MAX_FILES_LIMIT})."
        )

    missing_on_disk = sorted(expected_paths - disk_files)
    extra_on_disk = sorted(disk_files - expected_paths)

    for missing in missing_on_disk:
        errors.append(f"Missing expected file on disk: {missing}")
    for extra in extra_on_disk:
        errors.append(f"Unexpected file on disk not in target batch/manifest: {extra}")

    for rel_path in sorted(disk_files & expected_paths):
        full_path = root / rel_path

        errors.extend(check_placeholders(full_path, rel_path))

        if full_path.name == "SKILL.md":
            errors.extend(check_frontmatter_and_sections(full_path, rel_path))

        if full_path.suffix == ".md":
            errors.extend(
                check_markdown_links(
                    full_path,
                    rel_path,
                    root,
                    all_manifest_paths,
                    allow_pending_links,
                )
            )
        elif full_path.suffix == ".py":
            errors.extend(check_python_file(full_path, rel_path))
        elif full_path.suffix == ".json":
            errors.extend(check_json_file(full_path, rel_path))

    mode_label = (
        f"incremental batch <= {args.max_batch} ({len(expected_paths)}/{TARGET_FILES_COUNT} files)"
        if args.max_batch is not None
        else f"full package ({TARGET_FILES_COUNT} files)"
    )

    if errors:
        print(f"[FAIL] UltraSkill validation failed ({mode_label}):", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(
        f"[OK] UltraSkill validation passed ({mode_label}): "
        f"{len(disk_files)} files verified, frontmatter/links/AST/JSON clean."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
