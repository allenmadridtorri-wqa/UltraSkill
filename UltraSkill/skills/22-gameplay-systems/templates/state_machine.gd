class_name UltraStateMachine
extends Node
## Deterministic Hierarchical State Machine with guaranteed exit() cleanup
## and an 8-entry transition ring buffer for debugging.

signal state_changed(previous_state: StringName, new_state: StringName)

@export var initial_state_name: StringName = &"Idle"

var current_state_name: StringName = &""
var _states: Dictionary = {}
var _transition_history: Array[Dictionary] = []
var _tick_counter: int = 0
var _is_transitioning: bool = false

const MAX_HISTORY: int = 8


func register_state(state_id: StringName, state_obj: Object) -> void:
	_states[state_id] = state_obj


func start(msg: Dictionary = {}) -> void:
	if _states.has(initial_state_name):
		transition_to(initial_state_name, msg)


func transition_to(target_state_id: StringName, msg: Dictionary = {}) -> bool:
	if _is_transitioning:
		push_warning("StateMachine: Recursive transition blocked targeting %s" % target_state_id)
		return false
	if not _states.has(target_state_id):
		push_error("StateMachine: Unknown target state %s" % target_state_id)
		return false

	_is_transitioning = true
	var prev_id := current_state_name

	if prev_id != &"" and _states.has(prev_id):
		var prev_obj: Object = _states[prev_id]
		if prev_obj.has_method("exit"):
			prev_obj.call("exit", target_state_id)

	current_state_name = target_state_id
	var next_obj: Object = _states[target_state_id]
	if next_obj.has_method("enter"):
		next_obj.call("enter", prev_id, msg)

	_record_transition(prev_id, target_state_id)
	_is_transitioning = false
	state_changed.emit(prev_id, target_state_id)
	return true


func step_physics(dt: float) -> void:
	_tick_counter += 1
	if current_state_name != &"" and _states.has(current_state_name):
		var obj: Object = _states[current_state_name]
		if obj.has_method("physics_update"):
			obj.call("physics_update", dt)


func step_visual(dt: float) -> void:
	if current_state_name != &"" and _states.has(current_state_name):
		var obj: Object = _states[current_state_name]
		if obj.has_method("update"):
			obj.call("update", dt)


func get_transition_history() -> Array[Dictionary]:
	return _transition_history.duplicate()


func _record_transition(from_state: StringName, to_state: StringName) -> void:
	_transition_history.append({
		"from": from_state,
		"to": to_state,
		"tick": _tick_counter
	})
	if _transition_history.size() > MAX_HISTORY:
		_transition_history.pop_front()
