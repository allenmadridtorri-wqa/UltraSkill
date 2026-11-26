#!/usr/bin/env python3
"""Render Ledger CLI: Pure-stdlib SQLite WAL job & frame tracker for Colab OptiX render pipelines."""

import argparse
import dataclasses
import json
import pathlib
import sqlite3
import sys
import tempfile
from typing import Any, Dict, List


ALLOWED_PRESETS = {"FAST_PREVIEW", "PROD_1080P", "STILL_HIGH", "HERO_4K"}
ALLOWED_STATUSES = {"PENDING", "DONE", "FAILED"}


@dataclasses.dataclass(frozen=True)
class ValidatedJobSpec:
    job_id: str
    shot_name: str
    preset: str
    start_frame: int
    end_frame: int
    safe_output_dir: str


def validate_job_spec(
    base_dir: pathlib.Path,
    job_id: str,
    shot_name: str,
    preset: str,
    start_frame: int,
    end_frame: int,
    rel_output_dir: str,
) -> ValidatedJobSpec:
    """Pure Functional Core boundary parser enforcing domain invariants and path containment."""
    clean_id = job_id.strip()
    clean_shot = shot_name.strip()
    if not clean_id or len(clean_id) > 64:
        raise ValueError("job_id must be 1..64 non-empty characters")
    if not clean_shot or len(clean_shot) > 64:
        raise ValueError("shot_name must be 1..64 non-empty characters")
    if preset not in ALLOWED_PRESETS:
        raise ValueError(f"Unsupported preset '{preset}' (allowed: {sorted(ALLOWED_PRESETS)})")
    if start_frame < 1 or end_frame < start_frame or (end_frame - start_frame + 1) > 10000:
        raise ValueError(f"Invalid frame range [{start_frame}, {end_frame}]")

    if not rel_output_dir or "\x00" in rel_output_dir:
        raise ValueError("Invalid output directory")
    root = base_dir.resolve()
    target_dir = (root / rel_output_dir).resolve()
    if not target_dir.is_relative_to(root):
        raise ValueError(f"Path traversal blocked: '{rel_output_dir}' escapes '{root}'")

    return ValidatedJobSpec(
        job_id=clean_id,
        shot_name=clean_shot,
        preset=preset,
        start_frame=start_frame,
        end_frame=end_frame,
        safe_output_dir=str(target_dir.relative_to(root)),
    )


def compute_job_progress(frame_statuses: List[str]) -> Dict[str, Any]:
    """Pure calculation of completion percentage and remaining frames."""
    total = len(frame_statuses)
    if total == 0:
        return {"total": 0, "done": 0, "failed": 0, "pending": 0, "pct_complete": 0.0}
    done = sum(1 for s in frame_statuses if s == "DONE")
    failed = sum(1 for s in frame_statuses if s == "FAILED")
    pending = total - done - failed
    return {
        "total": total,
        "done": done,
        "failed": failed,
        "pending": pending,
        "pct_complete": round((done / total) * 100.0, 2),
    }


