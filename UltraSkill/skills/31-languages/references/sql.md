# SQL (`SQLite 3.35+` & `PostgreSQL 15+`) Standards

SQL is declarative, set-oriented, and ACID-transactional. Most database bottlenecks come from three mistakes: **string-interpolated queries (SQL injection)**, **missing composite indexes**, and **N+1 query loops in application code**.

---

## 1. Mandatory SQLite Production Pragmas

Whenever opening a SQLite connection in Python, Node.js, or game servers, execute these 4 pragmas immediately after connect:

```sql
PRAGMA journal_mode = WAL;          -- Concurrent readers + fast append-only WAL writes
PRAGMA synchronous = NORMAL;        -- Safe with WAL; 5x faster commits than FULL
PRAGMA foreign_keys = ON;           -- SQLite disables foreign key enforcement by default!
PRAGMA busy_timeout = 5000;         -- Wait up to 5s on concurrent write lock instead of instant SQLITE_BUSY error
```

---

## 2. Composite Indexing & The Left-Prefix Rule

An index on `(status, created_at DESC)` is an ordered B-Tree sorted first by `status`, then by `created_at`:
- **Fast Index Seek**: `WHERE status = 'PENDING' ORDER BY created_at DESC LIMIT 20` (reads exactly 20 leaf nodes; zero sort step).
- **Full Table Scan (Slow!)**: `WHERE created_at > '2026-01-01'` (cannot use the index because the leading column `status` is omitted).
- **Rule**: Place **equality columns (`=`) first**, and **range/sort columns (`>`, `<`, `ORDER BY`) last** in composite index definitions.
- Always verify every critical query with `EXPLAIN QUERY PLAN SELECT ...` and confirm it reports `SEARCH table USING INDEX` rather than `SCAN table` + `USE TEMP B-TREE FOR ORDER BY`.

---

## 3. Eliminating N+1 Query Loops & Offset Pagination

1. **Ban Queries Inside Application `for` Loops**:
   - Fetching 100 projects (`1` query) and then running `SELECT * FROM frames WHERE project_id = ?` inside a Python loop (`100` queries) executes **101 round-trips**. Use a single `JOIN` or `WHERE project_id IN (?, ?, ...)` batch query.
2. **Keyset (Cursor) Pagination over Large `OFFSET`**:
   - `LIMIT 50 OFFSET 100000` forces the database engine to read and discard 100,000 rows before returning 50.
   - Use keyset pagination on an indexed tuple:
     ```sql
     SELECT id, created_at, title
     FROM jobs
     WHERE (created_at, id) < (?, ?)
     ORDER BY created_at DESC, id DESC
     LIMIT 50;
     ```
