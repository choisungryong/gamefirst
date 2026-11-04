extends RefCounted
## GUI-unhandled press and global release remain separate.
## https://docs.godotengine.org/en/4.5/classes/class_node.html#class-node-private-method-unhandled-input
var held := false
var queued_cast := false
var auto_cast := false

## Plane.intersects_ray returns null when the pointer ray misses the ground.
## https://docs.godotengine.org/en/4.5/classes/class_plane.html
static func ground_point(camera: Camera3D, screen: Vector2) -> Variant:
	return Plane(Vector3.UP,0.0).intersects_ray(camera.project_ray_origin(screen),camera.project_ray_normal(screen))

func destination_request(event: InputEvent, camera: Camera3D) -> Variant:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		return ground_point(camera,event.position)
	return null

func movement_world(camera: Camera3D) -> Vector2:
	var axis := Vector2(float(Input.is_physical_key_pressed(KEY_D))-float(Input.is_physical_key_pressed(KEY_A)),float(Input.is_physical_key_pressed(KEY_S))-float(Input.is_physical_key_pressed(KEY_W)))
	return world_movement(axis,camera)

static func world_movement(axis: Vector2, camera: Camera3D) -> Vector2:
	var movement: Vector3 = camera.global_basis.x*axis.x+camera.global_basis.z*axis.y
	return Vector2(movement.x,movement.z).normalized()

func unhandled(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_RIGHT:
		held = event.pressed
		if event.pressed: queued_cast = true

func global_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_RIGHT and not event.pressed:
		held = false

func clear() -> void:
	clear_pointer()
	auto_cast = false

func clear_pointer() -> void:
	held = false
	queued_cast = false

func toggle_auto() -> void:
	clear_pointer()
	auto_cast = not auto_cast

func consume() -> bool:
	var result := held or queued_cast
	queued_cast = false
	return result

## Input policy only. Both policies become the same boolean request in Sim.step.
## A deliberate pointer request wins over automatic aiming for that tick.
func consume_request(sim: RefCounted, pointer_aim: Vector2) -> Dictionary:
	if consume(): return {"cast":true,"aim":pointer_aim,"policy":"manual"}
	if not auto_cast: return {"cast":false,"aim":pointer_aim,"policy":"manual"}
	var target: Dictionary = sim.nearest_enemy(sim.player)
	if target.is_empty(): return {"cast":false,"aim":pointer_aim,"policy":"auto"}
	var definition: Dictionary = sim.skill_display()
	var range_: float = float(definition.get("range_world",0.0))
	if sim.player.distance_squared_to(target.p) > range_*range_:
		return {"cast":false,"aim":pointer_aim,"policy":"auto"}
	return {"cast":true,"aim":Vector2(target.p),"policy":"auto"}

