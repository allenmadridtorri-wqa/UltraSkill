#!/usr/bin/env python3
"""Audit a release directory or zip archive for forbidden source/secret files, debug flags, and SHA-256 integrity."""

import argparse
import hashlib
import io
import json
import pathlib
import sys
import zipfile
from typing import Any, Dict, List, Tuple


FORBIDDEN_EXTENSIONS = {".blend", ".blend1", ".psd", ".xcf", ".env", ".pem", ".key"}
FORBIDDEN_DIR_NAMES = {".git", "__pycache__", "node_modules", ".venv"}
FORBIDDEN_DEBUG_TOKENS = ("DEBUG_GOD_MODE = true", "ENABLE_DEV_CHEATS = true")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def audit_zip_bytes(raw_zip: bytes) -> Tuple[bool, List[str], Dict[str, Any]]:
    errors: List[str] = []
    file_hashes: Dict[str, str] = {}

    with zipfile.ZipFile(io.BytesIO(raw_zip), "r") as zf:
        names = zf.namelist()
        if not names:
            return False, ["Release zip is empty."], {}

        has_executable_or_entry = False
        has_license = False

        for name in names:
            if name.endswith("/"):
                continue
            path_obj = pathlib.PurePosixPath(name)

            # Check forbidden directories
            if any(part in FORBIDDEN_DIR_NAMES for part in path_obj.parts):
                errors.append(f"Forbidden directory packaged in release: '{name}'")

            # Check forbidden authoring/secret extensions
            if path_obj.suffix.lower() in FORBIDDEN_EXTENSIONS or path_obj.name == ".env":
                errors.append(f"Forbidden source or secret file packaged in release: '{name}'")

            if path_obj.suffix.lower() in {".exe", ".pck", ".wasm"} or path_obj.name == "index.html":
                has_executable_or_entry = True
            if "LICENSE" in path_obj.name.upper():
                has_license = True

            content = zf.read(name)
            file_hashes[name] = sha256_bytes(content)

            if path_obj.suffix.lower() in {".gd", ".js", ".py", ".cfg", ".ini", ".json"}:
                text = content.decode("utf-8", errors="ignore")
                for token in FORBIDDEN_DEBUG_TOKENS:
                    if token in text:
                        errors.append(f"Active debug cheat flag '{token}' found in '{name}'")

        if not has_executable_or_entry:
            errors.append("Release archive contains no executable (.exe/.pck/.wasm) or index.html entry point.")
        if not has_license:
            errors.append("Release archive is missing THIRD_PARTY_LICENSES.txt or LICENSE.txt.")

    summary = {
        "archive_sha256": sha256_bytes(raw_zip),
        "archive_size_bytes": len(raw_zip),
        "file_count": len(file_hashes),
        "files": file_hashes,
    }
    return len(errors) == 0, errors, summary


def run_self_test() -> int:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("UltraGame.exe", b"MZ-simulated-win64-binary")
        zf.writestr("UltraGame.pck", b"GDPC-simulated-resource-pack")
        zf.writestr("THIRD_PARTY_LICENSES.txt", "Godot Engine - MIT License\n")
    ok, errs, summary = audit_zip_bytes(buf.getvalue())
    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print(
        f"Self-test PASSED: verified {summary['file_count']} release files "
        f"(sha256={summary['archive_sha256'][:16]}...)."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--zip", type=pathlib.Path, help="Path to release .zip archive to audit")
    parser.add_argument("--self-test", action="store_true", help="Run built-in release package self-test")
    args = parser.parse_args()

    if args.self_test or args.zip is None:
        return run_self_test()

    ok, errs, summary = audit_zip_bytes(args.zip.read_bytes())
    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
