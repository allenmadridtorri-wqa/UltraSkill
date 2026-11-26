# Rust (`2021+` Edition) Production Standards

Rust provides C++-grade zero-cost performance and deterministic memory footprint (no garbage collector) with compile-time guarantees against data races, null pointers, and use-after-free bugs.

---

## 1. Ownership, Borrowing & Slice Idioms

1. **Accept Slices in Function Signatures, Not Owned Containers**:
   - Write `fn verify_name(name: &str)` instead of `fn verify_name(name: &String)` (accepts `&str` literals, `String`, and substrings without allocation).
   - Write `fn sum_weights(items: &[f32])` instead of `fn sum_weights(items: &Vec<f32>)`.
2. **Pre-Allocate Capacities**:
   - Use `Vec::with_capacity(n)` and `String::with_capacity(bytes)` whenever the upper bound is known to avoid repeated geometric reallocations.
3. **Avoid Blind `.clone()` Calls to Appease the Borrow Checker**:
   - Before cloning a large buffer or struct inside a loop, check if you can pass a read-only reference `&T`, split struct borrows into smaller sub-structs, or use `Cow<'_, str>` (Clone-on-Write).

---

## 2. Error Handling (`Result<T, E>` & Zero `unwrap()`)

- **Ban `.unwrap()` and `.expect()` on Runtime Inputs**:
  - In production library and CLI code, `.unwrap()` turns a recoverable malformed file or network drop into a process-crashing `panic!`.
  - Propagate errors cleanly with the `?` operator and structured error enums:
  ```rust
  #[derive(Debug)]
  pub enum LedgerError {
      Io(std::io::Error),
      InvalidFrameRange { start: u32, end: u32 },
      ChecksumMismatch { frame: u32, expected: String, actual: String },
  }
  ```
- Reserve `.expect("invariant: ...")` strictly for compile-time constants or tests where failure indicates an impossible internal state bug.
