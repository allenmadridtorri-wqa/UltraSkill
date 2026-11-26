---
name: ultraskill-languages
description: Idiomatic, production-hardened coding standards across 9 core languages (Python, JavaScript/TypeScript, C++, C#, GDScript, GLSL Shaders, SQL, POSIX Shell, and Rust) covering type safety, memory discipline, and footgun prevention.
---

# 31 — Programming Languages Mastery

This skill enforces 10-year veteran coding idioms, type safety, memory efficiency, and common-bug prevention across the 9 primary languages used in 3D automation, game engines, and full-stack software development.

## When to use

- Writing or reviewing Python (`3.10+`) automation, CLI tools, data pipelines, or Blender `bpy` scripts.
- Writing or reviewing JavaScript (`ES2022+`) or strict TypeScript (`5.x`) for Three.js, Node.js, or web apps.
- Writing or reviewing performance-critical C++ (`C++20`), C# (`.NET 8` / Godot / Unity), or Rust (`2021+`).
- Writing or reviewing Godot 4.x statically typed GDScript (`2.0`) or GLSL (`300 es` / `450`) shaders.
- Writing or optimizing SQL queries (`SQLite` / `PostgreSQL`) or portable POSIX shell (`sh` / `bash`) scripts.

## Inputs

- Target language, runtime version, and hardware constraints (`4 GB RAM` / `1 GB Intel UHD` local baseline).
- Project linter/compiler configuration (`tsconfig.json`, `pyproject.toml`, `Cargo.toml`, `project.godot`).

## Steps

1. **Load the Target Language Reference**:
   - **Python 3.10+**: Read [references/python.md](references/python.md) (type hints, `pathlib`, stdlib-first, generator streaming, `argparse`).
   - **JavaScript / TypeScript**: Read [references/javascript-typescript.md](references/javascript-typescript.md) (`strict: true`, discriminated unions, zero per-frame allocations, `AbortController`).
   - **C++20**: Read [references/cpp.md](references/cpp.md) (RAII, `std::unique_ptr`, `std::span`, `string_view`, Rule of 0/5, ASan/UBSan).
   - **C#**: Read [references/csharp.md](references/csharp.md) (nullable reference types, `readonly struct`, `Span<T>`, zero-alloc `ArrayPool`, `CancellationToken`).
   - **GDScript (Godot 4.x)**: Read [references/gdscript.md](references/gdscript.md) (100% static typing `:=`, `StringName`, `@onready`, signal lifecycle).
   - **GLSL Shaders**: Read [references/glsl-shaders.md](references/glsl-shaders.md) (precision qualifiers, branchless math, `ORM` channel sampling, derivative anti-aliasing).
   - **SQL**: Read [references/sql.md](references/sql.md) (parameterized queries, composite indexing, `EXPLAIN QUERY PLAN`, transactions).
   - **POSIX Shell / Bash**: Read [references/shell-posix.md](references/shell-posix.md) (`set -euo pipefail`, variable quoting, `trap` cleanup, safe tempfiles).
   - **Rust**: Read [references/rust.md](references/rust.md) (ownership, borrowing, `thiserror`/`Result` propagation, zero `unwrap()` in production paths).
2. **Apply Strict Typing & Static Analysis**:
   - Enable strict compiler/linter flags from line 1. Never suppress type errors with blanket `# type: ignore` or `as any`.
3. **Eliminate Language-Specific Footguns**:
   - Check against the language reference's "Top Footguns & Fixes" table before finishing any file.

## Numbers and defaults

| Language | Standard / Version Baseline | Mandatory Compiler / Linter Flags |
|---|---|---|
| **Python** | Python `3.10+` | `python3 -m py_compile`, full type annotations, zero mutable default args |
| **TypeScript / JS** | ES2022 / TS `5.x` | `"strict": true`, `"noUncheckedIndexedAccess": true`, ESM `import/export` |
| **C++** | `C++20` | `-Wall -Wextra -Wpedantic -Werror -fno-rtti` (where applicable), RAII everywhere |
| **C#** | `.NET 8` / C# `12` | `<Nullable>enable</Nullable>`, `TreatWarningsAsErrors`, zero GC allocs in game loops |
| **GDScript** | Godot `4.2+` (GDScript 2.0) | `untyped_declaration = Error/Warning`, static types on all args and returns |
| **GLSL** | WebGL2 (`#version 300 es`) / Vulkan (`450`) | `<= 6` texture samplers on LOW preset, zero 3D procedural noise in fragment stage |
| **SQL** | SQLite `3.35+` / Postgres `15+` | `PRAGMA foreign_keys=ON;`, `PRAGMA journal_mode=WAL;`, 100% parameterized binds |
| **Shell** | POSIX `sh` / `bash 4+` | `set -euo pipefail`, all expansions quoted `"$var"`, `trap cleanup EXIT` |
| **Rust** | Rust `2021` Edition | `#![deny(unsafe_code)]` (unless FFI), `cargo clippy -- -D warnings` |

## Failure modes and fixes

- **Symptom (Python)**: A list default argument `def add_tag(tag: str, tags: list[str] = []):` retains items across separate function calls.
  - **Fix**: Never use mutable defaults (`[]`, `{}`). Use `tags: list[str] | None = None` and initialize `if tags is None: tags = []` inside the body.
- **Symptom (JS/TS)**: Floating promises silently crash or swallow errors, and `arr.sort()` sorts numbers alphabetically (`[1, 10, 2]`).
  - **Fix**: Always `await` or `.catch()` every promise, and always pass an explicit numeric comparator `arr.sort((a, b) => a - b)`.
- **Symptom (Shell)**: `rm -rf $BUILD_DIR/*` wipes `/bin` when `BUILD_DIR` is unset.
  - **Fix**: Always enable `set -euo pipefail` (errors on unset variables) and guard destructive paths (`rm -rf "${BUILD_DIR:?}/"*`).

## Done check

- [ ] Code uses explicit static types or type annotations on all public signatures.
- [ ] Zero language-specific footguns (mutable default args, unquoted shell vars, raw `new`/`delete`, string-concatenated SQL, or `unwrap()` on user inputs) exist.
- [ ] Scripts compile/parse cleanly (`ast.parse`, `tsc --noEmit`, `bash -n`).

## Related files

- [references/python.md](references/python.md)
- [references/javascript-typescript.md](references/javascript-typescript.md)
- [references/cpp.md](references/cpp.md)
- [references/csharp.md](references/csharp.md)
- [references/gdscript.md](references/gdscript.md)
- [references/glsl-shaders.md](references/glsl-shaders.md)
- [references/sql.md](references/sql.md)
- [references/shell-posix.md](references/shell-posix.md)
- [references/rust.md](references/rust.md)