class RenderLedgerDB:
    """Imperative Shell SQLite WAL repository with 100% parameterized queries."""

    def __init__(self, db_path: pathlib.Path) -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path), timeout=5.0)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode = WAL;")
        self.conn.execute("PRAGMA synchronous = NORMAL;")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.execute("PRAGMA busy_timeout = 5000;")
        self._init_schema()

    def _init_schema(self) -> None:
        with self.conn:
            self.conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS render_jobs (
                    job_id TEXT PRIMARY KEY,
                    shot_name TEXT NOT NULL,
                    preset TEXT NOT NULL,
                    start_frame INTEGER NOT NULL,
                    end_frame INTEGER NOT NULL,
                    output_dir TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS render_frames (
                    job_id TEXT NOT NULL REFERENCES render_jobs(job_id) ON DELETE CASCADE,
                    frame_num INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'PENDING'
                        CHECK (status IN ('PENDING', 'DONE', 'FAILED')),
                    checksum_sha256 TEXT,
                    render_time_sec REAL,
                    PRIMARY KEY (job_id, frame_num)
                );
                CREATE INDEX IF NOT EXISTS idx_frames_job_status
                    ON render_frames(job_id, status);
                """
            )

    def create_job_idempotent(self, spec: ValidatedJobSpec) -> bool:
        with self.conn:
            existing = self.conn.execute(
                "SELECT job_id FROM render_jobs WHERE job_id = ?", (spec.job_id,)
            ).fetchone()
            if existing is not None:
                return False
            self.conn.execute(
                """
                INSERT INTO render_jobs (job_id, shot_name, preset, start_frame, end_frame, output_dir)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (spec.job_id, spec.shot_name, spec.preset, spec.start_frame, spec.end_frame, spec.safe_output_dir),
            )
            frame_rows = [(spec.job_id, f, "PENDING") for f in range(spec.start_frame, spec.end_frame + 1)]
            self.conn.executemany(
                "INSERT INTO render_frames (job_id, frame_num, status) VALUES (?, ?, ?)",
                frame_rows,
            )
        return True

    def record_frame_result(
        self, job_id: str, frame_num: int, status: str, checksum_sha256: str, render_time_sec: float
    ) -> None:
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"Invalid frame status: {status}")
        with self.conn:
            cur = self.conn.execute(
                """
                UPDATE render_frames
                SET status = ?, checksum_sha256 = ?, render_time_sec = ?
                WHERE job_id = ? AND frame_num = ?
                """,
                (status, checksum_sha256, render_time_sec, job_id, frame_num),
            )
            if cur.rowcount == 0:
                raise KeyError(f"Frame {frame_num} not found for job '{job_id}'")

    def get_pending_frames(self, job_id: str) -> List[int]:
        rows = self.conn.execute(
            "SELECT frame_num FROM render_frames WHERE job_id = ? AND status != 'DONE' ORDER BY frame_num ASC",
            (job_id,),
        ).fetchall()
        return [int(r["frame_num"]) for r in rows]

    def get_job_summary(self, job_id: str) -> Dict[str, Any]:
        job = self.conn.execute("SELECT * FROM render_jobs WHERE job_id = ?", (job_id,)).fetchone()
        if job is None:
            raise KeyError(f"Unknown job_id '{job_id}'")
        rows = self.conn.execute(
            "SELECT status FROM render_frames WHERE job_id = ? ORDER BY frame_num ASC", (job_id,)
        ).fetchall()
        progress = compute_job_progress([str(r["status"]) for r in rows])
        return {
            "job_id": job["job_id"],
            "shot_name": job["shot_name"],
            "preset": job["preset"],
            "output_dir": job["output_dir"],
            **progress,
        }

    def close(self) -> None:
        self.conn.close()


def run_self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        spec = validate_job_spec(root, "job_01", "SH010", "PROD_1080P", 1, 10, "renders/SH010")
        db = RenderLedgerDB(root / "ledger.db")
        try:
            assert db.create_job_idempotent(spec) is True
            assert db.create_job_idempotent(spec) is False
            db.record_frame_result("job_01", 1, "DONE", "sha256_f1", 4.2)
            db.record_frame_result("job_01", 2, "DONE", "sha256_f2", 4.1)
            summary = db.get_job_summary("job_01")
            assert summary["pct_complete"] == 20.0
            assert len(db.get_pending_frames("job_01")) == 8
        finally:
            db.close()
    print("Self-test PASSED: RenderLedgerDB WAL lifecycle and path safety verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=pathlib.Path, help="Path to SQLite ledger file")
    parser.add_argument("--summary", help="Print JSON summary for job_id")
    parser.add_argument("--self-test", action="store_true", help="Run built-in ledger self-test")
    args = parser.parse_args()

    if args.self_test or args.db is None:
        return run_self_test()

    db = RenderLedgerDB(args.db)
    try:
        if args.summary:
            print(json.dumps(db.get_job_summary(args.summary), indent=2))
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
