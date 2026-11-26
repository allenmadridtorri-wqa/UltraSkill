# API and Contract Design

Whether designing an HTTP JSON API, a Python library module, a CLI tool, or a cross-language IPC protocol, **contracts are forever**. Internal implementation can be rewritten in an afternoon; breaking a public contract breaks every caller.

---

## 1. "Parse, Don't Validate" at the Boundary

Do not pass raw, untyped `dict[str, Any]` payloads deep into business functions and scatter `if "email" in data and data["amount"] > 0:` checks across 15 files.

1. **Boundary Parsing**:
   - The moment external data enters the process (CLI args, JSON body, config file, network packet), parse it into a strict, immutable domain object (`dataclass(frozen=True)` or validated TypeScript type).
   - Reject malformed inputs immediately at the boundary with an explicit field-level error list.
2. **Interior Guarantee**:
   - Any function inside `core/` that accepts a `ValidatedRenderJob` knows by construction that `start_frame >= 1`, `end_frame >= start_frame`, and `samples in (32, 64, 128, 256, 512, 1024)`.

---

## 2. Backwards-Compatible Evolution (Additive Changes Only)

When evolving a JSON schema, REST endpoint, or save/manifest format within the same major version (`v1.x`):
- **SAFE (Non-Breaking)**:
  - Adding a new optional response field.
  - Adding a new optional request field with a sensible default.
  - Adding a new endpoint or CLI flag.
- **BREAKING (Requires Major Version Bump or Migration Adapter)**:
  - Renaming or removing an existing field (`"userName"` -> `"username"`).
  - Changing a field's type (`"id": 123` -> `"id": "123"` or single object -> array).
  - Making an optional request parameter mandatory.

---

## 3. Idempotency & Deterministic Error Envelopes

1. **Idempotency Keys for State-Mutating Operations**:
   - Any operation that charges currency, enqueues a cloud render job, or creates a resource should accept a client-generated `idempotency_key` (UUIDv4 or deterministic content hash). If the client retries due to a network timeout, the server returns the original result without creating a duplicate job.
2. **Structured Error Envelopes**:
   - Never return bare strings (`"Error: failed"`) or HTML stack traces from an API. Return machine-readable error codes plus human guidance:
   ```json
   {
     "error": {
       "code": "VRAM_BUDGET_EXCEEDED",
       "message": "Scene estimated VRAM (4,850 MB) exceeds T4 safe ceiling (12,500 MB) when 4K textures are unpacked.",
       "field": "texture_resolution_cap",
       "retryable": false
     }
   }
   ```
