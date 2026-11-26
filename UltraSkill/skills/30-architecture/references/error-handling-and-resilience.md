# Error Handling and Resilience

Silent failures (`except Exception: pass`) corrupt data and waste hours of debugging. Production code classifies every failure mode, fails fast on invariant violations, and recovers gracefully from transient external hiccups.

---

## 1. Error Classification Taxonomy

| Category | Examples | Correct Handling Strategy |
|---|---|---|
| **1. Programmer Bug / Invariant Violation** | `TypeError`, `KeyError` on internal dict, `AssertionError`, null pointer | **Fail Fast**: Log full context + stack trace; abort current request/operation immediately; never retry |
| **2. Caller Input / Validation Error (`4xx`)** | Invalid CLI flag, malformed JSON, missing required field, negative quantity | **Reject Cleanly at Boundary**: Return structured validation error (`exit code 2` or `HTTP 400/422`); never retry |
| **3. Transient External Failure (`502/503/504`, Timeout, SQLite Busy)** | Network blip, rate-limit `429`, brief file lock | **Bounded Retry with Exponential Backoff + Full Jitter** (`max 3 attempts`) |
| **4. Permanent External Failure** | Disk full (`ENOSPC`), invalid credentials (`401/403`), missing input file (`ENOENT`) | **Fail Immediately with Actionable Remedy**: Report exact path/resource and required user action |

---

## 2. Exponential Backoff with Full Jitter

Never use fixed-interval `time.sleep(1)` retries across multiple workers (causes synchronized thundering-herd spikes):

```python
import random
import time
from typing import Callable, Tuple, Type, TypeVar

T = TypeVar("T")

def retry_transient(
    fn: Callable[[], T],
    retryable_exceptions: Tuple[Type[BaseException], ...],
    max_attempts: int = 3,
    base_delay_sec: float = 0.25,
    max_delay_sec: float = 4.0,
) -> T:
    for attempt in range(1, max_attempts + 1):
        try:
            return fn()
        except retryable_exceptions:
            if attempt == max_attempts:
                raise
            ceiling = min(max_delay_sec, base_delay_sec * (2 ** (attempt - 1)))
            sleep_sec = random.uniform(0.0, ceiling)
            time.sleep(sleep_sec)
    raise RuntimeError("Unreachable")
```

---

## 3. Resource Cleanup Guarantee (`with` / `try..finally`)

Every file descriptor, database connection, temporary directory, lock, or subprocess must be acquired inside a context manager (`with ...:` in Python, `using` in C#/TS, `defer` in Go/Rust RAII) so exceptions never leak open handles or leave stale lock files behind.
