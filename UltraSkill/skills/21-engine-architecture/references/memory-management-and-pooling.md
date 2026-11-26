# Memory Management and Object Pooling

On a 4 GB RAM baseline machine (where the OS consumes `~1.5 GB`), the game process must stay under **`1,800 MB` system RAM** and **`512 MB` GPU VRAM**. Furthermore, allocating and freeing nodes every frame triggers Garbage Collection (GC) or heap fragmentation spikes that ruin 60 FPS frame pacing.

---

## 1. Per-Frame Allocation Budget: Zero

During active gameplay (`PLAYING` state):
- **Target**: `0 KB` heap allocations on the hot path (`_process`, `_physics_process`, `requestAnimationFrame`).
- **Common Hidden Allocators to Eliminate**:
  - Creating temporary `Vector3` / `Matrix4` objects inside JavaScript loops (use module-scoped scratch variables `_tmpVec1`, `_tmpMat4`).
  - Dynamic string concatenation (`"HP: " + str(hp)`) every frame when `hp` has not changed (dirty-flag UI updates).
  - Lambda closures or array `.filter().map()` allocations inside per-frame AI perception ticks.
  - `instantiate()` and `queue_free()` on projectiles, hit sparks, damage numbers, and footsteps.

---

## 2. Deterministic Object Pool Implementation (Godot 4 GDScript)

Pre-allocate high-frequency transient entities during scene load:

```gdscript
class_name NodePool
extends Node

var _prefab: PackedScene
var _available: Array[Node] = []
var _active: Array[Node] = []
var _max_capacity: int

func setup(prefab: PackedScene, initial_count: int, max_capacity: int) -> void:
	_prefab = prefab
	_max_capacity = max_capacity
	for i in range(initial_count):
		var inst := _prefab.instantiate()
		_deactivate_node(inst)
		add_child(inst)
		_available.append(inst)

func acquire() -> Node:
	var inst: Node = null
	if not _available.is_empty():
		inst = _available.pop_back()
	elif _active.size() < _max_capacity:
		inst = _prefab.instantiate()
		add_child(inst)
	else:
		# Recycle oldest active instance deterministically
		inst = _active.pop_front()
		_deactivate_node(inst)
	_activate_node(inst)
	_active.append(inst)
	return inst

func release(inst: Node) -> void:
	var idx := _active.find(inst)
	if idx != -1:
		_active.remove_at(idx)
		_deactivate_node(inst)
		_available.append(inst)

func _activate_node(inst: Node) -> void:
	inst.set_process(true)
	inst.set_physics_process(true)
	if inst is CanvasItem or inst is Node3D:
		inst.visible = true

func _deactivate_node(inst: Node) -> void:
	inst.set_process(false)
	inst.set_physics_process(false)
	if inst is CanvasItem or inst is Node3D:
		inst.visible = false
	if inst.has_method("on_pool_reset"):
		inst.call("on_pool_reset")
```

---

## 3. Mandatory Reset Contract (`on_pool_reset`)

The most common pooling bug is **stale state bleed** (a recycled bullet retains its previous velocity, status effects, or signal connections). Every pooled entity must implement `on_pool_reset()`:
1. Zero linear and angular velocities (`velocity = Vector3.ZERO`).
2. Reset timers, hit counters, and lifetime accumulators.
3. Clear transient status arrays (e.g., `_already_hit_targets.clear()`).
4. Disable collision shapes via `set_deferred("disabled", true)` until placed at the new spawn transform.

---

## 4. Reference Cycle & Leak Prevention

1. **Signal Disconnection**: If a pooled or destroyed node connects to a global autoload (`EventBus`), disconnect in `_exit_tree()` or use weak references.
2. **Orphan Node Audit**: Run `Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT)` at scene transitions. An orphan count `> 0` after unloading a level indicates nodes removed from the tree (`remove_child`) without being freed (`queue_free`).
3. **VRAM Texture Unloading**: Inspect `Performance.RENDER_VIDEO_MEM_USED` before and after loading a level 5 times in a row. Memory usage must plateau by load #2 (`< 1%` drift).
