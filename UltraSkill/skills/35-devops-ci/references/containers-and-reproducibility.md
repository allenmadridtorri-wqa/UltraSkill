# Containers and Reproducibility

When deploying backend services or headless batch workers to cloud environments, build minimal, non-root, multi-stage container images.

---

## 1. Canonical Multi-Stage Non-Root `Dockerfile`

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim-bookworm AS builder
WORKDIR /build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY requirements.lock ./
RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --require-hashes -r requirements.lock

# Stage 2: Minimal Production Runtime
FROM python:3.12-slim-bookworm AS runtime
WORKDIR /app

# Create unprivileged user (UID 10001)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /usr/sbin/nologin -M appuser && \
    mkdir -p /app/data && chown -R appuser:appgroup /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY --from=builder /opt/venv /opt/venv
COPY --chown=appuser:appgroup src/ ./src/

USER 10001:10001
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD ["python3", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/healthz', timeout=2)"]

ENTRYPOINT ["python3", "-m", "src.server"]
```

---

## 2. Container Security & Size Checklist

1. **Pin Base Image Tags (Never `:latest`)**: Use `python:3.12-slim-bookworm` (or `@sha256:...` digest) so builds don't break overnight when upstream shifts OS versions.
2. **Mandatory `.dockerignore`**: Exclude `.git`, `node_modules`, `.venv`, `.env`, `renders/`, and `tests/` so secrets never leak into image layers and build context stays `< 5 MB`.
3. **Exec Form `ENTRYPOINT ["cmd", "arg"]`**: Never use shell form `ENTRYPOINT python3 server.py` (shell form runs under `/bin/sh -c` which fails to forward `SIGTERM` signals cleanly to your process on shutdown).
