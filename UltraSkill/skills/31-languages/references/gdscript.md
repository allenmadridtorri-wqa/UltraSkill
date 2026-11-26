# GDScript (`Godot 4.x`) Production Standards

Godot 4's GDScript 2.0 supports strict static typing that both catches bugs at edit time and unlocks faster typed-bytecode VM execution (`20–40%` faster than untyped dynamic variants).

---

## 1. Mandatory Static Typing Rules

Enable `debug/gdscript/warnings/untyped_declaration = 2` (Error) in Project Settings.

```gdscript
class_name CombatComponent
extends Node

signal health_depleted(killer_id: int)

@export var max_hp: int = 100
@export var armor_rating: float = 0.15

var _current_hp: int = 100
var _active_statuses: Array[StringName] = []


func _ready() -> void:
	_current_hp = max_hp


func apply_damage(raw_amount: int, attacker_id: int) -> int:
	if _current_hp <= 0:
		return 0
	var mitigated: int = maxi(1, roundi(float(raw_amount) * (1.0 - armor_rating)))
	_current_hp = maxi(0, _current_hp - mitigated)
	if _current_hp == 0:
		health_depleted.emit(attacker_id)
	return mitigated
```

---

## 2. GDScript Performance & Lifecycle Idioms

1. **Use `StringName` (`&"action_name"`) for Dictionary Keys, Signals, Input Actions, and Animation Names**:
   - `&"jump"` hashes a pre-interned pointer (`O(1)` integer comparison) instead of comparing character-by-character strings every frame.
2. **Typed Arrays (`Array[Node3D]`, `PackedFloat32Array`, `PackedVector3Array`)**:
   - Use `PackedVector3Array` / `PackedFloat32Array` for large vertex, path, or transform buffers (`3x` smaller memory footprint and contiguous layout).
3. **Never Call `get_node()` or `$Child` Inside `_process` / `_physics_process`**:
   - Cache node references once in `@onready var _mesh: MeshInstance3D = $VisualRoot/Mesh` or via `@export var target_mesh: MeshInstance3D`.
4. **Deferred Physics Mutations**:
   - Never toggle `CollisionShape3D.disabled = true` synchronously inside an `area_entered` or `body_entered` signal callback (causes `"Can't change this state while flushing queries"` engine errors). Use `collision_shape.set_deferred("disabled", true)`.
