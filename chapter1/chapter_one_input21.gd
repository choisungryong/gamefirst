extends "res://chapter1/chapter_one_view.gd"
## Full-chapter click targets use the same unlocked walkable bounds as movement.
## The archived representative scene keeps its original first-arena controller.
func _unhandled_input(event: InputEvent) -> void:
	if run.mode!="playing" or not event is InputEventMouseButton:return
	if event.button_index!=MOUSE_BUTTON_LEFT or not event.pressed:return
	var origin: Vector3=world.camera.project_ray_origin(event.position)
	var direction: Vector3=world.camera.project_ray_normal(event.position)
	var ground: Variant=Plane(Vector3.UP,0).intersects_ray(origin,direction)
	if ground is Vector3:
		_move_target=run._clamp_point(Vector2(ground.x,ground.z))
		_has_move_target=true;effects.move_marker(_move_target)
		get_viewport().set_input_as_handled()
