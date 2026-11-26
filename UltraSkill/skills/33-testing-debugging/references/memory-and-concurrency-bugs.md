# Memory Leaks and Concurrency Bugs

Memory leaks and race conditions are the hardest bugs to diagnose because their crash site is temporally and spatially separated from the bug that caused them.

---

## 1. Hunting Memory Leaks (`tracemalloc` & Object Growth Audits)

On a 4 GB RAM laptop, even a `5 MB/minute` leak crashes the application within an hour.

### The 3 Most Common Leak Patterns in Managed Languages (Python / JS / C# / GDScript)
1. **Unbounded Module Caches / Event Listeners**:
   - Appending callbacks to `eventBus.on(...)` every time a UI component or enemy spawns without calling `off(...)` when destroyed holds the entire closure and DOM/Node subtree pinned in RAM forever.
2. **Unclosed Native / GPU Handles**:
   - In Three.js: removing a `Mesh` from `scene.remove(mesh)` does **not** free its GPU memory! You must explicitly call `mesh.geometry.dispose()` and `material.map.dispose()`.
   - In Blender `bpy`: creating procedural meshes via `bpy.data.meshes.new()` without removing orphaned blocks (`bpy.data.meshes.remove(m)`) leaks data blocks across batch iterations.
3. **Diagnostic Tool — Python `tracemalloc` Delta Diff**:
   ```python
   import tracemalloc

   tracemalloc.start()
   snap1 = tracemalloc.take_snapshot()
   # Run workload 100 times...
   snap2 = tracemalloc.take_snapshot()
   for stat in snap2.compare_to(snap1, "lineno")[:5]:
       print(stat)
   ```

---

## 2. Hunting Concurrency & Race Conditions

| Bug Class | Classic Symptom | Root Cause & Fix |
|---|---|---|
| **Check-Then-Act Race (TOCTOU)** | `if not path.exists(): path.mkdir()` crashes with `FileExistsError` under 4 workers | Between `exists()` and `mkdir()`, another worker created the directory. Use atomic operations (`path.mkdir(exist_ok=True)` or `INSERT ... ON CONFLICT DO NOTHING`) |
| **Lost Update** | Two threads increment `counter += 1` from `10`, and final value is `11` instead of `12` | Read-modify-write is not atomic. Protect with a `threading.Lock()` or atomic SQL `UPDATE tbl SET count = count + 1` |
| **AB-BA Deadlock** | Process hangs indefinitely at `0%` CPU | Thread 1 holds `LockA` waiting for `LockB`; Thread 2 holds `LockB` waiting for `LockA`. Enforce total lock ordering and timeouts (`lock.acquire(timeout=5.0)`) |
