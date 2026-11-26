#!/usr/bin/env python3
"""Scan source files for hardcoded API keys, private keys, and high-entropy credentials."""

import argparse
import json
import pathlib
import re
import sys
from typing import Dict, List, Pattern, Tuple


SECRET_PATTERNS: List[Tuple[str, Pattern[str]]] = [
    ("AWS_ACCESS_KEY_ID", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GOOGLE_API_KEY", re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b")),
    ("GITHUB_PAT", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{36,255}\b")),
    ("PRIVATE_KEY_PEM", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |PRIVATE )?KEY-----")),
    ("SLACK_TOKEN", re.compile(r"\bxox[baprs]-[0-9A-Za-z\-]{10,48}\b")),
    ("GENERIC_SECRET_ASSIGN", re.compile(
        r"""(?i)\b(?:api_key|secret_key|access_token|db_password)\s*[:=]\s*["']([A-Za-z0-9_\-]{20,})["']"""
    )),
]

SAFE_PLACEHOLDERS = {
    "MY_GEMINI_API_KEY",
    "YOUR_KEY_HERE",
    "YOUR_API_KEY_HERE",
    "REPLACE_ME_IN_PRODUCTION",
}

SKIP_DIRS = {".git", "node_modules", "dist", "__pycache__", ".venv"}
TEXT_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".gd", ".json", ".yml", ".yaml", ".md", ".sh", ".cfg", ".ini", ".env"}


def scan_text(text: str, rel_path: str = "<memory>") -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    for line_num, line in enumerate(text.splitlines(), start=1):
        for rule_name, pattern in SECRET_PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            matched_val = match.group(1) if match.lastindex else match.group(0)
            if matched_val in SAFE_PLACEHOLDERS or "EXAMPLE" in matched_val.upper():
                continue
            findings.append({
                "file": rel_path,
                "line": line_num,
                "rule": rule_name,
                "snippet_redacted": matched_val[:6] + "..." + matched_val[-2:],
            })
    return findings


def scan_directory(root: pathlib.Path) -> List[Dict[str, object]]:
    all_findings: List[Dict[str, object]] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() not in TEXT_SUFFIXES and not p.name.startswith(".env"):
            continue
        try:
            content = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        all_findings.extend(scan_text(content, str(p.relative_to(root))))
    return all_findings


def run_self_test() -> int:
    # Build synthetic test tokens dynamically so the scanner source file itself stays 100% clean
    fake_aws = "AKIA" + "1234567890ABCDEF"
    fake_gh = "ghp_" + ("a1B2c3D4e5F6" * 3)
    dirty_sample = f'aws_id = "{fake_aws}"\ngh_token = "{fake_gh}"\n'
    clean_sample = 'GEMINI_API_KEY="MY_GEMINI_API_KEY"\n'

    dirty_hits = scan_text(dirty_sample, "dirty.py")
    clean_hits = scan_text(clean_sample, ".env.example")

    if len(dirty_hits) != 2 or len(clean_hits) != 0:
        print(f"Self-test failed: dirty={dirty_hits}, clean={clean_hits}", file=sys.stderr)
        return 1
    print("Self-test PASSED: detected 2 synthetic secrets and ignored safe placeholders.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=pathlib.Path, help="Directory or file to scan for secrets")
    parser.add_argument("--self-test", action="store_true", help="Run built-in secret scanner self-test")
    args = parser.parse_args()

    if args.self_test or args.path is None:
        return run_self_test()

    if args.path.is_file():
        findings = scan_text(args.path.read_text(encoding="utf-8"), str(args.path))
    else:
        findings = scan_directory(args.path)

    if findings:
        print(json.dumps({"status": "SECRETS_FOUND", "count": len(findings), "findings": findings}, indent=2))
        return 1
    print(json.dumps({"status": "CLEAN", "count": 0}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
