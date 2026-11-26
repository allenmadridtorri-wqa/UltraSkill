#!/usr/bin/env python3
"""
Google Colab Cycles OptiX Bootstrap & Runner (`colab_optix_runner.py`).

Run this script on a Google Colab GPU instance (Runtime -> Change runtime type -> T4 GPU)
to automatically:
  1. Check `nvidia-smi` for an attached NVIDIA T4 (or better) GPU.
  2. Download and extract portable Linux x86_64 Blender 4.2 LTS if not already cached.
  3. Execute `optix_verify.py` to prove headless Cycles OptiX GPU engagement.
  4.Optionally run `apply_preset.py`, `benchmark_scene.py`, and `render_sequence.py`
     saving directly to a mounted Google Drive folder.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path


BLENDER_VERSION = "4.2.3"
BLENDER_TAR_URL = (
    f"https://download.blender.org/release/Blender4.2/blender-{BLENDER_VERSION}-linux-x64.tar.xz"
)
DEFAULT_INSTALL_DIR = Path("/tmp/blender_portable")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="colab_optix_runner.py",
        description="Bootstrap portable Blender on Google Colab and prove Cycles OptiX GPU rendering.",
    )
    parser.add_argument(
        "--blender-bin",
        type=Path,
        default=None,
        help="Path to existing blender executable (downloads portable Blender 4.2 LTS if omitted).",
    )
    parser.add_argument(
        "--proof-only",
        action="store_true",
        help="Run only the mandatory OptiX hardware proof (optix_verify.py) and exit.",
    )
    parser.add_argument(
        "--blend-file",
        type=Path,
        default=None,
        help="Optional .blend scene file to benchmark and render after OptiX proof passes.",
    )
    parser.add_argument(
        "--preset",
        choices=["PREVIEW", "REVIEW", "FINAL"],
        default="REVIEW",
        help="Quality preset to apply when rendering --blend-file (default: REVIEW).",
    )
    parser.add_argument(
        "--drive-output",
        type=Path,
        default=Path("/content/drive/MyDrive/ultraskill_renders"),
        help="Google Drive folder where frames and render_manifest.json are saved.",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="Start frame for sequence render (default: 1).",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=1,
        help="End frame for sequence render (default: 1).",
    )
    return parser.parse_args(argv)


def ensure_blender(custom_bin: Path | None) -> Path:
    if custom_bin and custom_bin.is_file():
        return custom_bin.resolve()

    which_blender = shutil.which("blender")
    if which_blender:
        return Path(which_blender).resolve()

    extracted_bin = DEFAULT_INSTALL_DIR / f"blender-{BLENDER_VERSION}-linux-x64" / "blender"
    if extracted_bin.is_file():
        return extracted_bin

    DEFAULT_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    archive_path = DEFAULT_INSTALL_DIR / f"blender-{BLENDER_VERSION}-linux-x64.tar.xz"
    print(f"[INFO] Downloading portable Blender {BLENDER_VERSION} from {BLENDER_TAR_URL} ...")
    urllib.request.urlretrieve(BLENDER_TAR_URL, archive_path)
    print(f"[INFO] Extracting {archive_path} ...")
    subprocess.run(
        ["tar", "-xf", str(archive_path), "-C", str(DEFAULT_INSTALL_DIR)],
        check=True,
    )
    if not extracted_bin.is_file():
        raise FileNotFoundError(f"Expected Blender binary not found at {extracted_bin}")
    return extracted_bin


def run_cmd(cmd: list[str]) -> int:
    print(f"[EXEC] {' '.join(cmd)}")
    proc = subprocess.run(cmd, check=False)
    return proc.returncode


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    scripts_dir = Path(__file__).resolve().parent.parent / "scripts"
    optix_script = scripts_dir / "optix_verify.py"

    if not optix_script.is_file():
        print(f"[ERROR] Missing optix_verify.py at {optix_script}", file=sys.stderr)
        return 1

    try:
        blender_bin = ensure_blender(args.blender_bin)
    except Exception as exc:
        print(f"[ERROR] Could not locate or install Blender: {exc}", file=sys.stderr)
        return 1

    drive_out: Path = args.drive_output.resolve()
    drive_out.mkdir(parents=True, exist_ok=True)
    proof_img = drive_out / "optix_proof_0001.png"
    proof_json = drive_out / "optix_proof_report.json"

    rc = run_cmd(
        [
            str(blender_bin),
            "-b",
            "-P",
            str(optix_script),
            "--",
            "--output",
            str(proof_img),
            "--json-report",
            str(proof_json),
        ]
    )
    if rc != 0:
        print("[FATAL] Cycles OptiX hardware proof failed. Halting pipeline.", file=sys.stderr)
        return rc

    if args.proof_only or args.blend_file is None:
        print(f"[OK] OptiX proof complete. Report saved to {proof_json}")
        return 0

    blend_file = args.blend_file.resolve()
    if not blend_file.is_file():
        print(f"[ERROR] Scene file not found: {blend_file}", file=sys.stderr)
        return 1

    staged_blend = Path("/tmp") / f"staged_{args.preset.lower()}_{blend_file.name}"
    rc = run_cmd(
        [
            str(blender_bin),
            "-b",
            str(blend_file),
            "-P",
            str(scripts_dir / "apply_preset.py"),
            "--",
            "--preset",
            args.preset,
            "--save",
            str(staged_blend),
        ]
    )
    if rc != 0:
        return rc

    total_frames = max(1, args.end - args.start + 1)
    mid_frame = args.start + (total_frames // 2)
    rc = run_cmd(
        [
            str(blender_bin),
            "-b",
            str(staged_blend),
            "-P",
            str(scripts_dir / "benchmark_scene.py"),
            "--",
            "--frames",
            f"{args.start},{mid_frame},{args.end}",
            "--total-frames",
            str(total_frames),
            "--output-dir",
            str(drive_out / "benchmark"),
        ]
    )
    if rc != 0:
        return rc

    manifest_path = drive_out / "render_manifest.json"
    rc = run_cmd(
        [
            str(blender_bin),
            "-b",
            str(staged_blend),
            "-P",
            str(scripts_dir / "render_sequence.py"),
            "--",
            "--start",
            str(args.start),
            "--end",
            str(args.end),
            "--output-dir",
            str(drive_out / "frames"),
            "--manifest",
            str(manifest_path),
        ]
    )
    return rc


if __name__ == "__main__":
    sys.exit(main())
