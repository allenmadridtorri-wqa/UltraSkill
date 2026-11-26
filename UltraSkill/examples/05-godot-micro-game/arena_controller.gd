class_name ArenaEncounterController
extends Node3D
## Orchestrates the 3-wave micro-arena encounter with Squad Attack Token coordination,
## hit-stop impact feedback, and LOW-preset entity pooling caps (<= 12 active enemies).

signal wave_started(wave_index: int, total_enemies: int)
signal enemy_defeated_in_arena(remaining_enemies: int)
signal arena_victory(completion_time_sec: float)

const MAX_ACTIVE_ENEMIES_LOW: int = 12
const MAX_MELEE_ATTACK_TOKENS: int = 2

@export var total_waves: int = 3

var _current_wave: int = 0
var _active_enemies: Dictionary = {}
var _pending_reinforcements: int = 0
var _melee_token_holders: Dictionary = {}
var _elapsed_time_sec: float = 0.0
var _is_encounter_active: bool = false
var _hit_stop_timer: float = 0.0


func start_encounter() -> void:
	_current_wave = 0
	_elapsed_time_sec = 0.0
	_is_encounter_active = true
	_advance_to_next_wave()


func _physics_process(dt: float) -> void:
	if not _is_encounter_active:
		return

	if _hit_stop_timer > 0.0:
		_hit_stop_timer = maxf(0.0, _hit_stop_timer - dt)
		return

	_elapsed_time_sec += dt
	_prune_out_of_bounds_enemies()


func request_melee_token(enemy_id: int) -> bool:
	if _melee_token_holders.has(enemy_id):
		return true
	if _melee_token_holders.size() < MAX_MELEE_ATTACK_TOKENS:
		_melee_token_holders[enemy_id] = true
		return true
	return false


func release_melee_token(enemy_id: int) -> void:
	_melee_token_holders.erase(enemy_id)


func trigger_hit_stop(is_heavy_hit: bool) -> void:
	var duration := 0.085 if is_heavy_hit else 0.045
	_hit_stop_timer = maxf(_hit_stop_timer, duration)


func register_enemy_defeat(enemy_id: int) -> void:
	if not _active_enemies.has(enemy_id):
		return
	_active_enemies.erase(enemy_id)
	release_melee_token(enemy_id)

	if _pending_reinforcements > 0 and _active_enemies.size() < MAX_ACTIVE_ENEMIES_LOW:
		_pending_reinforcements -= 1
		_spawn_pooled_enemy()

	var total_remaining := _active_enemies.size() + _pending_reinforcements
	enemy_defeated_in_arena.emit(total_remaining)

	if total_remaining == 0:
		if _current_wave < total_waves:
			_advance_to_next_wave()
		else:
			_is_encounter_active = false
			arena_victory.emit(_elapsed_time_sec)


func _advance_to_next_wave() -> void:
	_current_wave += 1
	var wave_budget := 4 + (_current_wave * 4)
	var spawn_now := mini(wave_budget, MAX_ACTIVE_ENEMIES_LOW)
	_pending_reinforcements = wave_budget - spawn_now

	for i in range(spawn_now):
		_spawn_pooled_enemy()

	wave_started.emit(_current_wave, wave_budget)


func _spawn_pooled_enemy() -> void:
	var next_id := Time.get_ticks_usec() + _active_enemies.size()
	_active_enemies[next_id] = {"pos_y": 0.0}


func _prune_out_of_bounds_enemies() -> void:
	var fallen_ids: Array[int] = []
	for enemy_id: int in _active_enemies.keys():
		var data: Dictionary = _active_enemies[enemy_id]
		if float(data.get("pos_y", 0.0)) < -100.0:
			fallen_ids.append(enemy_id)
	for fallen_id in fallen_ids:
		register_enemy_defeat(fallen_id)
