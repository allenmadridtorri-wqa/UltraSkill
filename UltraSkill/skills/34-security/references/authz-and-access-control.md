# Authorization and Access Control (AuthZ)

**Authentication (AuthN)** proves *who* the caller is; **Authorization (AuthZ)** verifies whether that caller is permitted to perform *this specific action* on *this specific resource*.

---

## 1. Deny by Default & Central Policy Enforcement

1. **Default-Deny Middleware**:
   - Every endpoint requires an authenticated principal by default unless explicitly decorated as `@public_route` (e.g., `/healthz`, `/login`).
2. **Prevent Broken Object-Level Authorization (BOLA / IDOR)**:
   - Checking `if user.is_authenticated:` is **not** an authorization check!
   - Every query or mutation targeting an entity ID (`project_id`, `job_id`, `save_id`) must bind the authenticated user's `user_id` or `tenant_id` directly in the SQL `WHERE` clause:
   ```python
   row = conn.execute(
       "SELECT id, title, status FROM projects WHERE id = ? AND owner_id = ?",
       (project_id, current_user.id),
   ).fetchone()
   if row is None:
       raise PermissionOrNotFoundError("Project not found")
   ```
   - Returning a uniform `404 Not Found` when a user requests an ID owned by someone else prevents attackers from enumerating private IDs.

---

## 2. Prevent Mass Assignment (Explicit Field Allowlists)

Never update a database row or domain object by blindly merging a user's JSON dictionary (`user.__dict__.update(req_json)`), which allows an attacker to pass `{"role": "admin", "balance": 999999}` in a profile-update request.

- Explicitly destructure only the permitted fields for each action:
  ```python
  def update_profile(user_id: str, payload: dict[str, Any]) -> None:
      display_name = str(payload.get("display_name", "")).strip()[:64]
      bio = str(payload.get("bio", "")).strip()[:280]
      conn.execute(
          "UPDATE users SET display_name = ?, bio = ? WHERE id = ?",
          (display_name, bio, user_id),
      )
  ```
