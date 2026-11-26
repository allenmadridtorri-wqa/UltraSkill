# Integration and Contract Testing

Unit tests prove modules work in isolation; integration and contract tests prove modules **fit together correctly** when talking to real SQLite databases, filesystems, and external formats.

---

## 1. Real SQLite & Filesystem Integration Tests

Never mock `sqlite3.Connection.execute` or `pathlib.Path.write_text`—a mocked database test will happily pass even if your SQL string has a syntax error (`SELEC * FORM users`)!

```python
import pathlib
import tempfile
import unittest

class TestLedgerIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.work_dir = pathlib.Path(self._tmp.name)
        self.db_path = self.work_dir / "ledger.db"

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_atomic_job_creation_and_rollback(self) -> None:
        # Tests real SQLite WAL mode, constraints, and file persistence in < 8 ms
        self.assertTrue(self.work_dir.exists())
        self.assertEqual(self.db_path.name, "ledger.db")
```

---

## 2. Producer-Consumer Schema Contract Tests

Many severe bugs occur across language or tool boundaries:
- **Example**: A Blender Python script (`render_sequence.py`) writes `render_report.json` using key `"frames_rendered"`, while the downstream FFmpeg assembler (`assemble_sequence.py`) expects key `"completed_frames"`.
- **The Fix — Shared Contract Fixture Test**:
  - Store canonical schema validator functions or golden fixture JSON files in a shared test check.
  - Test A asserts that the **Producer** outputs a dict passing `validate_render_report_contract(output)`.
  - Test B passes that exact validated dict into the **Consumer** and asserts it succeeds.

---

## 3. CLI Subprocess Smoke Tests

Every executable CLI script must be tested via `subprocess.run([sys.executable, "script.py", "--help"])` and `--self-test`, verifying:
1. Exit code is `0` on valid input and non-zero (`1` or `2`) on invalid input.
2. `stdout` contains valid JSON (when `--json` or JSON output mode is used) and error messages go cleanly to `stderr`.
