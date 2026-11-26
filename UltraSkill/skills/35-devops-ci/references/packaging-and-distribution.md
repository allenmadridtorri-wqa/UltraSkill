# Packaging, Semantic Versioning, and Distribution

A release artifact must be **self-contained, version-stamped, reproducible, and cryptographically verifiable**.

---

## 1. Semantic Versioning (`MAJOR.MINOR.PATCH`)

Follow strict SemVer (`v1.2.3`):
- **`MAJOR` (`1.0.0 -> 2.0.0`)**: Breaking change to CLI flags, public API schemas, save file envelope without auto-migration, or minimum required engine version.
- **`MINOR` (`1.0.0 -> 1.1.0`)**: Backwards-compatible new skills, new scripts, new API endpoints, or new gameplay content.
- **`PATCH` (`1.0.0 -> 1.0.1`)**: Backwards-compatible bug fixes, performance optimizations, or documentation clarifications.
- **Pre-Release Tags**: `v1.1.0-rc.1` for Release Candidates tested prior to final Gold Master promotion.

---

## 2. Reproducible Zip Archives

Standard `zip` commands embed each file's local modification timestamp (`mtime`), meaning zipping the exact same source commit twice produces two `.zip` files with different SHA-256 hashes.

To create **bit-identical reproducible zip archives** in Python:
1. Sort all archive file paths in deterministic lexicographical order (`sorted(paths)`).
2. Normalize `ZipInfo.date_time` to a fixed epoch (`(2026, 1, 1, 0, 0, 0)`) and normalize POSIX file permissions (`0o644` for regular files, `0o755` for executable scripts).
3. Exclude transient cache directories (`__pycache__`, `.DS_Store`, `*.pyc`).

---

## 3. Cryptographic Checksum Manifest (`SHA256SUMS.txt`)

Every downloadable release must publish a standard GNU coreutils-compatible `SHA256SUMS.txt` file:
```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  UltraSkill-1.0.0.zip
```
Users and automated installers verify integrity with a single command:
```bash
sha256sum -c SHA256SUMS.txt
```
