extends "res://chapter1/view/chapter_actors_quality20.gd"
var _staff21_mesh: ArrayMesh
var _staff21_material: StandardMaterial3D
## Two further roles share the proven skin batch, retaining their actual AI.
func _create(kind: String) -> Node3D:
	if kind not in ["ranged","charger"]:return super._create(kind)
	var actor := super._create("walker");actor.set_meta("kind",kind)
	var state: Dictionary=actor.get_meta("minion19")
	state.model.scale=Vector3(.44,.58,.44) if kind=="ranged" else Vector3(.72,.48,.72)
	for mat in state.materials:
		var tint := Color(.72,.94,1.10) if kind=="ranged" else Color(.86,.60,.43)
		mat.albedo_color=tint;mat.set_meta("demon19_tint",tint)
	if kind=="ranged":_staff21(state)
	actor.set_meta("role21",kind)
	return actor
func _staff21(state: Dictionary) -> void:
	var rig: Skeleton3D=state.skeleton
	var index := rig.find_bone("Hand.R");assert(index>=0)
	# Hand translation follows the actual pose, while the held shaft remains
	# upright instead of inheriting the wrist's near-camera pointing rotation.
	var staff := Node3D.new();staff.name="CasterStaff21";staff.scale=state.model.scale;state.model.get_parent().add_child(staff);state.staff21=staff
	if _staff21_mesh==null:_build_staff21()
	var mesh := MeshInstance3D.new();mesh.name="StaffMesh";mesh.mesh=_staff21_mesh;mesh.layers=2;mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var mat := _staff21_material.duplicate() as StandardMaterial3D;mat.set_meta("demon19_tint",Color.WHITE);mesh.material_override=mat;state.materials.append(mat);staff.add_child(mesh)
func _build_staff21() -> void:
	var cylinder := CylinderMesh.new();cylinder.top_radius=.075;cylinder.bottom_radius=.09;cylinder.height=3.2;cylinder.radial_segments=6
	var prism := PrismMesh.new();prism.size=Vector3(.44,.70,.44)
	var combined: Array=[]
	for part in [{"mesh":cylinder,"y":.55,"color":Color(.22,.24,.23),"uv":Vector2(.25,.5)},{"mesh":prism,"y":2.4,"color":Color(.35,.67,.70),"uv":Vector2(.75,.5)}]:
		var arrays: Array=part.mesh.surface_get_arrays(0).duplicate(true)
		for i in arrays[Mesh.ARRAY_VERTEX].size():arrays[Mesh.ARRAY_VERTEX][i]+=Vector3(0,part.y,0)
		var colors := PackedColorArray();colors.resize(arrays[Mesh.ARRAY_VERTEX].size());colors.fill(part.color);arrays[Mesh.ARRAY_COLOR]=colors
		var uv := PackedVector2Array();uv.resize(colors.size());uv.fill(part.uv);arrays[Mesh.ARRAY_TEX_UV]=uv
		if combined.is_empty():combined=arrays;continue
		var offset: int=combined[Mesh.ARRAY_VERTEX].size()
		for slot in Mesh.ARRAY_MAX:
			if slot==Mesh.ARRAY_INDEX:
				for value in arrays[slot]:combined[slot].append(value+offset)
			elif arrays[slot]!=null:combined[slot].append_array(arrays[slot])
	_staff21_mesh=ArrayMesh.new();_staff21_mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,combined)
	var image := Image.create(2,1,false,Image.FORMAT_RGBA8);image.set_pixel(0,0,Color.BLACK);image.set_pixel(1,0,Color(.15,.45,.50))
	_staff21_material=StandardMaterial3D.new();_staff21_material.vertex_color_use_as_albedo=true;_staff21_material.vertex_color_is_srgb=true;_staff21_material.albedo_color=Color.WHITE;_staff21_material.roughness=.85
	_staff21_material.emission_enabled=true;_staff21_material.emission=Color.WHITE;_staff21_material.emission_energy_multiplier=.35;_staff21_material.emission_texture=ImageTexture.create_from_image(image);_staff21_material.texture_filter=BaseMaterial3D.TEXTURE_FILTER_NEAREST;_staff21_material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	if actor.has_meta("role21") and playing and moving and not dead:
		var entity := _entity(actor)
		if not entity.is_empty() and entity.position.distance_squared_to(view.run.hero.position)>9:
			var bucket: int=tick/3
			if int(actor.get_meta("role21_bucket",-1))==bucket:
				if direction.length_squared()>.001:actor.rotation.y=lerp_angle(actor.rotation.y,atan2(direction.x,direction.y),1-exp(-_render_delta*18))
				return
			actor.set_meta("role21_bucket",bucket)
	super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast)
	if not actor.has_meta("role21"):return
	var e := _entity(actor)
	if e.is_empty():return
	var state: Dictionary=actor.get_meta("minion19")
	if actor.get_meta("role21")=="ranged":
		var pose: Dictionary=actor.get_meta("minion19_pose",{})
		if state.get("staff21_time",-1.0)!=pose.get("time",0.0) or state.get("staff21_clip","")!=pose.get("clip",""):
			state.staff21.position=actor.to_local(_bone_point(state.skeleton,"Hand.R"));state.staff21_time=pose.get("time",0.0);state.staff21_clip=pose.get("clip","")
		return
	if not playing or dead:return
	if actor.get_meta("role21")=="charger":
		var lean := .48 if e.state=="dash" else (-.14 if e.state=="windup" else 0.0)
		state.model.rotation.x=lerpf(state.model.rotation.x,lean,1-exp(-_render_delta*20))
		if e.state=="dash":
			var player: AnimationPlayer=state.player
			var phase := fposmod(float(tick-int(e.state_until)+32)/60.0*2.4,1)
			player.play("walk",0);player.seek(phase*player.get_animation("walk").length,true);player.advance(0)
			actor.set_meta("minion19_pose",{"clip":"walk","time":phase*player.get_animation("walk").length,"dead":false,"tick":tick})
			actor.set_meta("role21_dash",{"tick":tick,"phase":phase,"paid_direction":e.attack_direction})
		elif e.state=="recover":
			var player: AnimationPlayer=state.player
			var definition: Dictionary=view.run._enemy_definition(e)
			var time_ := maxf(0,float(tick-int(e.state_until)+int(definition.recover)))/60.0
			player.play("idle",0);player.seek(minf(time_,player.get_animation("idle").length),true);player.advance(0)
			actor.set_meta("minion19_pose",{"clip":"idle","time":time_,"dead":false,"tick":tick})
