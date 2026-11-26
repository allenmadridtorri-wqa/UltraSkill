# HUD and Menu Ergonomics

A great game HUD communicates critical survival information through **peripheral vision and spatial proximity**, leaving the center `60%` of the viewport clear for gameplay.

---

## 1. HUD Spatial Hierarchy & Safe Zones

1. **5% Title-Safe Inset**:
   - Anchor all corner widgets (Health/Stamina, Minimap, Ammo/Cooldowns, Quest Tracker) inside a `5%` margin (`64x36 px` at `1920x1080`, `42x24 px` at `1280x720`).
   - Use 9-anchor layouts (`Top-Left`, `Bottom-Left`, `Bottom-Right`, `Center`) so switching from `16:9` (`1280x720`) to `16:10` (`1280x800` laptop screen) or `21:9` ultrawide never stretches or clips icons.
2. **Delayed Damage Bar (Two-Layer Health Bar)**:
   - Layer 1 (Top): Instant current HP bar (snaps down immediately on damage).
   - Layer 2 (Underneath): High-contrast white/amber "chunk bar" that pauses for `0.35 s` after damage and then drains smoothly (`decay = 6.0`) to match current HP, making large hits readable at a glance.
3. **Directional Threat Indicators**:
   - When off-screen enemies attack or hit the player, render a radial arc around the center reticle (`radius = 140 px`) pointing toward the attacker's world-space azimuth relative to camera forward.

---

## 2. Deterministic Gamepad & Keyboard Focus Stack

Never rely on automatic spatial UI focus guessing alone—in grid inventories or multi-column settings screens, auto-focus often skips diagonal buttons or gets trapped.

1. **Focus Stack Manager**:
   - Maintain `var _focus_history: Array[Control] = []`.
   - When opening `PauseMenu` -> `SettingsModal` -> `ConfirmResetDialog`:
     - Save current `get_viewport().gui_get_focus_owner()` onto `_focus_history`.
     - Set `process_mode` or `mouse_filter = IGNORE` on the background menu layer so clicks/D-pad inputs cannot leak behind the active modal.
     - Explicitly call `grab_focus()` on the modal's primary default button (`"Cancel"` for destructive dialogs, `"Resume"` for pause menu).
2. **Focus Rescue Watchdog**:
   - In the active menu controller's `_unhandled_input(event)`, if a directional D-pad/key event arrives while `get_viewport().gui_get_focus_owner() == null`, immediately call `default_focus_control.grab_focus()`.

---

## 3. Dirty-Flagged UI Updates (Zero Per-Frame Layout Thrash)

Never update text labels (`ammo_label.text = "%d / %d" % [cur, max]`) inside `_process(delta)` every frame—setting `.text` forces font shaping and layout recalculation every tick. Connect UI widgets purely to domain signals (`ammo_changed`, `health_changed`).
