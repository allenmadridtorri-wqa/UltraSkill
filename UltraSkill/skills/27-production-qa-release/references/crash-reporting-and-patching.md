# Crash Reporting and Hotfix Patching

When a player experiences a crash or bug in the wild, they rarely open a terminal to run your game with `--verbose`. Your game must automatically maintain clean, privacy-safe rotating logs and support low-friction `.pck` / data hotfixes.

---

## 1. Local Rotating Log Architecture

Enable file logging by default in `project.godot`:

```ini
[debug]
file_logging/enable_file_logging=true
file_logging/enable_file_logging.pc=true
file_logging/log_path="user://logs/game.log"
file_logging/max_log_files=5
```

### Structured Startup Banner
On boot (`GameLoop._ready()`), always print a single structured JSON header line at the top of the log so any player-submitted `game.log` immediately tells you their hardware and version:

```json
{"event":"boot","game_version":"1.0.0","commit":"a1b2c3d","os":"Windows","gpu":"Intel(R) UHD Graphics 620","ram_mb":4096,"preset":"LOW"}
```

### Privacy Rule for Logs
- **NEVER** log OS usernames (`C:\Users\RealName\...` -> sanitize to `user://...`), IP addresses, auth tokens, or environment variables inside `game.log`.

---

## 2. Crash Recovery & Safe Mode Boot

1. **Boot Sentinel File (`user://boot_in_progress.lock`)**:
   - Create `boot_in_progress.lock` at the start of boot before initializing 3D rendering or loading user graphics settings.
   - Delete `boot_in_progress.lock` once the Title Screen renders its first 10 frames cleanly.
2. **Automatic Safe-Mode Fallback**:
   - If `boot_in_progress.lock` **already exists** on startup, the previous launch crashed during initialization (e.g., player selected a broken resolution or `HIGH` preset exceeded their 1 GB VRAM).
   - Automatically fall back to **`LOW` Preset, `1280x720` Windowed mode**, and display a non-intrusive notice: *"Graphics settings were reset to Safe Mode after an unexpected shutdown."*

---

## 3. Delta `.pck` Hotfix Patching

In Godot 4 (and pack-based engines), you can ship a `2 MB` `patch_1_0_1.pck` containing only modified scripts, balance JSONs, or fixed scenes without forcing players to re-download a `400 MB` base archive:

```gdscript
func load_installed_patches() -> void:
	var patch_dir := DirAccess.open("user://patches")
	if patch_dir == null:
		return
	var files := patch_dir.get_files()
	files.sort() # Apply in lexicographical version order: patch_001.pck, patch_002.pck
	for file_name in files:
		if file_name.ends_with(".pck"):
			var ok := ProjectSettings.load_resource_pack("user://patches/" + file_name, true)
			print("Loaded hotfix pack: %s (ok=%s)" % [file_name, ok])
```
- Always verify the patch `.pck` SHA-256 signature against a signed manifest before calling `load_resource_pack()`.
