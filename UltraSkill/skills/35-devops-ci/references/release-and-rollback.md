# Release Verification and Fast Rollback

A deployment is not finished when `git push` or `deploy` returns `0`—a deployment is finished only when **automated post-deploy smoke checks confirm the new version is healthy in production**.

---

## 1. Pre-Deploy & Post-Deploy Checklist

### Pre-Deploy Gate
1. All CI checks (`validate.py`, `secret_scanner.py`, unit + integration tests) pass on the exact commit SHA being deployed.
2. Database migrations are **backwards-compatible (Expand phase)** with the currently running `N-1` code version so a code rollback does not break against the new database schema.
3. Previous release artifact (`vN-1.zip` or container tag) is archived and ready for immediate rollback.

### Automated Post-Deploy Smoke Check (`<= 30 seconds` after deploy)
1. Poll `GET /healthz` and `GET /readyz` -> assert `HTTP 200` and expected `"version": "vN"`.
2. Execute 1 synthetic read/write health transaction and check error logs for `0` new unhandled exceptions over a 60-second observation window.

---

## 2. The 60-Second Rollback Rule (`Rollback First, Debug Second`)

If a production deployment causes `S0`/`S1` errors, elevated `5xx` rates (`> 1%`), or crashes:
1. **Do NOT try to write and push a "quick forward fix" while production is burning.**
2. **Immediately roll back** to the known-good `vN-1` artifact (`< 60 seconds` recovery).
3. Reproduce the failure calmly in a local test or staging environment, write a regression test, and follow `skills/33-testing-debugging/templates/POSTMORTEM.md`.
