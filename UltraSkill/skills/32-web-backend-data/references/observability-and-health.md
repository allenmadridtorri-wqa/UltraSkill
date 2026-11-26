# Observability, Structured Logging, and Health Probes

You cannot operate or debug a service in production if its logs are unstructured `print("error happened")` lines and it lacks liveness/readiness probes.

---

## 1. Structured JSON Logging with Correlation IDs

Every HTTP request or CLI batch job generates or propagates a **`request_id` (`X-Request-ID`)** and emits single-line JSON log records to `stdout`/`stderr`:

```json
{
  "ts": "2026-05-01T14:32:10.412Z",
  "level": "INFO",
  "service": "render-ledger-api",
  "request_id": "req_9a8f1b2c",
  "method": "POST",
  "path": "/api/v1/jobs",
  "status": 201,
  "duration_ms": 4.82,
  "user_id": "usr_42"
}
```

### Redaction Policy
- **NEVER** log `Authorization` headers, session cookies, passwords, API keys, or full credit-card/PII payloads. Filter sensitive keys (`password`, `token`, `secret`, `authorization`, `cookie`) to `"[REDACTED]"` inside the logger formatter.

---

## 2. Liveness (`/healthz`) vs Readiness (`/readyz`) Probes

Separate "Is the process wedged?" from "Can the process serve traffic right now?":

1. **`GET /healthz` (Liveness Probe — `< 2 ms`)**:
   - Checks only that the event loop / HTTP worker thread is responsive.
   - Does **not** query external databases (otherwise a brief DB restart causes the orchestrator to kill and restart all healthy web containers in a cascading loop).
   - Returns `200 OK`: `{"status": "alive", "uptime_sec": 8420}`.
2. **`GET /readyz` (Readiness Probe — `< 25 ms` with `2s` timeout)**:
   - Executes a fast `SELECT 1;` against SQLite/Postgres and checks disk space in the work directory.
   - Returns `200 OK` when ready to accept traffic, or `503 Service Unavailable` when dependencies are unreachable.

---

## 3. Graceful Shutdown (`SIGTERM` / `SIGINT`)

When a service receives `SIGTERM`:
1. Immediately flip `/readyz` to return `503` and stop accepting new connections.
2. Allow in-flight requests/transactions up to **`10.0 seconds`** to finish.
3. Flush logs, close the database connection cleanly (checkpointing the SQLite WAL), and exit with code `0`.
