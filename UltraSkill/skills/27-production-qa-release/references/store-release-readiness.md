# Store Release Readiness (Steam / Itch.io / Web)

Before uploading a release build to Steam, Itch.io, or a public web host, run through the 12-point Gold Master checklist so day-one players experience a polished product.

---

## 1. The 12-Point Gold Master Packaging Checklist

1. **Zero Debug Cheats Enabled**:
   - All developer shortcuts (`God Mode`, `Unlock All Levels`, `Free Camera`, `Give 9999 Gold`) are gated behind `if OS.is_debug_build():` and disabled in release exports.
2. **Clean Default First-Boot State**:
   - No pre-existing developer save files, test high scores, or hardcoded window coordinates (`x = 2500` on a second monitor that the player does not have!) ship inside the build directory.
3. **First-Boot Hardware Auto-Detect**:
   - On first launch with no `settings.json`, inspect `RenderingServer.get_video_adapter_name()`. If `"Intel"` + `"UHD"` / `"HD Graphics"` or WebGL mobile/iGPU is detected, default automatically to the **`LOW` Preset (`1280x720`, 60 FPS)**.
4. **Application Icons & Metadata**:
   - Windows `.exe` has a multi-resolution `.ico` (`16, 32, 48, 64, 128, 256 px`), proper Product Name, File Version (`1.0.0.0`), and Copyright string embedded.
5. **Third-Party Licenses (`THIRD_PARTY_LICENSES.txt`)**:
   - Include engine license attribution (e.g., Godot MIT license + FreeType/ENet/MbedTLS notices) and asset/font licenses inside the distribution root.
6. **Authoring Source Excluded**:
   - `.blend`, `.blend1`, `.psd`, `.xcf`, `.git/`, `.env`, and `tests/` directories are excluded from the packaged zip.
7. **Audio Focus & Alt-Tab Behavior**:
   - When the game window loses OS focus (`NOTIFICATION_APPLICATION_FOCUS_OUT`), automatically pause single-player gameplay or mute/attenuate audio by `-20 dB`.
8. **Windowed / Borderless Fullscreen Toggle**:
   - `Alt+Enter` or `F11` and the Settings menu cleanly toggle between `Windowed` and `Borderless Fullscreen` without losing mouse capture.
9. **Exit to Desktop Works Cleanly**:
   - Clicking `"Quit to Desktop"` saves settings, flushes logs, and exits with code `0` within `< 1.0 second` (never hangs waiting on an un-joined background thread).
10. **Web Build Headers & Compression (Itch.io / Web Hosts)**:
    - Web builds avoid `SharedArrayBuffer` thread deadlocks when hosted on platforms without `Cross-Origin-Opener-Policy: same-origin` by exporting single-threaded WebGL2/WebAudio compatible presets unless COOP/COEP headers are guaranteed.
11. **Deterministic Checksum Manifest (`SHA256SUMS.txt`)**:
    - Every release zip ships alongside its SHA-256 hash.
12. **Clean-Machine Smoke Test**:
    - Unpack the zip into a fresh temporary folder and launch it with an empty user profile directory.
