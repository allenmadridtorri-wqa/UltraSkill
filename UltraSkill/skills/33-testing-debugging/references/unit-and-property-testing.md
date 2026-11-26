# Unit and Property-Based Testing

A single happy-path test (`assert add(2, 2) == 4`) proves almost nothing. High-leverage unit testing combines **Boundary Value Matrices** with **Property-Based Invariant Checks**.

---

## 1. The 5-Point Boundary Value Matrix

For every pure function, test at least these 5 points using table-driven subtests (`self.subTest()`):
1. **Nominal / Happy Path**: Typical mid-range inputs.
2. **Zero / Empty Input**: `0`, `""`, `[]`, `{}`.
3. **Exact Boundary Edges (`N - 1`, `N`, `N + 1`)**: E.g., for a T4 VRAM ceiling of `12,500 MB`, test `12,499.9 MB` (PASS), `12,500.0 MB` (PASS), and `12,500.1 MB` (FAIL). Off-by-one (`<` vs `<=`) bugs live here.
4. **Malformed / Invalid / Negative**: `None`, `-1`, `NaN`, `Inf`, wrong types (must raise a specific `ValueError` or return a structured error).
5. **Idempotency / Repeated Application**: Calling `normalize(normalize(x))` or `apply_migration()` twice yields the exact same state as calling it once.

---

## 2. Property-Based Testing (Without External Libraries)

Even with pure Python `unittest` and a seeded `random.Random(42)`, you can verify universal mathematical and structural **invariants** across 500 generated inputs in `< 20 ms`:

### Four Classic Properties to Assert
1. **Round-Trip (Invertibility) Invariant**:
   - For any valid save payload $P$: `deserialize(serialize(P)) == P`.
   - For any quantized network quaternion $Q$: `angle_between(dequantize(quantize(Q)), Q) <= 0.15°`.
2. **Conservation Invariant**:
   - In any inventory split/merge or currency transfer transaction, `sum(quantities_before) == sum(quantities_after)`.
3. **Monotonicity / Bounds Invariant**:
   - For any weapon damage calculation across arbitrary armor/buff combinations, `damage_dealt >= 0` and never `NaN`.
4. **Oracle Comparison (Fast Optimized vs Simple Reference)**:
   - Compare a complex optimized spatial-hash query against a 5-line brute-force $O(N^2)$ loop over 100 random point clouds to prove 100% identical outputs.
