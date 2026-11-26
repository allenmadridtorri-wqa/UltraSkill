# Authentication and Session Management

Never roll custom cryptography, never store plaintext or fast-hashed (`MD5`/`SHA1`/`raw SHA256`) passwords, and never put sensitive session tokens in `localStorage` where any XSS script can exfiltrate them.

---

## 1. Password Hashing with Memory-Hard KDFs

Use **`Argon2id`** (preferred) or **`scrypt`** (built into Python's standard library `hashlib.scrypt` and Node's `crypto.scrypt` with zero external dependencies):

```python
import hashlib
import hmac
import secrets

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        dklen=32,
    )
    return f"scrypt$16384$8$1${salt.hex()}${digest.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    parts = stored_hash.split("$")
    if len(parts) != 6 or parts[0] != "scrypt":
        return False
    n, r, p = int(parts[1]), int(parts[2]), int(parts[3])
    salt = bytes.fromhex(parts[4])
    expected = bytes.fromhex(parts[5])
    candidate = hashlib.scrypt(
        password.encode("utf-8"), salt=salt, n=n, r=r, p=p, dklen=len(expected)
    )
    return hmac.compare_digest(candidate, expected)
```
- Always use constant-time comparison (`hmac.compare_digest` / `crypto.timingSafeEqual`) when comparing digests or tokens.

---

## 2. Stateful Opaque Session Cookies vs JWTs

For web applications, **Opaque Server-Side Sessions** backed by SQLite/Redis/Postgres are simpler and safer than stateless JWTs because sessions can be **revoked immediately** on logout or compromise:

1. **Token Generation & DB Storage**:
   - Generate a `256-bit` random token: `raw_token = secrets.token_urlsafe(32)`.
   - Send `raw_token` to the browser in a cookie:
     `Set-Cookie: __Host-sid=<raw_token>; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=86400`
   - Store only `token_sha256 = hashlib.sha256(raw_token.encode()).hexdigest()` in the `sessions` database table alongside `user_id`, `expires_at`, and `revoked_at`. (If an attacker dumps the `sessions` table via a read-only leak, they still cannot hijack active sessions!)
2. **Session Rotation on Privilege Change**:
   - Always issue a brand-new session ID upon login or password change to prevent Session Fixation attacks.
3. **CSRF Protection**:
   - Pair `SameSite=Lax` cookies with a custom request header check (`X-Requested-With: XMLHttpRequest` or synchronizer CSRF token) and strict `Origin` header validation on all `POST`/`PUT`/`PATCH`/`DELETE` routes.
