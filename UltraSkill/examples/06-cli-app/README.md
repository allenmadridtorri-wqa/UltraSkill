# Example 06 — Pure-Stdlib Render Ledger CLI & SQLite Application (`README.md`)

This golden-master worked example demonstrates the **Coding Pillar (`30`–`36`)** in action: a production-hardened, pure-Python 3 (`0` external pip packages) command-line application and library (`render_ledger.py`) backed by SQLite in `WAL` mode, paired with a comprehensive deterministic unit & integration test suite (`test_render_ledger.py`).

---

## 1. Architecture & Security Highlights

1. **Functional Core, Imperative Shell (`skills/30-architecture`)**:
   - Pure domain validation (`validate_job_spec`, `compute_job_progress`) is 100% decoupled from SQLite persistence (`RenderLedgerDB`) and the `argparse` CLI entrypoint.
2. **SQLite WAL & Transactional Integrity (`skills/31-languages`, `skills/32-web-backend-data`)**:
   - Enforces `PRAGMA journal_mode=WAL;`, `PRAGMA foreign_keys=ON;`, `PRAGMA busy_timeout=5000;`, and `100%` parameterized SQL queries (`?`).
3. **Defensive Security (`skills/34-security`)**:
   - Enforces `Path.resolve().is_relative_to(base_dir)` path containment on all frame output directories, preventing path traversal (`../../etc/passwd`).
   - Enforces idempotency keys on job creation so network/Colab retries never create duplicate render jobs.
4. **Deterministic Zero-Flake Test Suite (`skills/33-testing-debugging`)**:
   - `python3 UltraSkill/examples/06-cli-app/test_render_ledger.py` runs 7 unit, boundary, security, and SQLite integration tests in `< 40 ms` using `tempfile.TemporaryDirectory()`.

---

## 2. Quick CLI Usage

```bash
# Run built-in self-test
python3 UltraSkill/examples/06-cli-app/render_ledger.py --self-test

# Run full unit & integration test suite
python3 UltraSkill/examples/06-cli-app/test_render_ledger.py
```
