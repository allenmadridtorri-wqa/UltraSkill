#!/usr/bin/env python3
"""Deterministic unit, boundary, security, and SQLite integration test suite for Example 06 (render_ledger.py)."""

import argparse
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from render_ledger import RenderLedgerDB, compute_job_progress, validate_job_spec  # noqa: E402


class TestRenderLedger(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base_dir = pathlib.Path(self._tmp.name)
        self.db = RenderLedgerDB(self.base_dir / "test_ledger.db")

    def tearDown(self) -> None:
        self.db.close()
        self._tmp.cleanup()

    def test_valid_job_creation_and_idempotency(self) -> None:
        spec = validate_job_spec(
            self.base_dir, "job_alpha", "SH010", "PROD_1080P", 1, 24, "renders/SH010"
        )
        created_first = self.db.create_job_idempotent(spec)
        created_second = self.db.create_job_idempotent(spec)
        self.assertTrue(created_first)
        self.assertFalse(created_second)

        summary = self.db.get_job_summary("job_alpha")
        self.assertEqual(summary["total"], 24)
        self.assertEqual(summary["pending"], 24)
        self.assertEqual(summary["pct_complete"], 0.0)

    def test_path_traversal_is_blocked(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_job_spec(
                self.base_dir, "job_evil", "SH010", "PROD_1080P", 1, 5, "../../etc/cron.d"
            )
        self.assertIn("Path traversal blocked", str(ctx.exception))

    def test_invalid_frame_ranges_and_presets_rejected(self) -> None:
        for bad_start, bad_end in [(0, 10), (10, 5), (1, 20000)]:
            with self.subTest(start=bad_start, end=bad_end):
                with self.assertRaises(ValueError):
                    validate_job_spec(
                        self.base_dir, "job_bad", "SH010", "PROD_1080P", bad_start, bad_end, "renders/out"
                    )
        with self.assertRaises(ValueError):
            validate_job_spec(
                self.base_dir, "job_bad_preset", "SH010", "ULTRA_8K_CPU", 1, 10, "renders/out"
            )

    def test_frame_completion_and_resume_queue(self) -> None:
        spec = validate_job_spec(
            self.base_dir, "job_resume", "SH020", "STILL_HIGH", 101, 105, "renders/SH020"
        )
        self.db.create_job_idempotent(spec)
        self.db.record_frame_result("job_resume", 101, "DONE", "sha_101", 3.5)
        self.db.record_frame_result("job_resume", 103, "DONE", "sha_103", 3.6)
        self.db.record_frame_result("job_resume", 104, "FAILED", "", 0.2)

        pending = self.db.get_pending_frames("job_resume")
        self.assertEqual(pending, [102, 104, 105])

        summary = self.db.get_job_summary("job_resume")
        self.assertEqual(summary["done"], 2)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["pending"], 2)
        self.assertEqual(summary["pct_complete"], 40.0)

    def test_pure_progress_calculation_boundaries(self) -> None:
        self.assertEqual(compute_job_progress([])["pct_complete"], 0.0)
        self.assertEqual(compute_job_progress(["DONE", "DONE"])["pct_complete"], 100.0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run full unit and integration test suite")
    parser.parse_args()

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestRenderLedger)
    result = unittest.TextTestRunner(stream=sys.stderr, verbosity=2).run(suite)
    if not result.wasSuccessful():
        return 1
    print(f"All {result.testsRun} RenderLedger tests PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
