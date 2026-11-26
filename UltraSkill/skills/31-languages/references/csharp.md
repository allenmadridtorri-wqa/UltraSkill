# C# (`.NET 8` / Godot C# / Unity) Standards

In C# game engines and high-throughput backends, the single greatest performance threat is **Garbage Collector (GC) pressure** caused by hidden boxing, LINQ closures, and heap allocations on the hot path.

---

## 1. Zero-Allocation Hot-Path Discipline

Inside `_PhysicsProcess(double delta)` / `Update()` or high-frequency request handlers:
1. **Ban `System.Linq` (`.Where().Select().ToList()`) on Hot Paths**:
   - Every LINQ chain allocates enumerator objects and closure delegates on the managed heap. Use a standard `for (int i = 0; i < list.Count; i++)` loop (`List<T>.Enumerator` is a value-type `struct` when iterated directly via `foreach` or indexed `for`).
2. **Use `Span<T>`, `ReadOnlySpan<T>`, and `ArrayPool<T>`**:
   - Slice arrays or parse buffers with `Span<byte>` (`stackalloc byte[256]` for small scratch buffers) with zero heap allocations.
   - Rent reusable arrays from `ArrayPool<T>.Shared.Rent(minLength)` and return them in a `finally` block.
3. **Value Types (`readonly record struct`)**:
   - Represent small math primitives, damage payloads, and grid coordinates (`<= 16–24 bytes`) as `readonly record struct` implementing `IEquatable<T>` (implementing `IEquatable<T>` prevents boxing when the struct is used as a `Dictionary<K, V>` key).

---

## 2. Nullable Reference Types & Resource Safety

- Enable `<Nullable>enable</Nullable>` across all `.csproj` files so potential `NullReferenceException` paths become compile-time warnings/errors.
- Wrap all `IDisposable` / `IAsyncDisposable` objects (`FileStream`, `HttpClient` responses, DB connections) in `using var` declarations.
- Pass `CancellationToken ct` through every `async Task` method signature and avoid `async void` (except top-level framework event handlers wrapped in `try/catch`).
