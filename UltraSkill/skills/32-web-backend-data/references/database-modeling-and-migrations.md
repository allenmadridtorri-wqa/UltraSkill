# Database Modeling and Zero-Downtime Migrations

A relational schema is the bedrock of application correctness. Let the database enforce data integrity via types, `NOT NULL`, `CHECK` constraints, `UNIQUE` indexes, and `FOREIGN KEY` constraints—never rely on application code alone.

---

## 1. Schema Design Rules

1. **Every Table Has a Primary Key & Audit Timestamps**:
   - Use 64-bit integers (`INTEGER PRIMARY KEY`) or sortable UUIDv7/ULIDs, plus `created_at TEXT NOT NULL` (ISO-8601 UTC `"2026-05-01T14:30:00Z"`) and `updated_at TEXT NOT NULL`.
2. **Store Money and Precise Quantities as Integers**:
   - Never store currency or frame timestamps as `FLOAT` (`0.1 + 0.2 = 0.30000000000000004`). Store integer minor units (`amount_cents INTEGER NOT NULL`) or integer microseconds/frames.
3. **Explicit Foreign Keys + Indexing**:
   - Every `FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE` column **must** have a supporting index (`CREATE INDEX idx_frames_project_id ON frames(project_id);`). Without an index on the child foreign key column, deleting a parent row triggers a full table scan of the child table!

---

## 2. Numbered Forward-Only Schema Migrations

Never edit a live database schema manually or use auto-magical `synchronize: true` ORMs in production. Maintain a directory of immutable, numbered SQL migrations (`migrations/001_init.sql`, `migrations/002_add_frame_checksum.sql`):

1. **Migration Tracking Table (`_schema_migrations`)**:
   ```sql
   CREATE TABLE IF NOT EXISTS _schema_migrations (
       version TEXT PRIMARY KEY,
       checksum_sha256 TEXT NOT NULL,
       applied_at_utc TEXT NOT NULL
   );
   ```
2. **Transactional Application**:
   - For each migration file sorted by `version`:
     - If `version` is already in `_schema_migrations`, verify its `checksum_sha256` matches the file on disk (alerts immediately if someone mutated an already-applied migration!).
     - Otherwise, execute the migration SQL and insert the `_schema_migrations` row inside a single atomic `BEGIN IMMEDIATE ... COMMIT` transaction.

---

## 3. Expand-Contract Pattern for Zero-Downtime Changes

To rename or split a column in a live service without downtime:
1. **Expand (Migration N)**: Add the new nullable column (`new_col`). Deploy code that writes to **both** `old_col` and `new_col`, while reading from `old_col`.
2. **Backfill**: Run a batched background update (`UPDATE tbl SET new_col = old_col WHERE new_col IS NULL LIMIT 5000`) until 0 rows remain.
3. **Switch & Contract (Migration N+1)**: Switch application reads/writes solely to `new_col`, then drop `old_col`.
