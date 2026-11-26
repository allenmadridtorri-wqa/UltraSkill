# Concurrency and Asynchronous Programming

Concurrency is not parallelism:
- **I/O-Bound Work** (network requests, waiting on child processes, disk reads): Use `async/await` event loops or a bounded thread pool (`ThreadPoolExecutor(max_workers=4)`).
- **CPU-Bound Work** (image processing, physics simulation, AST/data crunching): Use bounded process pools (`ProcessPoolExecutor(max_workers=os.cpu_count())`), native SIMD/NumPy, or worker threads in non-GIL languages.

---

## 1. The 5 Rules of Safe Concurrency

1. **Share Nothing by Default (Message Passing over Shared Mutable Memory)**:
   - Pass immutable data payloads across queues (`queue.Queue(maxsize=64)`). Never let two threads mutate the same dictionary or entity list without an explicit lock.
2. **Always Bound Queues (`maxsize`) for Backpressure**:
   - If a fast producer pushes 100,000 items into an unbounded `Queue()` while a slow consumer processes 10 items/sec, the queue eats all 4 GB of system RAM and crashes the machine. A bounded queue (`maxsize=64`) blocks the producer naturally until the consumer catches up.
3. **Structured Concurrency & Explicit Timeouts**:
   - Every spawned task (`asyncio.TaskGroup`, `Future`, `subprocess.run`) must belong to a parent scope that cancels and awaits all children on exit or failure, and every wait must include a timeout (`timeout=15.0`).
4. **Consistent Lock Ordering (Deadlock Prevention)**:
   - Avoid acquiring multiple locks simultaneously. If an operation must lock two accounts/resources `A` and `B`, always acquire them in deterministic sorted ID order (`first = min(id_a, id_b)`, `second = max(id_a, id_b)`).
5. **Never Block the Event Loop or Render Thread**:
   - In `asyncio`, Node.js, or browser main threads, a synchronous `time.sleep()`, heavy regex, or `fs.readFileSync()` freezes **all** concurrent connections and UI frames. Offload blocking calls to a worker thread (`asyncio.to_thread()`).
