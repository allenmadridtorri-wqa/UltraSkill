---
name: ultraskill-security
description: Defensive application security covering secret management, SQL/command/XSS/deserialization injection prevention, deny-by-default authorization (RBAC/ABAC), supply-chain lockfile pinning, and path-traversal/Zip-Slip filesystem safety.
---

# 34 — Defensive Application Security

This skill hardens every script, web service, game save loader, and CI pipeline against the most prevalent real-world vulnerabilities: hardcoded credentials, injection (SQLi, Command Injection, XSS, Unsafe Deserialization), broken object-level authorization (IDOR), supply-chain poisoning, and path-traversal / Zip-Slip exploits.

## When to use

- Handling API keys, database credentials, webhook signing secrets, or `.env.example` templates.
- Writing database queries, subprocess calls, HTML template rendering, or file/save parsers.
- Implementing role-based or ownership-based access control checks (`RBAC` / `ABAC`).
- Auditing third-party dependencies (`package-lock.json`, `requirements.txt`, GitHub Actions SHAs).
- Accepting user file paths, uploads, or unpacking `.zip` / `.tar` archives.

## Inputs

- Source files, configuration templates, and dependency manifests.
- Untrusted input boundaries (HTTP requests, CLI flags, environment files, user save/mod files).

## Steps

1. **Eliminate Hardcoded Secrets & Enforce Env Hygiene**:
   - Store secrets strictly in runtime environment variables or secret managers, commit only placeholder `.env.example` files, and scan commits with [references/secrets-and-configuration.md](references/secrets-and-configuration.md) and [scripts/secret_scanner.py](scripts/secret_scanner.py).
2. **Prevent All Injection Classes**:
   - Parameterize 100% of SQL queries, invoke subprocesses with argument lists (`shell=False`), auto-escape HTML/DOM outputs, and ban `eval`/`pickle`/`ResourceLoader.load` on untrusted data using [references/input-validation-and-injection.md](references/input-validation-and-injection.md).
3. **Enforce Deny-by-Default Authorization**:
   - Verify **both** authentication (who you are) and object-level ownership/permission (whether you own `resource_id`) on every request using [references/authz-and-access-control.md](references/authz-and-access-control.md).
4. **Lock Down Dependencies & Supply Chain**:
   - Minimize external dependencies, commit deterministic lockfiles with cryptographic integrity hashes, and pin CI actions using [references/dependency-and-supply-chain.md](references/dependency-and-supply-chain.md).
5. **Sandbox File Paths & Archive Extraction**:
   - Canonicalize paths via `Path.resolve()`, assert `resolved_path.is_relative_to(base_dir)`, validate magic bytes, and enforce Zip-Slip/zip-bomb ceilings using [references/file-and-path-safety.md](references/file-and-path-safety.md).

## Numbers and defaults

| Security Control | Default Policy | Hard Enforcement |
|---|---|---|
| Hardcoded Secrets in Repo | `0` secrets committed | Verified by `secret_scanner.py` (`exit code 0`) |
| SQL Parameterization | `100%` bind parameters (`?` / `$1`) | `0` f-strings or `%` formatting in SQL execution |
| Subprocess Execution | `subprocess.run([...], shell=False, timeout=30)` | `0` `shell=True` or `os.system()` calls with dynamic input |
| Archive Extraction Limits (Anti-Zip-Bomb) | Max `200` files, Max `250 MB` total uncompressed, Max ratio `25:1` | Reject any archive entry containing `..`, leading `/`, or symlinks |
| Upload File Verification | Magic-byte check + UUID storage filename | Never use user-supplied `filename` directly on disk |

## Failure modes and fixes

- **Symptom**: An API key is accidentally committed in column 40 of a config script and then "deleted" in a follow-up commit.
  - **Fix**: Deleting a secret in a new commit leaves the secret permanently readable in `git log -p`. **Immediately revoke and rotate the compromised key** at the provider, then purge history or replace with environment lookup `os.environ["API_KEY"]`.
- **Symptom**: `os.path.join("/app/uploads", "../../etc/passwd")` resolves to `/etc/passwd` when user input contains `..` or starts with `/`.
  - **Fix**: Resolve both paths (`target = (base_dir / user_rel).resolve()`) and assert `target.is_relative_to(base_dir.resolve())` before opening.
- **Symptom**: An authenticated user changes `GET /api/v1/projects/104` to `GET /api/v1/projects/105` and reads another user's private project (IDOR / Broken Object Level Authorization).
  - **Fix**: Scope every database query by the authenticated principal: `SELECT * FROM projects WHERE id = ? AND owner_user_id = ?`.

## Done check

- [ ] Zero hardcoded secrets or high-entropy private keys exist in the repository (`secret_scanner.py` passes).
- [ ] All SQL queries use bind parameters, all subprocess calls use `shell=False` lists, and all HTML output is escaped.
- [ ] Every endpoint/command verifies object-level ownership (`owner_id == current_user.id`).
- [ ] All file reads/writes and archive extractions enforce `is_relative_to(base_dir)` path containment.

## Related files

- [references/secrets-and-configuration.md](references/secrets-and-configuration.md)
- [references/input-validation-and-injection.md](references/input-validation-and-injection.md)
- [references/authz-and-access-control.md](references/authz-and-access-control.md)
- [references/dependency-and-supply-chain.md](references/dependency-and-supply-chain.md)
- [references/file-and-path-safety.md](references/file-and-path-safety.md)
- [scripts/secret_scanner.py](scripts/secret_scanner.py)
