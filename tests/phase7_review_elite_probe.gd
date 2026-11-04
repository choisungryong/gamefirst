extends SceneTree
var failures: Array[String] = []
func _initialize() -> void:
	call_deferred("run")
func require(value: bool, message: String) -> void:
	if not value: failures.append(message)
func run() -> void:
	var scene = load("res://Expedition.tscn").instantiate()
	root.add_child(scene)
	await process_frame
	scene.start_run()
	scene.set_physics_process(false)
	scene.set_process(false)
	var enemy: Dictionary = scene.sim.enemies.values()[0]
	var identity: Dictionary = scene.sim.handle(enemy)
	var key: String = scene.actor_registry.key(enemy)
	var actor: Node3D = scene.actor_registry.actors[key]
	var original_scale: Vector3 = actor.scale
	var original_materials: Array = materials(actor)
	scene.controller.elite_identity = identity
	scene.sync_actors()
	require(actor.scale.is_equal_approx(Vector3.ONE*1.48),"synthetic elite fixture must be visibly enlarged")
	scene.restart()
	var fresh: Dictionary = scene.sim.enemies.values()[0]
	var rebound: Node3D = scene.actor_registry.actors[scene.actor_registry.key(fresh)]
	require(actor==rebound,"fixture must reuse the same primary actor")
	require(rebound.scale.is_equal_approx(original_scale),"ordinary actor must recover original scale after elite reset/rebind")
	require(materials(rebound)==original_materials,"ordinary actor must recover original material resources after elite reset/rebind")
	print(JSON.stringify({"success":failures.is_empty(),"failures":failures,"before_scale":[original_scale.x,original_scale.y,original_scale.z],"after_scale":[rebound.scale.x,rebound.scale.y,rebound.scale.z],"scope":"Explicit synthetic elite identity and actual scene restart; no GPU claim"}))
	scene.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
func materials(node: Node) -> Array:
	var result: Array = []
	if node is MeshInstance3D:
		for i in range(node.mesh.get_surface_count()): result.append(node.get_active_material(i))
	for child in node.get_children(): result.append_array(materials(child))
	return result
