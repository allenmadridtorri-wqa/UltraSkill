# The 5-Pass Code Review Method

Reviewing code top-to-bottom in a single linear pass mixes high-severity architectural and security flaws with trivial formatting nits. Execute code reviews in **five focused passes**.

---

## Pass 1: Architecture, Scope & Hardware Fit (20% of time)
- Does this change solve the actual requirement with minimal added complexity?
- Are pure domain rules separated from I/O adapters (**Functional Core, Imperative Shell**)?
- **Hardware Fit**: Will this run cleanly on the user's **4 GB RAM laptop with 1 GB Intel UHD graphics** (`LOW` preset), or is heavy rendering/compilation properly routed to **Colab OptiX GPU** / **GitHub Actions**?

## Pass 2: Security & Data Integrity (25% of time)
- Are all external inputs parsed and validated at the ingress boundary?
- Are 100% of SQL queries parameterized (`?`) and subprocess calls using argument arrays (`shell=False`)?
- Are file paths constrained via `resolve().is_relative_to(base_dir)`?
- Are critical file writes atomic (`.tmp -> .bak -> replace`) so crashes mid-write never corrupt user saves or render ledgers?

## Pass 3: Correctness, Edge Cases & Failure Modes (25% of time)
- What happens on empty input (`[]`, `""`, `0`), boundary limits (`N`, `N+1`), negative values, or `NaN`/`Inf`?
- Do all external I/O calls specify explicit timeouts and resource cleanup (`with` / `try..finally` / `exit()` hooks)?
- In concurrent or async code, are shared structures locked or message-passed via bounded queues?

## Pass 4: Performance & Memory Budgets (15% of time)
- Are there hidden $O(N^2)$ loops (linear searches or database queries inside a loop) or unbounded `file.read()` calls?
- In 60 FPS game/Three.js loops, are there per-frame heap allocations (`new Vector3()`, `.map()`, `instantiate()`) or unbatched draw calls?

## Pass 5: Tests & Maintainability (15% of time)
- Do unit/integration tests verify both happy paths and failure/boundary paths without `time.sleep()` flakiness?
- Would a new engineer understand this module in 2 minutes without reading the commit author's mind?
