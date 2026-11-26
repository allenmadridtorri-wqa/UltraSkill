# File, Path, and Archive Extraction Safety

Handling user-supplied file paths or extracting `.zip` / `.tar` archives without strict containment checks enables **Path Traversal** (reading/overwriting `/etc/passwd` or `~/.ssh/authorized_keys`) and **Zip-Slip / Zip-Bomb** denial-of-service attacks.

---

## 1. Path Traversal Prevention (`resolve()` + `is_relative_to()`)

Never sanitize paths by calling `.replace("../", "")` (an attacker simply sends `....//` which collapses to `../` after a single pass). Always canonicalize with `pathlib.Path.resolve()` and check containment:

```python
import pathlib

def safe_join_under(base_dir: pathlib.Path, untrusted_rel_path: str) -> pathlib.Path:
    if not untrusted_rel_path or "\x00" in untrusted_rel_path:
        raise ValueError("Invalid path")
    root = base_dir.resolve()
    candidate = (root / untrusted_rel_path).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError(f"Path traversal blocked: '{untrusted_rel_path}' escapes '{root}'")
    return candidate
```

---

## 2. Safe `.zip` Extraction (Anti-Zip-Slip & Anti-Zip-Bomb)

Never call `zip_file.extractall(dest_dir)` directly on an untrusted archive—Python's `extractall` and many archive utilities historically wrote files outside `dest_dir` if an entry was named `../../evil.sh`, or exhausted disk/RAM if a `1 MB` zip decompressed to `100 GB` of zeroes.

```python
import pathlib
import zipfile

MAX_ARCHIVE_FILES = 500
MAX_UNCOMPRESSED_BYTES = 250 * 1024 * 1024  # 250 MB
MAX_COMPRESSION_RATIO = 30.0

def safe_extract_zip(zip_path: pathlib.Path, dest_dir: pathlib.Path) -> list[pathlib.Path]:
    root = dest_dir.resolve()
    root.mkdir(parents=True, exist_ok=True)
    extracted: list[pathlib.Path] = []
    total_bytes = 0

    with zipfile.ZipFile(zip_path, "r") as zf:
        infos = zf.infolist()
        if len(infos) > MAX_ARCHIVE_FILES:
            raise ValueError(f"Archive file count {len(infos)} exceeds {MAX_ARCHIVE_FILES}")

        for info in infos:
            if info.is_dir():
                continue
            target = safe_join_under(root, info.filename)
            total_bytes += info.file_size
            if total_bytes > MAX_UNCOMPRESSED_BYTES:
                raise ValueError("Archive exceeds maximum uncompressed size budget")
            if info.compress_size > 0 and (info.file_size / info.compress_size) > MAX_COMPRESSION_RATIO:
                raise ValueError(f"Suspicious compression ratio on '{info.filename}'")

            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info, "r") as src, target.open("wb") as dst:
                while chunk := src.read(65536):
                    dst.write(chunk)
            extracted.append(target)

    return extracted
```
