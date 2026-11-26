# Dependency and Supply-Chain Security

Every third-party package added to `package.json` or `requirements.txt` grants its transitive dependency tree execution rights on developer laptops and production servers.

---

## 1. The Stdlib-First Minimal Dependency Rule

Before installing any external package, ask:
1. **Can this be written in `<= 40 lines` of standard library code?**
   - Never install external packages for left-padding, simple SHA-256 hashing (`hashlib`), UUID generation (`uuid.uuid4()`), CLI parsing (`argparse`), SQLite access (`sqlite3`), or temporary directory creation (`tempfile`).
2. **What is the transitive dependency fan-out and maintenance health?**
   - Reject abandoned libraries or packages that pull in 80 transitive sub-packages for a single utility function.

---

## 2. Lockfiles & Deterministic Installs

1. **Always Commit Lockfiles**:
   - Commit `package-lock.json`, `Cargo.lock`, or hash-pinned `requirements.lock` (`pip-compile --generate-hashes`) to version control.
2. **Use Immutable Install Commands in CI & Production**:
   - Node.js: Run `npm ci --ignore-scripts` (where native build scripts aren't required) instead of `npm install`, guaranteeing the exact SHA-512 integrity hashes in `package-lock.json` are installed.
   - Python: Run `pip install --require-hashes -r requirements.lock`.

---

## 3. Hardening GitHub Actions Workflows

- **Least-Privilege `permissions:` Block**:
  - Set top-level workflow permissions to read-only by default:
    ```yaml
    permissions:
      contents: read
    ```
  - Only grant `contents: write` on the specific release job that uploads release tags/artifacts.
- **Prevent Script Injection in `run:` Blocks**:
  - Never interpolate untrusted GitHub event fields (`${{ github.event.issue.title }}` or `${{ github.head_ref }}`) directly inside a bash `run:` script. Bind them to an `env:` variable first and reference `"${PR_TITLE}"` in bash so shell metacharacters are never evaluated.
