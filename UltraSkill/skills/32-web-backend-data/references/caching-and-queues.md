# Caching and Background Job Queues

Caches accelerate hot reads; background queues decouple slow or retryable work (FFmpeg encoding, batch verification, webhook delivery) from interactive request/response threads.

---

## 1. Cache-Aside Discipline & Stampede Protection

1. **Bounded Memory + Jittered TTL**:
   - Always bound in-process caches by entry count (`maxsize = 1024`) and attach a Time-To-Live (TTL) with `±10%` random jitter (`ttl = base_ttl * random.uniform(0.9, 1.1)`) so 500 keys populated at startup do not expire at the exact same millisecond.
2. **Write Invalidation over Complex Write-Through**:
   - On any database mutation (`UPDATE` / `DELETE`), **delete** the affected cache key (`cache.pop(key, None)`) after the transaction commits rather than trying to mutate cache state in place (which races under concurrent updates).

---

## 2. Durable SQLite-Backed Job Queue (Zero External Broker Needed on 4 GB RAM)

On a 4 GB RAM laptop, running Redis + RabbitMQ + Celery daemons wastes `> 600 MB` RAM. A single SQLite table in `WAL` mode comfortably powers an ACID, crash-recoverable job queue at up to `1,000 jobs/sec`:

```sql
CREATE TABLE IF NOT EXISTS job_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idempotency_key TEXT NOT NULL UNIQUE,
    job_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING'
        CHECK (status IN ('PENDING', 'RUNNING', 'DONE', 'DEAD')),
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    available_at_utc TEXT NOT NULL,
    locked_by TEXT,
    last_error TEXT,
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_job_queue_poll
    ON job_queue(status, available_at_utc);
```

### Worker Claim, Visibility Timeout & Dead-Letter Flow
1. **Atomic Claim**:
   - Worker opens `BEGIN IMMEDIATE`, selects the oldest job where `status = 'PENDING' AND available_at_utc <= :now`, updates `status = 'RUNNING', attempts = attempts + 1, locked_by = :worker_id`, and `COMMIT`s.
2. **Idempotent Execution**:
   - Job handlers must be idempotent (safe if executed twice after a crash).
3. **Failure & Dead-Letter Transition**:
   - On failure: if `attempts < max_attempts`, set `status = 'PENDING'` and `available_at_utc = now + backoff`; otherwise set `status = 'DEAD'` and preserve `last_error` for inspection.
