---
name: ultraskill-web-backend-data
description: Full-stack web and backend engineering covering accessible frontend state architecture, HTTP APIs, secure authentication and sessions, relational database modeling and expand-contract migrations, caching and job queues, WebSockets/SSE, and observability.
---

# 32 — Web, Backend & Data Engineering

This skill covers production full-stack engineering: building responsive, accessible browser frontends, stateless HTTP services, hardened authentication/session flows, ACID database schemas with zero-downtime migrations, background queues, realtime WebSockets/SSE, and health observability—optimized to run locally on a 4 GB RAM laptop using lightweight SQLite/in-process services before scaling to the cloud.

## When to use

- Building or architecting a frontend UI, SPA, or interactive web dashboard.
- Designing REST / JSON RPC backend APIs with validation, pagination, and rate limiting.
- Implementing user authentication, password hashing (`Argon2id`/`scrypt`), session cookies, or OAuth2/PKCE.
- Modeling relational database schemas (`SQLite` / `PostgreSQL`) and running numbered schema migrations.
- Adding bounded caching, idempotent background worker queues, or dead-letter handling.
- Implementing bidirectional WebSockets or unidirectional Server-Sent Events (SSE) with heartbeat and backpressure.
- Configuring `/healthz` and `/readyz` probes, structured JSON request logs, and latency metrics.

## Inputs

- Domain entities, access patterns, and latency/throughput targets.
- Target deployment profile (local single-file SQLite on 4 GB RAM vs hosted cloud service).

## Steps

1. **Design the Frontend State & Accessibility Layer**:
   - Separate server-cache state from local UI state, enforce semantic HTML + keyboard navigation (`WCAG AA >= 4.5:1`), and handle all 4 async states (`Idle`, `Loading`, `Empty`, `Error`) using [references/frontend-architecture.md](references/frontend-architecture.md).
2. **Build Clean HTTP Services & Endpoints**:
   - Enforce proper HTTP methods, status codes, cursor pagination, request payload size caps (`<= 1 MB` JSON), and token-bucket rate limiting using [references/http-services-and-apis.md](references/http-services-and-apis.md).
3. **Harden Authentication & Sessions**:
   - Hash passwords with memory-hard `Argon2id` or `scrypt`, store opaque session tokens in `HttpOnly; Secure; SameSite=Lax` cookies, and protect state-changing routes against CSRF using [references/authentication-and-sessions.md](references/authentication-and-sessions.md).
4. **Model the Database & Automate Migrations**:
   - Normalize tables to 3NF with explicit `FOREIGN KEY` constraints and composite indexes, and apply forward-only transactional migrations using [references/database-modeling-and-migrations.md](references/database-modeling-and-migrations.md) and [scripts/sqlite_migration_runner.py](scripts/sqlite_migration_runner.py).
5. **Add Bounded Caching & Background Queues**:
   - Use cache-aside with jittered TTLs, prevent cache stampedes, and run idempotent job workers with dead-letter queues using [references/caching-and-queues.md](references/caching-and-queues.md).
6. **Wire Realtime Streams & Observability**:
   - Use SSE for server-to-client progress streams or WebSockets with `25s` ping/pong heartbeats ([references/realtime-websockets-sse.md](references/realtime-websockets-sse.md)) and expose structured correlation-ID logs + `/healthz` probes ([references/observability-and-health.md](references/observability-and-health.md)).

## Numbers and defaults

| Parameter | Default Value | Tolerance / Notes |
|---|---|---|
| API Latency Target (`p95` / `p99`) | `<= 50 ms` / `<= 150 ms` (local/cached) | Database query budget `<= 15 ms` |
| Max Request Body Size (JSON) | `1 MB` (`1,048,576 bytes`) | Reject oversized bodies with `HTTP 413` before JSON parsing |
| Pagination Page Size | Default `25`, Max `100` | Keyset cursor `(created_at, id)` preferred over `OFFSET` |
| Password Hashing (`scrypt` / `Argon2id`) | `Argon2id (m=64MB, t=3, p=1)` or `hashlib.scrypt(n=16384, r=8, p=1)` | `16-byte` cryptographic random salt per password |
| Session Token Entropy & Cookie TTL | `256 bits` (`secrets.token_urlsafe(32)`), Idle TTL `24h`, Absolute `7d` | Store SHA-256 hash of session token in DB, never raw token |
| WebSocket / SSE Heartbeat | `25 seconds` ping interval, `10 seconds` timeout | Reconnect with exponential backoff (`500 ms -> 15 s` + jitter) |

## Failure modes and fixes

- **Symptom**: Concurrent API requests fail intermittently with `sqlite3.OperationalError: database is locked`.
  - **Fix**: Enable `PRAGMA journal_mode=WAL;` and `PRAGMA busy_timeout=5000;` on connection startup, and keep write transactions under `5 ms` (never perform network calls inside an open DB transaction).
- **Symptom**: Deleting or renaming a database column breaks running web workers during a deployment.
  - **Fix**: Follow the **3-Step Expand-Contract Pattern**: (1) Add new nullable column and dual-write; (2) Backfill existing rows and switch reads; (3) Drop old column in a subsequent release.
- **Symptom**: Expired popular cache key causes 200 concurrent requests to hit the database simultaneously (Cache Stampede).
  - **Fix**: Use single-flight request coalescing (only 1 worker recomputes while others await the same promise/lock) and add `±10%` random jitter to cache TTLs.

## Done check

- [ ] Frontend handles `Loading`, `Empty`, `Error`, and `Success` states with full keyboard navigation and `>= 4.5:1` contrast.
- [ ] All SQL queries use parameterized placeholders (`?` or `$1`) and composite indexes verified by `EXPLAIN QUERY PLAN`.
- [ ] Session tokens use `256-bit` CSPRNG entropy stored hashed in the database with `HttpOnly` cookies.
- [ ] `python3 skills/32-web-backend-data/scripts/sqlite_migration_runner.py --self-test` exits with code `0`.

## Related files

- [references/frontend-architecture.md](references/frontend-architecture.md)
- [references/http-services-and-apis.md](references/http-services-and-apis.md)
- [references/authentication-and-sessions.md](references/authentication-and-sessions.md)
- [references/database-modeling-and-migrations.md](references/database-modeling-and-migrations.md)
- [references/caching-and-queues.md](references/caching-and-queues.md)
- [references/realtime-websockets-sse.md](references/realtime-websockets-sse.md)
- [references/observability-and-health.md](references/observability-and-health.md)
- [scripts/sqlite_migration_runner.py](scripts/sqlite_migration_runner.py)
