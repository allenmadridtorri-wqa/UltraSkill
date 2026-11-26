# Python (`3.10+`) Production Standards

Python powers UltraSkill's validation tooling, Blender `bpy` automation, Google Colab runners, and backend data scripts. Write stdlib-first, statically typed, memory-bounded Python.

---

## 1. Core Idioms & Stdlib-First Discipline

1. **Zero Unnecessary Pip Dependencies**:
   - Before reaching for a third-party package, use Python's batteries-included standard library:
     - Paths: `pathlib.Path` (never `os.path.join` string concatenation).
     - CLI parsing: `argparse` with `--help` and `--self-test`.
     - Data structures: `dataclasses.dataclass(frozen=True)`, `typing.TypedDict`, `enum.Enum`, `collections.deque`.
     - Subprocesses: `subprocess.run(["cmd", "arg"], check=True, capture_output=True, text=True, timeout=30)` (never `shell=True` with user strings).
     - Database: `sqlite3` with `with conn:` transaction context managers.
     - Testing: `unittest` (runs anywhere with zero setup).
2. **Complete Type Annotations**:
   - Annotate every function parameter and return type (`def parse_frame(path: pathlib.Path) -> dict[str, Any]:`).
3. **Atomic File Writes**:
   - Write to `target.with_suffix(target.suffix + ".tmp")` and call `tmp_path.replace(target)` so interrupted scripts never leave half-written JSON or config files.

---

## 2. Top Python Footguns & Fixes

| Footgun | Bug Behavior | Fix |
|---|---|---|
| **Mutable Default Arguments** (`def fn(items=[]):`) | Default list is allocated once at `def` time and mutated across calls | Use `items: list[str] | None = None` |
| **Late-Binding Loop Closures** (`[lambda: i for i in range(5)]`) | All 5 lambdas return `4` | Capture loop var as default arg: `[lambda x=i: x for i in range(5)]` |
| **Bare `except:` or `except Exception: pass`** | Swallows `KeyboardInterrupt`, `SystemExit`, and real bugs silently | Catch specific exceptions (`except (OSError, ValueError) as exc:`) and log/re-raise |
| **Unbounded `read()` on Large Files** | `Path("2gb.log").read_text()` crashes a 4 GB RAM laptop | Iterate line-by-line: `with path.open("r", encoding="utf-8") as f: for line in f:` |
| **Naive `datetime.now()`** | Local timezone ambiguity causes DST bugs | Always use UTC: `datetime.now(timezone.utc).isoformat()` |
