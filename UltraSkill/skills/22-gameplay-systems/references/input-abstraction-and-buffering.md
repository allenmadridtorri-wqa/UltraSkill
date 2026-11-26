# Input Abstraction and Buffering

Gameplay code must never query hardware keys (`Input.is_key_pressed(KEY_SPACE)`) directly. Instead, route all hardware events through an **Action Map + Rolling Input Buffer** that supports keyboard/mouse, gamepad, runtime rebinding, and frame-accurate action queuing.

---

## 1. Logical Action Layer

Separate hardware bindings from gameplay verbs:

| Logical Action | Default Keyboard/Mouse | Default Gamepad | Input Type |
|---|---|---|---|
| `move_x`, `move_y` | `WASD` / Arrow Keys | Left Stick (`deadzone = 0.18`) | 2D Normalized Vector |
| `look_x`, `look_y` | Mouse Delta (`sens = 0.0022 rad/px`) | Right Stick (`deadzone = 0.15`, response curve `x^1.6`) | 2D Delta / Rate Vector |
| `jump` | `Space` | South Button (`A` / `Cross`) | Buffered Trigger (`120 ms`) |
| `attack_light` | Left Mouse Button | West Button (`X` / `Square`) | Buffered Trigger (`150 ms`) |
| `attack_heavy` | Right Mouse Button | Top Button (`Y` / `Triangle`) | Buffered Trigger (`150 ms`) |
| `dodge` | `Left Shift` | East Button (`B` / `Circle`) | Buffered Trigger (`140 ms`) |
| `interact` | `E` / `F` | Right Shoulder (`RB` / `R1`) | Instant / Hold Trigger |

---

## 2. Radial Stick Deadzone (Not Axial)

Never apply deadzones independently to X and Y (`if abs(x) < 0.2: x = 0`), which creates a cross-shaped cardinal snap that ruins 360° diagonal movement. Apply a **scaled radial deadzone**:

```gdscript
func apply_radial_deadzone(raw_stick: Vector2, deadzone: float = 0.18) -> Vector2:
	var mag := raw_stick.length()
	if mag < deadzone:
		return Vector2.ZERO
	var rescaled_mag := clampf((mag - deadzone) / (1.0 - deadzone), 0.0, 1.0)
	return (raw_stick / mag) * rescaled_mag
```

---

## 3. Rolling Action Input Buffer

When a player presses `dodge` 3 frames (`50 ms`) before their current attack recovery ends, dropping that input makes the game feel broken.

### Buffer Algorithm
1. Maintain a dictionary `_buffer_timestamps: Dictionary = {}` mapping `action_name -> float` (remaining buffer seconds).
2. Whenever an action is pressed (`event.is_action_pressed(action)`), set `_buffer_timestamps[action] = 0.14` (`140 ms`).
3. Every physics tick (`dt`), decrement all active timers: `_buffer_timestamps[action] -= dt`.
4. Provide a consumption method:
   ```gdscript
   func consume_buffered_action(action: StringName) -> bool:
   	if _buffer_timestamps.get(action, 0.0) > 0.0:
   		_buffer_timestamps[action] = 0.0
   		return true
   	return false
   ```
5. When an attack enters its recovery cancel window or the character lands on the floor, call `consume_buffered_action("dodge")` or `consume_buffered_action("jump")`.

---

## 4. Automatic Input Device Switching & Prompts

Track the last active input device (`DEVICE_KBM` vs `DEVICE_GAMEPAD_XBOX` vs `DEVICE_GAMEPAD_PS`):
- Require a stick movement `> 0.35` or button press to switch from KBM to Gamepad (ignores slight controller drift on a desk).
- Require mouse movement `> 12 px` or key press to switch from Gamepad to KBM.
- Emit `device_changed(new_device)` so HUD button prompts update instantaneously without flickering.
