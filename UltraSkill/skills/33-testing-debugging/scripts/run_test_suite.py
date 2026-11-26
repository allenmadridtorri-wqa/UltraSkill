#!/usr/bin/env python3
"""Discover and execute Python unittest suites and script --self-test checks with timing and JSON summary."""

import argparse
import json
import pathlib
import subprocess
import sys
import time
import unittest
from typing import Any, Dict, List


class BuiltinSelfTests(unittest.TestCase):
    """Built-in sanity tests verifying deterministic boundary and invariant properties."""

    def test_openexr_magic_and_size_guard(self) -> None:
        exr_magic = b"\x76\x2f\x31\x01"
        valid_stub = exr_magic + (b"\x00" * 4096)
        truncated_stub = exr_magic + (b"\x00" * 16)
        corrupt_stub = b"PNG\r" + (b"\x00" * 4096)

        def is_valid_exr(buf: bytes, min_bytes: int = 1024) -> bool:
            return len(buf) >= min_bytes and buf[:4] == exr_magic

        self.assertTrue(is_valid_exr(valid_stub))
        self.assertFalse(is_valid_exr(truncated_stub))
        self.assertFalse(is_valid_exr(corrupt_stub))

    def test_conservation_of_currency_transfer(self) -> None:
        balances = {"alice": 500, "bob": 300}
        total_before = sum(balances.values())
        transfer = 175
        balances["alice"] -= transfer
        balances["bob"] += transfer
        self.assertEqual(sum(balances.values()), total_before)
        self.assertTrue(all(v >= 0 for v in balances.values()))


def run_unittest_discovery(start_dir: pathlib.Path, pattern: str = "test*.py") -> Dict[str, Any]:
    t0 = time.perf_counter()
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(start_dir), pattern=pattern)
    runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=2)
    result = runner.run(suite)
    elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
    return {
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "elapsed_ms": elapsed_ms,
        "passed": result.wasSuccessful(),
    }


def run_script_self_tests(scripts: List[pathlib.Path]) -> Dict[str, Any]:
    results = []
    all_passed = True
    for script in scripts:
        t0 = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, str(script), "--self-test"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        ok = proc.returncode == 0
        if not ok:
            all_passed = False
        results.append({
            "script": str(script),
            "passed": ok,
            "elapsed_ms": elapsed_ms,
            "output": (proc.stdout + proc.stderr).strip(),
        })
    return {"all_passed": all_passed, "scripts": results}


def run_self_test() -> int:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BuiltinSelfTests)
    res = unittest.TextTestRunner(stream=sys.stderr, verbosity=1).run(suite)
    if not res.wasSuccessful():
        return 1
    print(f"Self-test PASSED: {res.testsRun} deterministic invariant tests verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", type=pathlib.Path, help="Directory to discover test*.py files")
    parser.add_argument("--pattern", default="test*.py", help="Unittest filename glob pattern")
    parser.add_argument("--self-test", action="store_true", help="Run built-in test runner self-test")
    args = parser.parse_args()

    if args.self_test or args.dir is None:
        return run_self_test()

    summary = run_unittest_discovery(args.dir, args.pattern)
    print(json.dumps(summary, indent=2))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
