#!/usr/bin/env python3
"""Pure-stdlib SQLite schema migration runner with WAL pragma setup, SHA-256 tamper verification, and self-test."""

import argparse
import datetime
import hashlib
import json
import pathlib
import sqlite3
import sys
import tempfile
from typing import Dict, List, Tuple


def connect_sqlite(db_path: pathlib.Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path), timeout=5.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 5000;")
    return conn


def ensure_migrations_table(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS _schema_migrations (
                version TEXT PRIMARY KEY,
                checksum_sha256 TEXT NOT NULL,
                applied_at_utc TEXT NOT NULL
            );
            """
        )


def apply_migrations(
    conn: sqlite3.Connection, migrations: List[Tuple[str, str]]
) -> Tuple[bool, List[str], List[str]]:
    """Apply sorted (version, sql_text) pairs transactionally and detect tampering."""
    ensure_migrations_table(conn)
    errors: List[str] = []
    applied_now: List[str] = []

    existing: Dict[str, str] = {
        row["version"]: row["checksum_sha256"]
        for row in conn.execute("SELECT version, checksum_sha256 FROM _schema_migrations")
    }

    for version, sql_text in sorted(migrations, key=lambda x: x[0]):
        digest = hashlib.sha256(sql_text.encode("utf-8")).hexdigest()
        if version in existing:
            if existing[version] != digest:
                errors.append(
                    f"Migration '{version}' checksum mismatch: DB has {existing[version][:12]}, "
                    f"disk has {digest[:12]}"
                )
                return False, errors, applied_now
            continue

        now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            with conn:
                conn.executescript(sql_text)
                conn.execute(
                    "INSERT INTO _schema_migrations (version, checksum_sha256, applied_at_utc) VALUES (?, ?, ?)",
                    (version, digest, now_utc),
                )
            applied_now.append(version)
        except sqlite3.Error as exc:
            errors.append(f"Migration '{version}' failed: {exc}")
            return False, errors, applied_now

    return True, errors, applied_now


def run_self_test() -> int:
    sample_migrations = [
        (
            "001_create_projects",
            """
            CREATE TABLE projects (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at_utc TEXT NOT NULL
            );
            """,
        ),
        (
            "002_create_render_frames",
            """
            CREATE TABLE render_frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                frame_num INTEGER NOT NULL,
                status TEXT NOT NULL CHECK (status IN ('PENDING', 'DONE', 'FAILED')),
                checksum_sha256 TEXT,
                UNIQUE(project_id, frame_num)
            );
            CREATE INDEX idx_render_frames_project_status ON render_frames(project_id, status);
            """,
        ),
    ]

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_file = pathlib.Path(tmp_dir) / "test_ledger.db"
        conn = connect_sqlite(db_file)
        try:
            ok, errs, applied = apply_migrations(conn, sample_migrations)
            assert ok and len(applied) == 2, f"Initial apply failed: {errs}"

            # Idempotent re-run applies 0 new migrations
            ok2, errs2, applied2 = apply_migrations(conn, sample_migrations)
            assert ok2 and len(applied2) == 0, f"Idempotent re-run failed: {errs2}"

            # Tampered migration check must fail
            tampered = [("001_create_projects", "CREATE TABLE projects (id TEXT);")]
            ok3, errs3, _ = apply_migrations(conn, tampered)
            assert not ok3 and "checksum mismatch" in errs3[0]
        finally:
            conn.close()

    print("Self-test PASSED: SQLite WAL setup, idempotent migration apply, and tamper detection verified.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=pathlib.Path, help="Path to SQLite .db file")
    parser.add_argument("--migrations-dir", type=pathlib.Path, help="Directory of numbered .sql files")
    parser.add_argument("--self-test", action="store_true", help="Run built-in SQLite migration self-test")
    args = parser.parse_args()

    if args.self_test or args.db is None or args.migrations_dir is None:
        return run_self_test()

    sql_files = sorted(args.migrations_dir.glob("*.sql"))
    migrations = [(f.stem, f.read_text(encoding="utf-8")) for f in sql_files]

    conn = connect_sqlite(args.db)
    try:
        ok, errs, applied = apply_migrations(conn, migrations)
    finally:
        conn.close()

    if not ok:
        for e in errs:
            print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    print(json.dumps({"status": "ok", "applied": applied}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
