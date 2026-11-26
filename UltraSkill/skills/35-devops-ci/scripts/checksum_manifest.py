#!/usr/bin/env python3
"""Generate and verify deterministic SHA256SUMS.txt manifests for release directories or archives."""

import argparse
import hashlib
import pathlib
import sys
import tempfile
from typing import Dict, List, Tuple


def compute_file_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_manifest(target: pathlib.Path) -> Tuple[str, Dict[str, str]]:
    records: Dict[str, str] = {}
    if target.is_file():
        digest = compute_file_sha256(target)
        records[target.name] = digest
    else:
        for p in sorted(target.rglob("*")):
            if not p.is_file() or p.name == "SHA256SUMS.txt":
                continue
            rel = p.relative_to(target).as_posix()
            records[rel] = compute_file_sha256(p)

    lines = [f"{sha}  {rel}" for rel, sha in sorted(records.items())]
    return "\n".join(lines) + "\n", records


def verify_manifest(base_dir: pathlib.Path, manifest_text: str) -> Tuple[bool, List[str]]:
    errors: List[str] = []
    for line_num, raw_line in enumerate(manifest_text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            errors.append(f"Line {line_num}: malformed manifest entry '{line}'")
            continue
        expected_sha, rel_path = parts[0].strip(), parts[1].strip()
        file_path = (base_dir / rel_path).resolve()
        if not file_path.is_relative_to(base_dir.resolve()):
            errors.append(f"Line {line_num}: path traversal blocked on '{rel_path}'")
            continue
        if not file_path.exists():
            errors.append(f"Missing file: '{rel_path}'")
            continue
        actual_sha = compute_file_sha256(file_path)
        if actual_sha != expected_sha:
            errors.append(
                f"Checksum mismatch for '{rel_path}': expected {expected_sha[:12]}..., got {actual_sha[:12]}..."
            )
    return len(errors) == 0, errors


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        (root / "artifact_a.bin").write_bytes(b"ultraskill-release-payload-a")
        (root / "artifact_b.json").write_text('{"version": "1.0.0"}\n', encoding="utf-8")

        manifest_str, records = generate_manifest(root)
        assert len(records) == 2
        ok, errs = verify_manifest(root, manifest_str)
        if not ok:
            print(f"Self-test failed: {errs}", file=sys.stderr)
            return 1

        # Corrupt a file and confirm verification catches it
        (root / "artifact_a.bin").write_bytes(b"tampered-payload")
        ok2, errs2 = verify_manifest(root, manifest_str)
        if ok2 or not errs2:
            print("Self-test failed: tamper went undetected", file=sys.stderr)
            return 1

    print("Self-test PASSED: SHA-256 manifest generation and tamper verification succeeded.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=pathlib.Path, help="Directory or file to checksum")
    parser.add_argument("--verify", type=pathlib.Path, help="Verify an existing SHA256SUMS.txt file against --path")
    parser.add_argument("--output", type=pathlib.Path, help="Optional output file path for SHA256SUMS.txt")
    parser.add_argument("--self-test", action="store_true", help="Run built-in checksum manifest self-test")
    args = parser.parse_args()

    if args.self_test or args.path is None:
        return run_self_test()

    if args.verify:
        base = args.path if args.path.is_dir() else args.path.parent
        ok, errs = verify_manifest(base, args.verify.read_text(encoding="utf-8"))
        if not ok:
            for e in errs:
                print(f"[ERROR] {e}", file=sys.stderr)
            return 1
        print("SHA256SUMS verification PASSED.")
        return 0

    manifest_text, _ = generate_manifest(args.path)
    if args.output:
        args.output.write_text(manifest_text, encoding="utf-8")
    else:
        print(manifest_text, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
