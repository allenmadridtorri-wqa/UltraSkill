# Cloud Builds for Low-Spec Laptops (4 GB RAM / 1 GB Intel UHD)

When developing on a 4 GB RAM laptop, the browser + OS + code editor already consume `~2.8 GB` of RAM. Running local Docker daemons, heavy C++/Rust links, multi-worker Webpack/Vite production bundlers, or offline Cycles renders will freeze the laptop via swap thrashing.

---

## 1. Local vs Cloud Workload Split

| Task | Run Locally on 4 GB RAM Laptop? | Where It Runs Instead |
|---|---|---|
| **Editing Code, JSON Schemas, Markdown, GDScript** | **YES** (`< 150 MB` RAM) | Local Editor |
| **Python Stdlib Unit Tests, AST Checks, Secret Scan** | **YES** (`< 50 MB` RAM, `< 2 sec`) | Local Terminal (`python3 tools/validate.py`) |
| **Three.js / Godot `LOW` Preset (`720p`, `<= 150` draws)** | **YES** (`<= 380 MB` VRAM) | Local Browser / Lightweight Engine Preview |
| **Blender Wireframe / Solid / Workbench Blocking** | **YES** (Optional) | Local or Headless Script Generation |
| **Blender Cycles Path Tracing (1080p/4K + OIDN)** | **NEVER LOCALLY** | **Google Colab GPU (`Tesla T4` 16 GB VRAM) with OptiX** |
| **Windows `.exe` + `.pck` Cross-Compilation & Zipping** | **NEVER LOCALLY** | **GitHub Actions (`ubuntu-24.04` 16 GB RAM Runner)** |
| **Docker Image Builds & Multi-Version Test Matrices** | **NEVER LOCALLY** | **GitHub Actions CI/CD** |

---

## 2. Keeping Local Dev Tools Featherweight

1. **Limit Node.js / TypeScript Memory When Run Locally**:
   - If running a local dev server, set `NODE_OPTIONS="--max-old-space-size=1024"` and disable heavy source-map generation in dev mode.
2. **Single-Worker Local Test Execution**:
   - Run local tests sequentially or with `--jobs 2` max; let GitHub Actions run the full 4-core matrix.
3. **Triggering Cloud Builds on Demand**:
   - Push a branch or tag (`git tag v1.0.0 && git push origin v1.0.0`), then download the finished `.zip` artifact directly from the GitHub Actions Release page.
