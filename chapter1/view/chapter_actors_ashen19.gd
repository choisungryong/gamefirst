extends "res://chapter1/view/chapter_actors_motion19.gd"
## Authored silhouette/material study on the CC0 rig; never final by test count.
func _create(kind: String) -> Node3D:
	var actor := super._create(kind)
	if not actor.has_meta("minion19"):return actor
	var state: Dictionary=actor.get_meta("minion19")
	for mat in state.materials:
		var tint := Color(.22,.25,.24) if kind=="walker" else Color(.31,.23,.16)
		if String(mat.resource_name).begins_with("Glow"):tint=Color(.06,.10,.08) if kind=="walker" else Color(.30,.07,.02)
		mat.albedo_color=tint;mat.set_meta("motion19_tint",tint);mat.rim_enabled=true;mat.rim=.18;mat.rim_tint=.2
	var rig: Skeleton3D=state.skeleton
	var attachment := BoneAttachment3D.new();attachment.bone_name="hips";rig.add_child(attachment)
	var cloth := MeshInstance3D.new();cloth.mesh=_rag_mesh();cloth.layers=2
	var mat := StandardMaterial3D.new();mat.albedo_color=Color("292b27");mat.roughness=1;mat.cull_mode=BaseMaterial3D.CULL_DISABLED
	cloth.material_override=mat
	var rest := rig.get_bone_global_rest(rig.find_bone("hips"))
	cloth.basis=rest.basis.inverse();attachment.add_child(cloth)
	return actor
func _rag_mesh() -> ArrayMesh:
	var st := SurfaceTool.new();st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for side in [-1,1]:
		for strip in 4:
			var x := -.19+strip*.095
			var a := Vector3(x,.04,side*.16);var b := Vector3(x+.10,.04,side*.16)
			var c := Vector3(x+.09,-.36-float(strip%2)*.10,side*.21)
			var d := Vector3(x,-.44+float(strip%3)*.03,side*.20)
			for point in [a,b,c,a,c,d]:st.add_vertex(point)
	st.generate_normals();return st.commit()
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast)
	if not actor.has_meta("minion19"):return
	var rig: Skeleton3D=actor.get_meta("minion19").skeleton
	rig.set_bone_pose_scale(rig.find_bone("head"),Vector3(.58,.74,.62))
