#!/usr/bin/env python3
"""Package UltraSkill v1.0.0 into a deterministic, bit-reproducible zip archive with SHA-256 verification."""

import argparse
import hashlib
import json
import pathlib
import sys
import zipfile
from typing import Dict, List, Tuple

import validate


PACKAGE_ROOT = pathlib.Path(__file__).resolve().parent.parent
FIXED_ZIP_EPOCH = (2026, 1, 1, 0, 0, 0)


def compute_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def build_reproducible_zip(
    root: pathlib.Path, output_zip: pathlib.Path
) -> Tuple[int, str, Dict[str, str]]:
    manifest = json.loads((root / "MANIFEST.json").read_text(encoding="utf-8"))
    manifest_paths: List[str] = sorted(entry["path"] for entry in manifest["files"])

    output_zip.parent.mkdir(parents=True, exist_ok=True)
    tmp_zip = output_zip.with_suffix(output_zip.suffix + ".tmp")
    file_hashes: Dict[str, str] = {}

    with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for rel_path in manifest_paths:
            full_path = root / rel_path
            raw_bytes = full_path.read_bytes()
            file_hashes[rel_path] = hashlib.sha256(raw_bytes).hexdigest()

            arcname = f"UltraSkill/{rel_path}"
            zinfo = zipfile.ZipInfo(filename=arcname, date_time=FIXED_ZIP_EPOCH)
            zinfo.compress_type = zipfile.ZIP_DEFLATED
            # Set deterministic POSIX permissions (0755 for .py/.sh scripts, 0644 otherwise)
            mode = 0o100755 if full_path.suffix in {".py", ".sh"} else 0o100644
            zinfo.external_attr = mode << 16
            zf.writestr(zinfo, raw_bytes)

    tmp_zip.replace(output_zip)
    zip_sha256 = compute_sha256(output_zip)
    sums_path = output_zip.with_name(output_zip.name + ".sha256")
    sums_path.write_text(f"{zip_sha256}  {output_zip.name}\n", encoding="utf-8")

    return len(manifest_paths), zip_sha256, file_hashes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=PACKAGE_ROOT.parent / "UltraSkill-1.0.0.zip",
        help="Output path for the reproducible UltraSkill zip package",
    )
    parser.add_argument(
        "--skip-validate",
        action="store_true",
        help="Skip running validate.py before packaging",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Validate package integrity and test deterministic zip creation in a temp path",
    )
    args = parser.parse_args()

    if not args.skip_validate:
        rc = validate.main(["--root", str(PACKAGE_ROOT)])
        if rc != 0:
            return rc

    count, zip_sha256, _ = build_reproducible_zip(PACKAGE_ROOT, args.output)
    size_kb = round(args.output.stat().st_size / 1024.0, 2)
    print(
        json.dumps(
            {
                "status": "PACKAGED",
                "output_zip": str(args.output),
                "files_packaged": count,
                "size_kb": size_kb,
                "sha256": zip_sha256,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
