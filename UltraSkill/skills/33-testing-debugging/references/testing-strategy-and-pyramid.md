# Testing Strategy and the Testing Pyramid

Tests exist to give you **high confidence to ship changes quickly**. A test suite that takes 20 minutes to run, breaks every time you rename a private helper method, or passes when the database query is broken is worse than useless.

---

## 1. The 70 / 20 / 10 Testing Pyramid

| Tier | Share | Scope & Dependencies | Speed per Test | What It Proves |
|---|---|---|---|---|
| **1. Unit & Property Tests** | **70%** | Pure Functional Core (`0` network, `0` disk, `0` database) | `0.05 – 2.0 ms` | Math, state machines, parsers, budget calculators, edge-case boundaries |
| **2. Integration & Contract Tests** | **20%** | Real temp SQLite DB, real temp filesystem, real CLI arg parsing | `5 – 50 ms` | SQL migrations/queries, atomic file writes, JSON schema serialization contracts |
| **3. End-to-End (E2E) Smoke Tests** | **10%** | Full CLI invocation or headless browser/engine boot | `100 – 1,500 ms` | Entrypoints wire all adapters together without missing imports or config errors |

---

## 2. Test Behavior, Never Implementation Details

- **Fragile Test (Bad)**: Asserts that `OrderService.checkout()` called `self._calculate_subtotal()` once and `self._apply_discount_internal()` twice. If you inline `_apply_discount_internal`, the test breaks even though checkout total is 100% correct.
- **Resilient Test (Good)**: Passes an `Order` with 3 items and a `15%` coupon into `calculate_checkout_receipt(order)` and asserts the returned `Receipt` has `total_cents == 4250` and `line_items` count `== 3`.

---

## 3. The 4 Sources of Test Flakiness (And How to Ban Them)

1. **Wall-Clock Time (`datetime.now()`, `time.time()`)**:
   - Pass `now: datetime` or a `clock: Callable[[], float]` parameter into time-dependent functions so tests can jump forward 24 hours in `0.001 ms` without calling `time.sleep()`.
2. **Unseeded Randomness (`random.random()`)**:
   - Always pass an explicit `random.Random(seed)` instance into stochastic simulators (e.g., loot drop tables, Monte Carlo combat balance).
3. **Unordered Sets / Dictionary Iteration Assumptions**:
   - Always sort outputs (`sorted(results)`) or compare as sets when order is not part of the contract.
4. **Shared Filesystem Paths (`/tmp/output.json`)**:
   - Always allocate a unique `tempfile.TemporaryDirectory()` per test method.
