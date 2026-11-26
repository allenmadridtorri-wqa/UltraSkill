# POSIX Shell & Bash Scripting Standards

Shell scripts glue together CI pipelines, FFmpeg encoding jobs, and cloud container builds. Unchecked shell scripts fail silently mid-way and continue executing destructive commands on empty variables.

---

## 1. Canonical Safe Script Header & Cleanup Trap

Every `bash` script must begin with strict error modes and a deterministic `EXIT` cleanup trap:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
IFS=$'\n\t'

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_WORK_DIR=""

cleanup() {
  local exit_code=$?
  if [[ -n "${TMP_WORK_DIR}" && -d "${TMP_WORK_DIR}" ]]; then
    rm -rf "${TMP_WORK_DIR}"
  fi
  exit "${exit_code}"
}
trap cleanup EXIT INT TERM

TMP_WORK_DIR="$(mktemp -d)"
```

- **`-e` (`errexit`)**: Exit immediately if any command exits non-zero.
- **`-u` (`nounset`)**: Treat unset variables as an error and exit immediately.
- **`-o pipefail`**: A pipeline `cmd1 | cmd2` fails if *any* stage fails (default bash only checks the last stage!).

---

## 2. Quoting, Arrays, and Safe Iteration

1. **Quote Every Variable Expansion (`"${var}"`)**:
   - Unquoted `$file_path` splits on spaces and expands `*` globs, breaking paths like `My Render Project/shot 01.exr`.
2. **Use Bash Arrays for Command Arguments (Never `eval` Strings)**:
   ```bash
   ffmpeg_args=(-y -framerate 24 -i "${input_pattern}" -c:v libx264 -crf 16 "${out_mp4}")
   ffmpeg "${ffmpeg_args[@]}"
   ```
3. **Safe File Iteration (`find -print0`)**:
   - Never write `for f in $(ls *.exr); do` (breaks on spaces and special characters).
   - Use null-delimited streams or nullglob:
     ```bash
     while IFS= read -r -d '' file; do
       printf 'Processing: %s\n' "${file}"
     done < <(find "${RENDER_DIR}" -maxdepth 1 -name '*.exr' -print0)
     ```
4. **When to Switch from Shell to Python**:
   - The moment a script needs nested JSON parsing, floating-point math, retry loops, or exceeds **`80 lines`**, write it in Python 3 (`argparse` + `subprocess.run`) instead of bash.
