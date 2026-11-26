# C++ (`C++20`) Production Standards

When writing native engine modules, GDExtensions, physics solvers, or CLI tools in C++, enforce deterministic **RAII ownership**, **contiguous cache-friendly memory**, and **zero undefined behavior**.

---

## 1. Ownership & Memory Model (Rule of Zero / Five)

1. **Zero Raw `new` or `delete`**:
   - Allocate dynamic heap objects by value (`std::vector<T>`), single-owner smart pointer (`std::make_unique<T>()`), or arena/slab allocator.
   - Reserve `std::shared_ptr<T>` strictly for genuine shared lifetime across asynchronous threads (atomic reference-count increments have measurable overhead).
   - Pass non-owning references as `const T&` (required) or `const T*` (optional) — never pass `const std::shared_ptr<T>&` when a function does not participate in lifetime ownership.
2. **Rule of Zero**:
   - Design classes around standard RAII members (`std::vector`, `std::string`, `std::unique_ptr`) so the compiler generates correct destructors and move operations automatically.
   - If you must write a custom destructor (e.g., wrapping a C file handle or GPU buffer), implement or `= delete` all five special member functions (Destructor, Copy Ctor, Copy Assign, Move Ctor, Move Assign).

---

## 2. Cache-Friendly Containers & Zero-Copy Views

- **Contiguous Storage Default**: Default to `std::vector<T>` with `.reserve(capacity)` upfront. Avoid `std::list` or `std::map` (pointer-chasing heap nodes destroy L1/L2 CPU cache hit rates).
- **Non-Owning Views (`C++17/20`)**:
  - Accept read-only strings via `std::string_view` instead of `const std::string&` (avoids temporary heap allocation when passing string literals `"hero_mesh"`).
  - Accept contiguous array slices via `std::span<const Vertex>` instead of `(const Vertex* ptr, size_t count)`.

---

## 3. Mandatory Sanitizer & Compiler Gate

Compile all debug/test targets with:
```bash
g++ -std=c++20 -O1 -g -Wall -Wextra -Wpedantic -Werror -fsanitize=address,undefined
```
- **AddressSanitizer (`ASan`)** catches use-after-free, heap/stack buffer overflows, and memory leaks immediately.
- **UndefinedBehaviorSanitizer (`UBSan`)** catches signed integer overflow, null-pointer dereferences, and misaligned reads.
