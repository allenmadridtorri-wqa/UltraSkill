#!/usr/bin/env python3
"""Analyze frame-time CSV/JSON logs, compute p50/p95/p99 percentiles, diagnose CPU vs GPU bounds, and verify budgets."""

import argparse
import csv
import io
import json
import math
import pathlib
import sys
from typing import Any, Dict, List


PRESET_BUDGETS: Dict[str, Dict[str, float]] = {
    "LOW": {"p95_ms": 16.67, "p99_ms": 22.0, "draw_calls": 150, "vram_mb": 512.0},
    "MEDIUM": {"p95_ms": 16.67, "p99_ms": 19.0, "draw_calls": 400, "vram_mb": 1200.0},
    "HIGH": {"p95_ms": 16.67, "p99_ms": 17.5, "draw_calls": 1200, "vram_mb": 3000.0},
}


def percentile(sorted_vals: List[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    idx = min(len(sorted_vals) - 1, max(0, math.ceil((pct / 100.0) * len(sorted_vals)) - 1))
    return round(sorted_vals[idx], 3)


def analyze_samples(rows: List[Dict[str, Any]], preset: str = "LOW") -> Dict[str, Any]:
    budget = PRESET_BUDGETS.get(preset.upper(), PRESET_BUDGETS["LOW"])
    frame_times = sorted(float(r["frame_ms"]) for r in rows)
    cpu_times = sorted(float(r.get("cpu_ms", r["frame_ms"])) for r in rows)
    gpu_times = sorted(float(r.get("gpu_ms", r["frame_ms"])) for r in rows)
    draw_calls = max(int(r.get("draw_calls", 0)) for r in rows) if rows else 0
    vram_mb = max(float(r.get("vram_mb", 0.0)) for r in rows) if rows else 0.0

    p50 = percentile(frame_times, 50)
    p95 = percentile(frame_times, 95)
    p99 = percentile(frame_times, 99)
    cpu_p95 = percentile(cpu_times, 95)
    gpu_p95 = percentile(gpu_times, 95)

    dropped_60fps = sum(1 for t in frame_times if t > 16.67)
    hitches_33ms = sum(1 for t in frame_times if t > 33.33)

    if gpu_p95 > cpu_p95 * 1.15:
        bottleneck = "GPU_BOUND"
    elif cpu_p95 > gpu_p95 * 1.15:
        bottleneck = "CPU_BOUND"
    else:
        bottleneck = "BALANCED"

    violations: List[str] = []
    if p95 > budget["p95_ms"]:
        violations.append(f"p95 frame time {p95} ms exceeds {budget['p95_ms']} ms")
    if p99 > budget["p99_ms"]:
        violations.append(f"p99 frame time {p99} ms exceeds {budget['p99_ms']} ms")
    if draw_calls > budget["draw_calls"]:
        violations.append(f"Peak draw_calls {draw_calls} exceeds {int(budget['draw_calls'])}")
    if vram_mb > budget["vram_mb"]:
        violations.append(f"Peak vram_mb {vram_mb} MB exceeds {budget['vram_mb']} MB")

    return {
        "preset": preset.upper(),
        "frame_count": len(rows),
        "p50_ms": p50,
        "p95_ms": p95,
        "p99_ms": p99,
        "effective_fps_p50": round(1000.0 / p50, 1) if p50 > 0 else 0.0,
        "one_percent_low_fps": round(1000.0 / p99, 1) if p99 > 0 else 0.0,
        "cpu_p95_ms": cpu_p95,
        "gpu_p95_ms": gpu_p95,
        "primary_bottleneck": bottleneck,
        "dropped_frames_over_16_67ms": dropped_60fps,
        "severe_hitches_over_33_33ms": hitches_33ms,
        "peak_draw_calls": draw_calls,
        "peak_vram_mb": vram_mb,
        "passes_budget": len(violations) == 0,
        "violations": violations,
    }


def run_self_test() -> int:
    synthetic_rows = []
    for i in range(120):
        # Smooth 60 FPS telemetry under LOW budget
        synthetic_rows.append({
            "frame_ms": 12.2 + (i % 5) * 0.6,
            "cpu_ms": 8.4 + (i % 4) * 0.4,
            "gpu_ms": 11.8 + (i % 5) * 0.6,
            "draw_calls": 118,
            "vram_mb": 384.0,
        })
    report = analyze_samples(synthetic_rows, preset="LOW")
    if not report["passes_budget"]:
        print(f"Self-test failed: {report}", file=sys.stderr)
        return 1
    print(
        f"Self-test PASSED: p50={report['p50_ms']}ms, p95={report['p95_ms']}ms, "
        f"p99={report['p99_ms']}ms ({report['primary_bottleneck']})."
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, help="Input CSV or JSON telemetry file")
    parser.add_argument("--preset", default="LOW", choices=["LOW", "MEDIUM", "HIGH"], help="Budget preset")
    parser.add_argument("--self-test", action="store_true", help="Run built-in frame analysis self-test")
    args = parser.parse_args()

    if args.self_test or args.input is None:
        return run_self_test()

    raw = args.input.read_text(encoding="utf-8")
    if args.input.suffix.lower() == ".json":
        rows = json.loads(raw)
    else:
        rows = list(csv.DictReader(io.StringIO(raw)))

    rep = analyze_samples(rows, preset=args.preset)
    print(json.dumps(rep, indent=2))
    return 0 if rep["passes_budget"] else 1


if __name__ == "__main__":
    sys.exit(main())
