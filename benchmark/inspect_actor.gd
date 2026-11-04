extends SceneTree
func _initialize() -> void:
	call_deferred("run")
func inspect(node: Node) -> void:
	if node is MeshInstance3D:
		var bindings: Array = []
		if node.skin:
			for index in range(node.skin.get_bind_count()): bindings.append([node.skin.get_bind_bone(index),str(node.skin.get_bind_name(index)),str(node.skin.get_bind_pose(index))])
		print(JSON.stringify({"path":str(node.get_path()),"transform":str(node.transform),"surfaces":node.mesh.get_surface_count(),"skin":node.skin.get_instance_id() if node.skin else 0,"bindings":bindings,"skeleton":str(node.skeleton)}))
	for child in node.get_children(): inspect(child)
func run() -> void:
	var scene: PackedScene = load("res://assets/actors/Skeleton_Minion.glb")
	var actor: Node3D = scene.instantiate()
	root.add_child(actor)
	inspect(actor)
	actor.free()
	quit()
