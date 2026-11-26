# JavaScript (`ES2022+`) and TypeScript (`5.x`) Standards

JavaScript and TypeScript drive Three.js realtime 3D web scenes, interactive story runtimes, and full-stack Node.js/browser applications.

---

## 1. Strict TypeScript Configuration & Type Modeling

Always enable `"strict": true` and `"noUncheckedIndexedAccess": true`.
1. **Model States with Discriminated Unions (Impossible States Impossible)**:
   ```typescript
   type AsyncState<T> =
     | { status: "idle" }
     | { status: "loading"; startedAtMs: number }
     | { status: "ready"; data: T }
     | { status: "error"; code: string; message: string };
   ```
   - Never use `{ loading: boolean; data?: T; error?: string }` where `loading: true` and `error: "failed"` can accidentally be true simultaneously.
2. **Prefer `unknown` over `any` at External Boundaries**:
   - Parse `JSON.parse()` or `fetch()` payloads as `unknown` and narrow them via type-guard functions before accessing properties.

---

## 2. Zero-Allocation Rules for `requestAnimationFrame` Loops

In Three.js or HTML5 Canvas 60 FPS loops (`16.67 ms` budget):
- **NEVER** call `new THREE.Vector3()`, `new THREE.Matrix4()`, `.map()`, `.filter()`, or object spread `{ ...state }` inside `requestAnimationFrame`. Allocating 500 short-lived objects per frame triggers V8 Major GC pauses (`15–45 ms` frame stutters).
- Pre-allocate module-scoped scratch variables (`const _tmpVec = new THREE.Vector3();`) and mutate them in place (`_tmpVec.copy(a).sub(b)`).

---

## 3. Top JS/TS Footguns & Fixes

| Footgun | Bug Behavior | Fix |
|---|---|---|
| **`[10, 2, 1].sort()`** | Converts numbers to strings and returns `[1, 10, 2]` | Always pass numeric comparator: `.sort((a, b) => a - b)` |
| **Floating Promises & Uncanceled Fetch** | Race conditions when user clicks quickly; memory leaks after unmount | Pass `AbortController.signal` to `fetch()` and abort on cleanup |
| **`==` Loose Equality & `0` Falsiness** | `if (!count)` treats valid `0` as missing | Use `===` and nullish coalescing `count ?? defaultVal` (not `count \|\| defaultVal`) |
| **Event Listener Leaks** | `window.addEventListener("resize", ...)` never removed | Store listener reference or `AbortController` and remove in `dispose()` |
