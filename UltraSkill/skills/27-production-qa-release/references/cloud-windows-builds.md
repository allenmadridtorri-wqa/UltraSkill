# Cloud Windows Builds for Low-Spec Laptops

On a 4 GB RAM laptop with 1 GB Intel UHD integrated graphics, downloading multi-gigabyte C++ cross-compilers, Windows SDKs, or full Godot export template bundles and packing a 500 MB `.pck` archive locally exhausts RAM and disk space.

**The Solution**: Edit lightweight scripts and scenes locally (`< 50 MB`), push a git commit or tag, and let **GitHub Actions cloud runners (2-core / 4-core Ubuntu VMs with 7–16 GB RAM)** build, test, and package your Windows `.exe`, Linux binary, and Web `.zip` in the cloud.

---

## 1. End-to-End Cloud Build Architecture

```text
[4 GB RAM Laptop]
  1. Edit GDScript / Python / JS + JSON data
  2. Run fast local validation (< 2 sec):
     python3 scripts/verify_stat_tables.py
     python3 scripts/package_release_check.py
  3. git tag v1.0.0 && git push origin v1.0.0
          │
          ▼
[GitHub Actions Ubuntu Runner (16 GB RAM, High-Speed SSD)]
  4. Downloads Godot 4 Headless + Export Templates in ~15 seconds
  5. Runs headless unit tests & scene load checks
  6. Exports:
     - build/windows/GameName.exe + GameName.pck -> GameName-v1.0.0-win64.zip
     - build/web/index.html + .wasm + .pck       -> GameName-v1.0.0-web.zip
  7. Generates SHA256SUMS.txt and attaches zips to GitHub Release
```

---

## 2. Headless Godot 4 Export Configuration (`export_presets.cfg`)

Ensure your repository commits a clean `export_presets.cfg` (containing **zero** keystore passwords or API secrets—inject secrets via GitHub Actions environment variables if code-signing):

```ini
[preset.0]
name="Windows Desktop"
platform="Windows Desktop"
runnable=true
dedicated_server=false
custom_features=""
export_filter="all_resources"
include_filter=""
exclude_filter="tests/*,*.blend,*.psd"
export_path="build/windows/Game.exe"

[preset.0.options]
binary_format/architecture="x86_64"
binary_format/embed_pck=false
codesign/enable=false
application/modify_resources=false
```

- **Why `exclude_filter="tests/*,*.blend,*.psd"` is critical**: Keeps raw authoring files and unit-test fixtures out of the player's download zip.
- **Why `embed_pck=false` is recommended**: Keeping `Game.exe` (`~65 MB` signed engine binary) separate from `Game.pck` (your game assets and scripts) avoids false-positive antivirus flags on oversized self-extracting executables and allows small `.pck` hotfix patches.
