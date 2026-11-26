# Architecture Decision Record (`ADR-001`)

- **Title**: `<Short Noun Phrase — e.g., ADR-001: Use SQLite in WAL Mode with Pure-Python Migration Runner for Local State>`
- **Status**: `[ ] Proposed | [x] Accepted | [ ] Superseded by ADR-XXX`
- **Date**: `<YYYY-MM-DD>`
- **Owners / Pillars Affected**: `<Coding / Game Dev / 3D Pipeline>`

---

## 1. Context & Problem Statement

Describe the technical requirement, scale targets, and hardware constraints driving this decision in 3–5 sentences:
- **Workload**: `<e.g., Track 10,000 render frames, checksums, and job retries across local CLI and Google Colab sessions>`
- **Hardware Constraint**: `<Must run in < 50 MB RAM with zero external daemon processes on a 4 GB RAM laptop>`

---

## 2. Options Considered

| Option | Pros | Cons / Risks | Memory & Dependency Cost |
|---|---|---|---|
| **Option A (Chosen)**: `<SQLite3 stdlib in WAL mode>` | Built into Python 3 stdlib; ACID transactions; single-file portable `.db`; concurrent readers with `WAL` | Single-writer lock (`busy_timeout = 5000ms` required) | `~4 MB` RAM, `0` pip packages |
| **Option B (Rejected)**: `<PostgreSQL in Docker container>` | High multi-node write concurrency | Docker Desktop consumes `1.5–2.5 GB` RAM, crashing a 4 GB laptop | `> 1,500 MB` RAM |
| **Option C (Rejected)**: `<Flat JSON file rewritten on every update>` | Zero SQL syntax | Corrupts on power loss if not atomic; $O(N)$ full-file rewrite on every frame status update | $O(N)$ RAM growth |

---

## 3. Decision & Technical Guardrails

We chose **Option A** with the following mandatory guardrails:
1. Enable `PRAGMA journal_mode=WAL;`, `PRAGMA synchronous=NORMAL;`, `PRAGMA foreign_keys=ON;`, and `PRAGMA busy_timeout=5000;` on every connection.
2. Wrap all schema upgrades in numbered, transactional migration scripts tracked in a `_schema_migrations` table.
3. Parameterize 100% of SQL queries (`?` placeholders); zero string-interpolated SQL.

---

## 4. Consequences & Rollback Plan

- **Positive**: Zero external dependencies, `< 5 ms` query latency, portable single-file backups.
- **Negative / Limit**: If write throughput ever exceeds `~2,000 transactions/second` across distributed cloud nodes, we will swap the repository adapter behind the `LedgerRepository` port interface.
