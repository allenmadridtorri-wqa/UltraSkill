# Refactoring Legacy Code Safely

Never rewrite a working 2,000-line legacy module from scratch without a test harness ("big-bang rewrites" almost always re-introduce subtle edge-case bugs that the messy legacy code handled years ago).

---

## 1. The 5-Step Safe Refactoring Loop

### Step 1: Write Characterization (Golden Master) Tests First
Before changing a single line of legacy logic:
- Feed the existing function/CLI a representative matrix of 10–30 real inputs (including weird edge cases).
- Record its exact current outputs (return values, written files, stdout) and assert them in an automated test.
- This creates a **safety net**: if your refactoring accidentally changes behavior, the characterization test fails immediately.

### Step 2: Identify and Extract a Seam
Find where the monolithic function mixes **I/O** (reading a file, querying a global singleton, calling `datetime.now()`) with **Calculation**:
- Pass the I/O result in as a function parameter with a default fallback (`def process_invoice(data, now_utc=None):`).

### Step 3: Guard Clauses to Flatten Arrow Code
Replace 6-level deep nested `if/else` pyramids with early-return guard clauses:
```python
# Before: deep nesting
if user is not None:
    if user.is_active:
        if order.items:
            return compute_total(order)

# After: flat guard clauses
if user is None or not user.is_active or not order.items:
    return 0.0
return compute_total(order)
```

### Step 4: Strangler Fig Migration
Route one sub-feature at a time through the new clean module while keeping the old entrypoint interface intact. Delete dead legacy branches as soon as 100% of callers are routed through the new path.

### Step 5: Never Mix Refactoring and Feature Changes in One Commit
- **Commit 1**: Pure structural refactoring (behavior 100% identical, all existing tests pass).
- **Commit 2**: New feature or bug fix + new unit test.
