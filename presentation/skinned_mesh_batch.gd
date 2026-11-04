extends RefCounted
## Narrow immutable merge: same Skeleton3D, same Skin, identity transforms only.
## https://docs.godotengine.org/en/4.5/classes/class_arraymesh.html
## Positions/UVs/bone indices/weights stay in source order. Godot re-encodes
## normal/tangent octahedral uint16 values when constructing ArrayMesh surfaces.
var cache: Dictionary = {}

func merge(actor: Node3D) -> Dictionary:
	var skeleton: Skeleton3D = find_skeleton(actor)
	if not skeleton: return {"merged":false}
	var meshes: Array[MeshInstance3D] = []
	for child in skeleton.get_children():
		if child is MeshInstance3D: meshes.append(child)
	if meshes.size() <= 1: return {"merged":false}
	var skin: Skin = meshes[0].skin
	var signature := ""
	var groups: Dictionary = {}
	var vertices := 0
	var indices := 0
	for instance in meshes:
		if instance.skin != skin or instance.skeleton != NodePath("..") or not instance.transform.is_equal_approx(Transform3D.IDENTITY) or instance.mesh.get_blend_shape_count() > 0:
			return {"merged":false,"reason":"incompatible skin, transform or blendshape"}
		signature += str(instance.mesh.get_instance_id())+":"
		for surface in range(instance.mesh.get_surface_count()):
			if instance.mesh.surface_get_primitive_type(surface) != Mesh.PRIMITIVE_TRIANGLES: return {"merged":false,"reason":"non-triangle source"}
			var active: Material = instance.get_active_material(surface)
			var key_: int = active.get_instance_id() if active else 0
			signature += str(key_)+":"
			if not groups.has(key_): groups[key_] = {"material":active,"arrays":[],"format":instance.mesh.surface_get_format(surface)}
			if groups[key_].format != instance.mesh.surface_get_format(surface): return {"merged":false,"reason":"incompatible surface formats"}
			var source: Array = instance.mesh.surface_get_arrays(surface)
			vertices += source[Mesh.ARRAY_VERTEX].size()
			indices += source[Mesh.ARRAY_INDEX].size()
			groups[key_].arrays.append(source)
	var merged: ArrayMesh
	if cache.has(signature): merged = cache[signature]
	else:
		merged = ArrayMesh.new()
		for group in groups.values():
			var combined: Array = []
			for source in group.arrays:
				if combined.is_empty():
					combined = source.duplicate(true)
					continue
				var offset: int = combined[Mesh.ARRAY_VERTEX].size()
				for slot in range(Mesh.ARRAY_MAX):
					if slot == Mesh.ARRAY_INDEX:
						for index in source[slot]: combined[slot].append(index+offset)
					elif source[slot] != null: combined[slot].append_array(source[slot])
			merged.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,combined)
			merged.surface_set_material(merged.get_surface_count()-1,group.material)
		cache[signature] = merged
	var node := MeshInstance3D.new()
	node.name = "MergedProxy"
	node.mesh = merged
	node.skin = skin
	node.skeleton = NodePath("..")
	node.cast_shadow = meshes[0].cast_shadow
	node.layers = meshes[0].layers
	skeleton.add_child(node)
	for instance in meshes: instance.free()
	return {"merged":true,"source_meshes":meshes.size(),"surfaces":merged.get_surface_count(),"vertices":vertices,"indices":indices}

func find_skeleton(node: Node) -> Skeleton3D:
	if node is Skeleton3D: return node
	for child in node.get_children():
		var found: Skeleton3D = find_skeleton(child)
		if found: return found
	return null
