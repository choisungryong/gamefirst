extends "res://chapter1/view/chapter_actors_readable19.gd"
## Same authored skin/UV/bone data; one surface with baked body/mask tint.
## The original three materials all reference the same embedded diffuse image.
var _batch19_cache: Dictionary={}
func _create(kind: String) -> Node3D:
	var actor := super._create(kind)
	if actor.has_meta("minion19"):
		for mat in actor.get_meta("minion19").materials:
			if mat.resource_name=="Minion19Batched":
				mat.albedo_color=Color.WHITE;mat.set_meta("demon19_tint",Color.WHITE)
	return actor
func _demon19_materials(node: Node,materials: Array[StandardMaterial3D],kind: String) -> void:
	for child in node.get_children():
		if not child is MeshInstance3D:
			_demon19_materials(child,materials,kind);continue
		child.layers=2
		# Ordinary sprites never cast directional shadows either. Keep the final
		# Warden and hero on their existing independently shadowed presenters.
		child.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var signature := str(child.mesh.get_instance_id())+":"+kind
		if not _batch19_cache.has(signature):
			var combined: Array=[]
			var base: StandardMaterial3D
			for surface in child.mesh.get_surface_count():
				var source := child.get_active_material(surface) as StandardMaterial3D
				assert(source!=null)
				if source.resource_name.begins_with("WardenChain"):continue
				if base==null:base=source
				else:assert(base.albedo_texture.get_image().get_data()==source.albedo_texture.get_image().get_data())
				var arrays: Array=child.mesh.surface_get_arrays(surface).duplicate(true)
				var mask: bool=source.resource_name.begins_with("WardenMask")
				var tint := Color(.47,.46,.40) if kind=="walker" else Color(.39,.25,.20)
				if mask:tint=Color(.64,.60,.49) if kind=="walker" else Color(.84,.65,.40)
				var colors := PackedColorArray();colors.resize(arrays[Mesh.ARRAY_VERTEX].size());colors.fill(tint);arrays[Mesh.ARRAY_COLOR]=colors
				if combined.is_empty():combined=arrays;continue
				var offset: int=combined[Mesh.ARRAY_VERTEX].size()
				for slot in Mesh.ARRAY_MAX:
					if slot==Mesh.ARRAY_INDEX:
						for index in arrays[slot]:combined[slot].append(index+offset)
					elif arrays[slot]!=null:combined[slot].append_array(arrays[slot])
			var mesh := ArrayMesh.new();mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,combined)
			var mat := base.duplicate() as StandardMaterial3D
			mat.resource_name="Minion19Batched";mat.vertex_color_use_as_albedo=true;mat.vertex_color_is_srgb=true
			mat.albedo_color=Color.WHITE;mat.roughness=.9;mat.metallic=0;mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
			mesh.surface_set_material(0,mat);_batch19_cache[signature]=mesh
		child.mesh=_batch19_cache[signature]
		var mat := child.mesh.surface_get_material(0).duplicate() as StandardMaterial3D
		mat.set_meta("demon19_tint",Color.WHITE);child.set_surface_override_material(0,mat);materials.append(mat)
