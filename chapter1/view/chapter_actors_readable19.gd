extends "res://chapter1/view/chapter_actors_demon19.gd"
## Material and silhouette refinement; all combat remains owned by the core.
func _create(kind: String) -> Node3D:
	var actor := super._create(kind)
	if not actor.has_meta("minion19"):return actor
	var state: Dictionary=actor.get_meta("minion19")
	for mat in state.materials:
		var mask: bool=String(mat.resource_name).begins_with("WardenMask")
		var tint := Color(.47,.46,.40) if kind=="walker" else Color(.39,.25,.20)
		if mask:tint=Color(.64,.60,.49) if kind=="walker" else Color(.84,.65,.40)
		mat.albedo_color=tint;mat.set_meta("demon19_tint",tint)
		mat.rim_enabled=true;mat.rim=.22;mat.rim_tint=.15
	if kind=="elite":_shoulders(state)
	return actor
func _shoulders(state: Dictionary) -> void:
	var rig: Skeleton3D=state.skeleton
	var bone := rig.find_bone("Spine1")
	assert(bone>=0)
	var attachment := BoneAttachment3D.new();attachment.bone_name="Spine1";rig.add_child(attachment)
	var armor := Node3D.new();armor.basis=rig.get_bone_global_rest(bone).basis.inverse();attachment.add_child(armor)
	var mat := StandardMaterial3D.new();mat.albedo_color=Color(.26,.23,.19);mat.roughness=.7;mat.metallic=.45
	mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS;mat.set_meta("demon19_tint",mat.albedo_color);state.materials.append(mat)
	for side in [-1,1]:
		var plate := MeshInstance3D.new();var sphere := SphereMesh.new();sphere.radius=.35;sphere.height=.7;sphere.radial_segments=8;sphere.rings=4
		plate.mesh=sphere;plate.scale=Vector3(1,.38,.86);plate.position=Vector3(side*.66,.54,0);plate.material_override=mat;plate.layers=2;armor.add_child(plate)
		var horn := MeshInstance3D.new();var cone := CylinderMesh.new();cone.top_radius=0;cone.bottom_radius=.13;cone.height=.54;cone.radial_segments=6
		horn.mesh=cone;horn.position=Vector3(side*.86,.80,0);horn.rotation.z=-side*.5;horn.material_override=mat;horn.layers=2;armor.add_child(horn)
