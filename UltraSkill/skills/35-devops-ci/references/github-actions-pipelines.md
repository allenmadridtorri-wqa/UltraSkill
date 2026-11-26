# GitHub Actions CI/CD Pipelines

A well-engineered CI pipeline runs in under 3 minutes, caches dependencies deterministically, cancels superseded runs, and blocks broken or insecure commits from ever reaching `main`.

---

## 1. The 5 Non-Negotiable Workflow Guardrails

Every `.github/workflows/*.yml` file must include:
1. **Concurrency Cancellation**:
   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```
2. **Explicit Job Timeout**:
   - Always set `timeout-minutes: 10` (default GitHub timeout is 360 minutes—a single hung test without a timeout can burn 6 hours of quota!).
3. **Least-Privilege Permissions**:
   - Set `permissions: contents: read` at the top level.
4. **Lockfile-Keyed Dependency Caching**:
   - Use `cache: 'npm'` or `cache: 'pip'` in `actions/setup-node@v4` / `actions/setup-python@v5` so unchanged dependencies restore in 4 seconds.
5. **Fail-Fast Stage Ordering**:
   - Run the fastest, cheapest checks first:
     1. Secret Scan & Syntax/Manifest Validation (`< 3 seconds`)
     2. Static Type Check & Linter (`< 15 seconds`)
     3. Unit & Integration Test Suite (`< 30 seconds`)
     4. Production Build & Checksum Packaging (`1–3 minutes`)
