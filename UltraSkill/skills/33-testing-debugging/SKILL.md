---
name: ultraskill-testing-debugging
description: Testing pyramid strategy, fast deterministic unit and property-based tests, integration and contract testing, scientific root-cause debugging, structured tracing, memory/concurrency bug hunting, and blameless postmortems.
---

# 33 — Testing & Root-Cause Debugging

This skill enforces deterministic verification and scientific root-cause debugging across all UltraSkill code: writing fast zero-flake unit and property tests, verifying real database/filesystem integrations, diagnosing bugs systematically instead of guessing, and preventing regressions with postmortems.

## When to use

- Designing a test suite for new or modified code (Python `unittest`, Node `node:test`, C++/Rust test runners).
- Writing unit tests, boundary edge-case matrices, or property-based invariant checks.
- Writing integration tests against real temporary SQLite databases, filesystems, or CLI subprocesses.
- Debugging a failing test, crash, frame hitch, memory leak, race condition, or corrupted render output.
- Writing a blameless technical postmortem after fixing a severe (`S0`/`S1`) defect.

## Inputs

- Target module, CLI script, or bug reproduction report.
- Expected domain invariants and latency/memory constraints (`<= 4 GB RAM`).

## Steps

1. **Balance the Testing Pyramid**:
   - Allocate **`70%` Pure Unit & Property Tests** (`< 1 ms` each, zero I/O), **`20%` Integration & Contract Tests** (real temp SQLite / temp filesystem), and **`10%` End-to-End Smoke Tests** following [references/testing-strategy-and-pyramid.md](references/testing-strategy-and-pyramid.md).
2. **Write Deterministic Unit & Property Tests**:
   - Control all sources of non-determinism (inject clock `now_utc`, fix RNG seeds, ban arbitrary `sleep()` calls) and test boundary + invariant properties using [references/unit-and-property-testing.md](references/unit-and-property-testing.md).
3. **Verify Real Boundaries via Integration & Contract Tests**:
   - Test SQL queries, migrations, and file atomic writes against real `tempfile.TemporaryDirectory()` instances (never mock SQLite with fake string checks) using [references/integration-and-contract-testing.md](references/integration-and-contract-testing.md).
4. **Debug Failures Scientifically (Never Shotgun-Edit)**:
   - Follow the **5-Step Root-Cause Method** (`Reproduce Deterministically -> Isolate via Binary Search -> Hypothesize & Predict -> Prove with Failing Test -> Fix & Verify`) using [references/root-cause-debugging-method.md](references/root-cause-debugging-method.md).
5. **Instrument Tracing & Hunt Memory/Concurrency Bugs**:
   - Use correlation spans ([references/structured-logging-and-tracing.md](references/structured-logging-and-tracing.md)) and isolate leaks/deadlocks/races ([references/memory-and-concurrency-bugs.md](references/memory-and-concurrency-bugs.md)).
6. **Run the Automated Test Runner & Record Postmortems**:
   - Execute the full test suite with [scripts/run_test_suite.py](scripts/run_test_suite.py) and document root causes + regression guards in [templates/POSTMORTEM.md](templates/POSTMORTEM.md).

## Numbers and defaults

| Metric / Rule | Target Value | Hard Constraint |
|---|---|---|
| Full Unit Test Suite Runtime | `<= 2.0 seconds` | Individual unit test `<= 10 ms` |
| Full Integration Suite Runtime | `<= 15.0 seconds` | Runs cleanly offline on a 4 GB RAM laptop |
| Flaky Test Tolerance | **`0.0%`** | Any test that fails 1 in 50 runs is a broken test (usually wall-clock sleep or shared state) |
| Boundary Test Matrix per Function | Minimum `5` cases | Happy path, empty/zero, min/max boundary, malformed/invalid, idempotency |
| Bug Fix Requirement | `1` new failing regression test first | Never merge a bug fix without a test that fails before the fix and passes after |

## Failure modes and fixes

- **Symptom**: Tests pass locally when run individually, but fail randomly when run together in a suite.
  - **Fix**: Hidden shared mutable state (module-level dictionary cache, singleton, environment variable, or shared `/tmp/test.db` path). Give every test method its own isolated `tempfile.TemporaryDirectory()` and fresh object instances in `setUp()`.
- **Symptom**: Everything is mocked (`@patch` on 6 internal methods), so tests pass 100% while the real app crashes on startup with a SQL syntax error.
  - **Fix**: Only mock true external network APIs or expensive hardware unavailable in CI. Never mock your own pure functions, data structures, or local SQLite database.
- **Symptom**: Developer makes 5 speculative edits at once hoping to fix a bug ("shotgun debugging"), introducing 2 new bugs without knowing which edit mattered.
  - **Fix**: Revert all unverified edits (`git checkout -- .`). Reproduce the bug in a minimal test case, form 1 falsifiable hypothesis, and change 1 variable at a time.

## Done check

- [ ] Every pure domain module has unit + boundary tests covering valid, edge, and error paths.
- [ ] Every fixed bug includes a deterministic regression test that fails without the fix.
- [ ] Zero tests rely on `time.sleep()` or external internet connectivity.
- [ ] `python3 skills/33-testing-debugging/scripts/run_test_suite.py --self-test` exits with code `0`.

## Related files

- [references/testing-strategy-and-pyramid.md](references/testing-strategy-and-pyramid.md)
- [references/unit-and-property-testing.md](references/unit-and-property-testing.md)
- [references/integration-and-contract-testing.md](references/integration-and-contract-testing.md)
- [references/root-cause-debugging-method.md](references/root-cause-debugging-method.md)
- [references/structured-logging-and-tracing.md](references/structured-logging-and-tracing.md)
- [references/memory-and-concurrency-bugs.md](references/memory-and-concurrency-bugs.md)
- [templates/POSTMORTEM.md](templates/POSTMORTEM.md)
- [scripts/run_test_suite.py](scripts/run_test_suite.py)
