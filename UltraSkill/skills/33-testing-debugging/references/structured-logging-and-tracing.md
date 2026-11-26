# Structured Logging and Diagnostic Tracing

When debugging batch pipelines (e.g., 1,440 Blender frames on Google Colab) or multi-step transactions, unstructured `print("done")` lines are useless. Every log event must carry **who, what, where, how long, and why**.

---

## 1. Contextual Span Logging Pattern

Wrap every distinct pipeline phase (Scene Load, OptiX Device Init, Frame Render, EXR Check, FFmpeg Encode) in a timed diagnostic span:

```python
import contextlib
import json
import sys
import time
from typing import Any, Iterator

@contextlib.contextmanager
def trace_span(span_name: str, **context: Any) -> Iterator[dict[str, Any]]:
    t0 = time.perf_counter()
    meta: dict[str, Any] = dict(context)
    try:
        yield meta
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        record = {"event": span_name, "status": "OK", "elapsed_ms": elapsed_ms, **meta}
        print(json.dumps(record), file=sys.stderr)
    except BaseException as exc:
        elapsed_ms = round((time.perf_counter() - t0) * 1000.0, 2)
        record = {
            "event": span_name,
            "status": "ERROR",
            "elapsed_ms": elapsed_ms,
            "error_type": type(exc).__name__,
            "error_msg": str(exc),
            **meta,
        }
        print(json.dumps(record), file=sys.stderr)
        raise
```

---

## 2. Log Level Discipline

- **`ERROR`**: An operation failed and could not recover automatically (e.g., corrupted `.exr`, database constraint violation, missing GPU). Must include the exact input ID/path and exception message.
- **`WARN`**: An unexpected condition occurred, but the system recovered automatically (e.g., transient network retry #1 succeeded, missing `save.json` fell back to `save.json.bak`).
- **`INFO`**: Coarse lifecycle milestones (`"Job started"`, `"Batch 12/24 completed in 18.4s"`). Never emit `INFO` logs inside a per-frame `60 Hz` loop or per-pixel loop.
- **`DEBUG`**: Granular state transitions or SQL query parameters; disabled by default and enabled via `--verbose` or `LOG_LEVEL=DEBUG`.
