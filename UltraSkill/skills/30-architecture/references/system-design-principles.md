# System Design Principles

Well-architected software minimizes the cost of change and isolates pure decision logic from volatile external dependencies (filesystems, networks, databases, 3D engines).

---

## 1. Functional Core, Imperative Shell (Hexagonal / Ports & Adapters Lite)

Divide every application or subsystem into two distinct layers:

1. **The Functional Core (`core/` or `domain/` — 80% of logic, 0% I/O)**:
   - Accepts plain data structures (`dict`, `dataclass`, typed tuples, arrays).
   - Performs validation, math, state transitions, scheduling, and rule evaluation.
   - Returns plain data structures or declarative **Effect Commands** (`WriteFileCommand`, `EmitSignalCommand`).
   - **Zero side effects**: Does not import `requests`, `sqlite3`, `bpy`, or `os.environ`, and does not read the system clock (`datetime.now()` is passed in as an argument `now_utc`).
   - **Payoff**: Runs 500 unit tests in `< 50 ms` on a 4 GB RAM laptop with zero mocks required.
2. **The Imperative Shell (`cli/`, `api/`, `adapters/` — 20% of logic, 100% of I/O)**:
   - Parses CLI arguments or HTTP requests, reads required rows/files from disk, calls the Functional Core, and executes the returned Effect Commands inside a transaction.

---

## 2. Dependency Direction & Acyclic Module Graph

Dependencies must flow strictly **inward toward the Domain Core**:

```text
[CLI / HTTP / UI] ──► [Application Use Cases] ──► [Pure Domain Core]
                               ▲
[SQLite / File / Network] ─────┘ (implements Port interface)
```

- **Hard Rule**: Never allow `core/` to import from `cli/`, `ui/`, or `adapters/`.
- If module `A` imports `B` and `B` imports `A`, extract the shared data contract into a leaf module `types.py` / `contracts.ts` that neither `A` nor `B` mutates.

---

## 3. Locality of Behavior vs Premature DRY

- **Rule of Three**: Do not extract a shared base class or generic helper the first time two functions look superficially similar. Wait until **three concrete use cases** exist so the right abstraction boundary is obvious.
- **Explicit Parameters over Global State**: Pass configuration objects explicitly to constructors or functions rather than reading module-level mutable globals.
