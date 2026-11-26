# Data Structures and Algorithmic Complexity

On a 4 GB RAM laptop—or inside a 16.67 ms game frame—an accidental $O(N^2)$ nested loop or an unbounded in-memory cache turns a sub-millisecond operation into a multi-second freeze.

---

## 1. Access-Pattern Selection Cheat Sheet

| Primary Operation | Wrong Structure ($O(N)$ or worse) | Right Structure | Time / Space Complexity |
|---|---|---|---|
| **Membership test (`x in items`) or ID lookup** | `list` / `Array` scan | `set` / `dict` / `Map` | $O(1)$ avg time, $O(N)$ space |
| **FIFO Queue / Sliding Window** | `list.pop(0)` ($O(N)$ memory shift!) | `collections.deque(maxlen=K)` or Ring Buffer | $O(1)$ push/pop, bounded $O(K)$ RAM |
| **Top-K Priority / Next Scheduled Timer** | Sorting full list every tick ($O(N \log N)$) | Binary Heap (`heapq`) | $O(\log N)$ push/pop, $O(1)$ peek min |
| **2D/3D Nearby Entity Query (`radius <= R`)** | All-pairs nested loop ($O(N^2)$) | **Uniform Spatial Hash Grid** (`cell_size = 2*R`) | $O(1)$ cell lookup + local neighbor check |
| **Ordered Range Scan (`WHERE ts BETWEEN a AND b`)** | Unindexed scan | B-Tree index (`SQLite`) or sorted array + `bisect` | $O(\log N + K)$ |
| **Large File / Stream Processing (`> 50 MB`)** | `file.readlines()` / `json.load()` on giant blob | Line-by-line Generator / JSONL (`yield`) | **$O(1)$ constant RAM** |

---

## 2. Eliminating Hidden $O(N^2)$ Traps

1. **String Concatenation in Loops**:
   - Never accumulate large text via `out += chunk` inside a loop across thousands of items. Collect chunks in a list and call `"".join(chunks)` once ($O(N)$).
2. **Repeated Linear Lookups Inside a Loop**:
   - Bad ($O(N \times M)$):
     ```python
     for order in orders:
         user = next(u for u in users if u.id == order.user_id)
     ```
   - Good ($O(N + M)$):
     ```python
     user_by_id = {u.id: u for u in users}
     for order in orders:
         user = user_by_id.get(order.user_id)
     ```
3. **Bounded Caches Only**:
   - Never use an unbounded dictionary as an in-memory cache (`_CACHE[key] = val`, or `@lru_cache(maxsize=None)`). Always enforce an explicit bound (`@lru_cache(maxsize=512)`) so long-running processes never leak memory.
