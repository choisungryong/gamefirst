extends RefCounted
## Static floor only. Actor rigs remain distinct and independently animated.
## Pattern based on prior courtyard; official property order before instance_count:
## https://docs.godotengine.org/en/4.5/classes/class_multimesh.html
static func collect(node: Node, owner: Node3D, groups: Dictionary) -> int:
	var count := 0
	if node is MeshInstance3D and node.mesh is ArrayMesh:
		var signature: String = str(node.mesh.get_instance_id())
		var materials: Array = []
		for surface in range(node.mesh.get_surface_count()):
			var active: Material = node.get_active_material(surface)
			materials.append(active)
			signature += ":"+str(active.get_instance_id() if active else 0)
		if not groups.has(signature): groups[signature] = {"mesh":node.mesh,"materials":materials,"transforms":[]}
		groups[signature].transforms.append(owner.global_transform.affine_inverse()*node.global_transform)
		count += 1
	for child in node.get_children(): count += collect(child,owner,groups)
	return count

static func batch(owner: Node3D, roots: Array[Node3D]) -> Dictionary:
	var groups: Dictionary = {}
	var count := 0
	for node in roots: count += collect(node,owner,groups)
	for group in groups.values():
		var mesh: ArrayMesh = group.mesh.duplicate()
		for surface in range(mesh.get_surface_count()): mesh.surface_set_material(surface,group.materials[surface])
		var multi := MultiMesh.new()
		multi.transform_format = MultiMesh.TRANSFORM_3D
		multi.mesh = mesh
		multi.instance_count = group.transforms.size()
		var bounds := AABB()
		for index in range(group.transforms.size()):
			var transform_: Transform3D = group.transforms[index]
			multi.set_instance_transform(index,transform_)
			var instance_bounds: AABB = transform_*mesh.get_aabb()
			bounds = instance_bounds if index == 0 else bounds.merge(instance_bounds)
		multi.custom_aabb = bounds
		var instance := MultiMeshInstance3D.new()
		instance.multimesh = multi
		owner.add_child(instance)
	for node in roots: node.free()
	return {"source_roots":roots.size(),"source_meshes":count,"batches":groups.size()}
