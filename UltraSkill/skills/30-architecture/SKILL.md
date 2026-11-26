---
name: ultraskill-software-architecture
description: Pragmatic system design, architecture decision records (ADRs), design patterns without over-engineering, algorithmic complexity and data structures, API contract design, error handling, concurrency, and legacy refactoring.
---

# 30 — Software Architecture & System Design

This skill governs software architecture across the Coding pillar (and the shared infrastructure of 3D and Game pipelines): designing clean module boundaries, choosing optimal data structures, defining backwards-compatible API contracts, handling partial failures gracefully, and refactoring legacy code safely without breaking running systems.

## When to use

- Designing a new application, CLI tool, service, data pipeline, or engine module before writing code.
- Writing an Architecture Decision Record (`ADR`) to document trade-offs between competing designs.
- Selecting data structures and verifying algorithmic time (`O(...)`) and memory complexity under low-spec (`4 GB RAM`) constraints.
- Defining public API schemas, CLI flags, file formats, or RPC contracts.
- Designing error boundaries, retry/backoff policies, circuit breakers, or concurrent worker pools.
- Refactoring tangled legacy code incrementally via the Strangler Fig and Characterization Test patterns.

## Inputs

- Functional requirements, throughput/latency targets, and hardware memory constraints (`<= 4 GB RAM` local baseline).
- Existing codebase layout or upstream/downstream data schemas.

## Steps

1. **Decompose System Boundaries (Functional Core, Imperative Shell)**:
   - Separate pure deterministic business logic (zero I/O, trivially unit-testable) from thin outer I/O adapters (CLI, HTTP, filesystem, database, GPU) following [references/system-design-principles.md](references/system-design-principles.md).
2. **Record Non-Trivial Trade-Offs in an ADR**:
   - Whenever choosing a database, concurrency model, or serialization format, capture context, rejected alternatives, and failure blast radius using [templates/ADR_TEMPLATE.md](templates/ADR_TEMPLATE.md).
3. **Apply Design Patterns Only to Earned Complexity**:
   - Use Strategy, Adapter, Command, State, and Observer pragmatically while rejecting speculative abstract-factory hierarchies following [references/design-patterns-pragmatic.md](references/design-patterns-pragmatic.md).
4. **Select Optimal Data Structures & Bound Memory**:
   - Match access patterns (`O(1)` lookup, ordered range scan, bounded LRU, streaming generator) and enforce hard collection size limits using [references/data-structures-and-complexity.md](references/data-structures-and-complexity.md).
5. **Lock Down API & Data Contracts**:
   - Validate inputs at system boundaries ("Parse, Don't Validate"), enforce idempotency keys, and preserve backwards compatibility using [references/api-and-contract-design.md](references/api-and-contract-design.md).
6. **Build Resilient Error & Concurrency Paths**:
   - Distinguish transient vs permanent errors, apply exponential backoff with full jitter, and enforce bounded queues/timeouts on every concurrent task using [references/error-handling-and-resilience.md](references/error-handling-and-resilience.md) and [references/concurrency-and-async.md](references/concurrency-and-async.md).
7. **Refactor Legacy Code via Characterization Tests**:
   - Lock existing behavior under golden master tests before extracting seams using [references/refactoring-legacy-code.md](references/refactoring-legacy-code.md).

## Numbers and defaults

| Architectural Metric | Default Target | Hard Limit / Rule |
|---|---|---|
| Module Dependency Graph | Strict Directed Acyclic Graph (DAG) | `0` circular imports between packages/modules |
| Function / Method Length | `15–40 lines` | `<= 80 lines`; cyclomatic complexity `<= 10` |
| Max In-Memory Batch Size (4 GB RAM) | Stream in `64 KB – 4 MB` chunks | Never `read()` unbounded multi-hundred-MB files into RAM at once |
| External I/O Timeout | `5.0 s` connect, `15.0 s` read | `0` external calls without an explicit timeout |
| Retry Policy (Transient Errors Only) | `max_attempts = 3`, base `250 ms` | Exponential backoff `2^n * base` + full random jitter; never retry `4xx` validation errors |
| Worker Pool / Queue Concurrency | `min(4, os.cpu_count())` threads/workers | Bounded work queue (`maxsize = 64–256`) with backpressure |

## Failure modes and fixes

- **Symptom**: Business logic cannot be unit-tested without spinning up a live database, HTTP server, or Blender/Godot GUI.
  - **Fix**: Refactor to **Functional Core, Imperative Shell**. Move calculations and decision rules into pure functions taking plain data dicts/structs and returning decisions/commands; keep I/O inside a 20-line outer wrapper.
- **Symptom**: Processing a 600 MB log or EXR metadata dump crashes a 4 GB RAM laptop with `MemoryError`.
  - **Fix**: Replace eager list comprehensions (`[parse(line) for line in f.readlines()]`) with streaming iterators/generators (`for line in f:`) and bounded batch flushes (`1,000` records per transaction).
- **Symptom**: Retry loop hammers a degraded downstream service and triggers a cascading outage (Retry Storm).
  - **Fix**: Cap retries at `3`, add full random jitter (`random.uniform(0, min(max_delay, base * 2 ** attempt))`), and trip a circuit breaker when failure rate exceeds `50%` over 20 requests.

## Done check

- [ ] Core domain logic is decoupled from I/O adapters and runs in `< 100 ms` under `unittest` / `node:test`.
- [ ] Module dependency graph has zero circular dependencies.
- [ ] All I/O calls specify explicit timeouts, bounded memory streaming, and structured error handling.
- [ ] Major architectural decisions are recorded using `templates/ADR_TEMPLATE.md`.

## Related files

- [references/system-design-principles.md](references/system-design-principles.md)
- [references/design-patterns-pragmatic.md](references/design-patterns-pragmatic.md)
- [references/data-structures-and-complexity.md](references/data-structures-and-complexity.md)
- [references/api-and-contract-design.md](references/api-and-contract-design.md)
- [references/error-handling-and-resilience.md](references/error-handling-and-resilience.md)
- [references/concurrency-and-async.md](references/concurrency-and-async.md)
- [references/refactoring-legacy-code.md](references/refactoring-legacy-code.md)
- [templates/ADR_TEMPLATE.md](templates/ADR_TEMPLATE.md)
