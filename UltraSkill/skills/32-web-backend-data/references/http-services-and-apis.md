# HTTP Services and APIs

Design HTTP endpoints that are predictable, strictly validated at ingress, bounded in payload size, and safe to retry.

---

## 1. HTTP Method & Status Code Semantics

| Method | Idempotent? | Typical Success Code | Standard Error Codes |
|---|---|---|---|
| `GET /api/v1/jobs` | Yes | `200 OK` | `400` Bad Query Params, `401` Unauthenticated, `429` Rate Limited |
| `POST /api/v1/jobs` | Via `Idempotency-Key` header | `201 Created` (with `Location` header) or `202 Accepted` (async job) | `400` Malformed JSON, `409` Conflict, `413` Payload Too Large, `422` Schema Validation Failed |
| `PATCH /api/v1/jobs/:id` | Yes (for deterministic field updates) | `200 OK` | `403` Forbidden, `404` Not Found, `409` Optimistic Lock Conflict (`etag`) |
| `DELETE /api/v1/jobs/:id` | Yes | `204 No Content` | `403` Forbidden, `404` Not Found |

---

## 2. Ingress Guardrails (Size, Content-Type, Rate Limiting)

1. **Strict `Content-Type` & Body Limit**:
   - Reject any `POST`/`PUT`/`PATCH` missing `Content-Type: application/json` with `HTTP 415 Unsupported Media Type`.
   - Enforce a stream byte limit (`<= 1 MB` for JSON endpoints) **before** buffering into memory or running `JSON.parse()`, returning `HTTP 413`.
2. **Cursor Pagination Envelope**:
   - Never allow an unbounded `GET /api/v1/items` that dumps 500,000 rows into a single JSON response. Clamp `limit = min(int(req.limit or 25), 100)`:
   ```json
   {
     "items": [{"id": "job_102", "status": "DONE"}],
     "next_cursor": "MjAyNi0wNS0wMVQxNDozMDowMFp8am9iXzEwMg==",
     "has_more": true
   }
   ```
3. **Token-Bucket Rate Limiting**:
   - Apply per-IP and per-user rate limits (e.g., `60 req/min` general API, `5 req/min` login/password-reset endpoints) returning `HTTP 429 Too Many Requests` with a `Retry-After: <seconds>` header.
