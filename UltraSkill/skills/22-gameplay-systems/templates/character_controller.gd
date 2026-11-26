class_name UltraCharacterController3D
extends CharacterBody3D
## Responsive 3D kinematic character controller with coyote time, jump buffering,
## asymmetric fall gravity, variable jump height, and slope snapping.

@export_group("Movement")
@export var max_speed: float = 7.0
@export var sprint_speed: float = 10.5
@export var ground_accel: float = 45.0
@export var ground_friction: float = 38.0
@export var air_control_mult: float = 0.65
@export var turn_boost_mult: float = 2.0

@export_group("Jump & Gravity")
@export var jump_height: float = 2.4
@export var time_to_apex: float = 0.42
@export var time_to_descent: float = 0.32
@export var early_release_cut: float = 0.45
@export var terminal_fall_speed: float = 28.0
@export var coyote_time_window: float = 0.10
@export var jump_buffer_window: float = 0.12

var _jump_velocity: float
var _gravity_up: float
var _gravity_down: float
var _coyote_timer: float = 0.0
var _jump_buffer_timer: float = 0.0
var _is_jumping: bool = false


func _ready() -> void:
	floor_max_angle = deg_to_rad(45.0)
	floor_snap_length = 0.25
	floor_constant_speed = true
	_recalculate_jump_kinematics()


func _recalculate_jump_kinematics() -> void:
	_gravity_up = (2.0 * jump_height) / (time_to_apex * time_to_apex)
	_gravity_down = (2.0 * jump_height) / (time_to_descent * time_to_descent)
	_jump_velocity = (2.0 * jump_height) / time_to_apex


func step_movement(
	dt: float,
	wish_dir: Vector3,
	wants_sprint: bool,
	jump_just_pressed: bool,
	jump_held: bool
) -> void:
	# 1. Update grounded forgiveness timers
	if is_on_floor():
		_coyote_timer = coyote_time_window
		_is_jumping = false
	else:
		_coyote_timer = maxf(0.0, _coyote_timer - dt)

	if jump_just_pressed:
		_jump_buffer_timer = jump_buffer_window
	else:
		_jump_buffer_timer = maxf(0.0, _jump_buffer_timer - dt)

	# 2. Horizontal velocity integration
	var horiz_vel := Vector3(velocity.x, 0.0, velocity.z)
	var target_speed := sprint_speed if wants_sprint else max_speed
	var clean_wish := Vector3(wish_dir.x, 0.0, wish_dir.z)
	if clean_wish.length_squared() > 1.0:
		clean_wish = clean_wish.normalized()

	var accel_rate := ground_accel if is_on_floor() else (ground_accel * air_control_mult)
	if clean_wish.length_squared() > 0.001:
		if horiz_vel.dot(clean_wish) < 0.0:
			accel_rate *= turn_boost_mult
		horiz_vel = horiz_vel.move_toward(clean_wish * target_speed, accel_rate * dt)
	elif is_on_floor():
		horiz_vel = horiz_vel.move_toward(Vector3.ZERO, ground_friction * dt)

	velocity.x = horiz_vel.x
	velocity.z = horiz_vel.z

	# 3. Jump execution (Coyote Time + Jump Buffer)
	if _jump_buffer_timer > 0.0 and _coyote_timer > 0.0:
		velocity.y = _jump_velocity
		_coyote_timer = 0.0
		_jump_buffer_timer = 0.0
		_is_jumping = true
		floor_snap_length = 0.0
	else:
		if is_on_floor():
			floor_snap_length = 0.25

		# Variable jump height cut on early button release
		if _is_jumping and velocity.y > 0.0 and not jump_held:
			velocity.y *= early_release_cut
			_is_jumping = false

		# Asymmetric gravity integration
		if not is_on_floor():
			var g := _gravity_up if velocity.y > 0.0 else _gravity_down
			velocity.y = maxf(velocity.y - g * dt, -terminal_fall_speed)

	move_and_slide()
