# Secrets and Configuration Management

Credentials, private keys, and signing tokens must remain strictly separate from source code.

---

## 1. The 5 Commandments of Secret Management

1. **Zero Secrets in Source or Git History**:
   - Never hardcode API keys (`AIza...`, `sk-...`, `ghp_...`, `AKIA...`), database passwords, or JWT signing keys in source files, tests, or Dockerfiles.
2. **Commit `.env.example`, Gitignore `.env`**:
   - `.gitignore` must contain `.env`, `.env.*`, `*.pem`, `*.key`, `credentials.json`, and `!*env.example`.
   - `.env.example` documents every required variable with safe dummy placeholders (`GEMINI_API_KEY="YOUR_KEY_HERE"`).
3. **Fail Fast on Startup When Required Secrets Are Missing**:
   - Validate all required environment variables during process boot (`config.py`), raising an explicit startup error listing any missing variable names (never their values!).
4. **Never Expose Private Secrets to Browser Bundles**:
   - Any environment variable prefixed with `VITE_`, `NEXT_PUBLIC_`, or `REACT_APP_` is compiled directly into public client-side JavaScript readable by anyone in DevTools. Keep private API keys strictly in server-side `process.env` / `os.environ` behind `/api/*` backend routes.
5. **Redact Secrets from Logs, Crash Reports, and Error Messages**:
   - If a database connection fails, log `"Database connection failed to host db.internal:5432"` — never log the full connection URI `"postgres://admin:SuperSecret123@db.internal:5432/prod"`.
