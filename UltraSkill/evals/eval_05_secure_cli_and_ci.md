# Eval 05 — Secure SQLite WAL Application, Test Pyramid & CI Pipeline

## 1. Benchmark Prompt

> "Build a pure-Python render job ledger backed by SQLite that tracks frame completion across Colab sessions. Include path-traversal protection, idempotent job creation, a deterministic `unittest` suite, secret scanning, and a GitHub Actions CI pipeline."

---

## 2. Skills Routed

1. [`skills/30-architecture/SKILL.md`](../skills/30-architecture/SKILL.md) (Functional Core / Imperative Shell separation, idempotency)
2. [`skills/32-web-backend-data/SKILL.md`](../skills/32-web-backend-data/SKILL.md) (SQLite `WAL`, `foreign_keys = ON`, `busy_timeout = 5000`, numbered migrations)
3. [`skills/33-testing-debugging/SKILL.md`](../skills/33-testing-debugging/SKILL.md) (Boundary value tests, real `TemporaryDirectory()` SQLite integration tests, zero `sleep()`)
4. [`skills/34-security/SKILL.md`](../skills/34-security/SKILL.md) (`100%` parameterized `?` SQL, `Path.resolve().is_relative_to()` containment, `secret_scanner.py`)
5. [`skills/35-devops-ci/SKILL.md`](../skills/35-devops-ci/SKILL.md) (GitHub Actions workflow with timeouts, `contents: read`, and `SHA256SUMS.txt`)

---

## 3. Pass / Fail Grading Rubric (100 Points Total — Pass Threshold `>= 90`)

| Check ID | Criterion | Points | Verification Command / Method |
|---|---|---|---|
| `E05-1` | **SQLite WAL & 100% Parameterized SQL**: Connection enables `WAL` + `foreign_keys = ON` + `busy_timeout = 5000`, and every query uses `?` bind tuples | `25` | `python3 skills/32-web-backend-data/scripts/sqlite_migration_runner.py --self-test` |
| `E05-2` | **Path Traversal & Boundary Validation**: `validate_job_spec` blocks `../../` escapes via `resolve().is_relative_to()` and rejects invalid frame ranges | `25` | `python3 examples/06-cli-app/test_render_ledger.py` |
| `E05-3` | **Zero Hardcoded Secrets**: Repository passes `secret_scanner.py` with `0` findings | `25` | `python3 skills/34-security/scripts/secret_scanner.py --path UltraSkill` |
| `E05-4` | **Deterministic Checksum Packaging**: `checksum_manifest.py` generates and verifies `SHA256SUMS.txt` and detects 1-byte tampering | `25` | `python3 skills/35-devops-ci/scripts/checksum_manifest.py --self-test` |
