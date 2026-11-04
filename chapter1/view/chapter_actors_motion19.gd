extends "res://chapter1/view/chapter_actors_quality17.gd"
## Motion/art comparison only. KayKit CC0 is a reference, not final art approval.
const MINION_MODEL := "res://assets/actors/Skeleton_Minion.glb"
const MergeMinion=preload("res://presentation/skinned_mesh_batch.gd")
var _minion_merge=MergeMinion.new()
var _motion19_event := -1
var _minion_attacks: Dictionary={}
var motion19_samples := 0
func _create(kind: String) -> Node3D:
	if kind not in ["walker","elite"] or (kind=="elite" and view.run.zone==2):return super._create(kind)
	var actor := Node3D.new();actor.set_meta("kind",kind)
	var model: Node3D=load(MINION_MODEL).instantiate();model.scale=Vector3.ONE*(1.45 if kind=="elite" else 1.02);actor.add_child(model)
	var merged: Dictionary=_minion_merge.merge(model)
	var player: AnimationPlayer=model.find_child("AnimationPlayer",true,false)
	var skeleton: Skeleton3D=model.find_child("Skeleton3D",true,false)
	player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	var materials: Array[StandardMaterial3D]=[]
	_minion_materials(model,materials,kind)
	actor.set_meta("minion19",{"model":model,"player":player,"skeleton":skeleton,"materials":materials,"fade":1.0,"death_age":0.0,"clip":"","bucket":-1})
	player.play("Idle",0);player.seek(0,true);player.advance(0)
	if actors.is_empty():print("MOTION19_RIG ",JSON.stringify({"bones":skeleton.get_bone_count(),"merged":merged,"scope":"CC0 motion reference; final art unapproved"}))
	return actor
func _minion_materials(node: Node,materials: Array[StandardMaterial3D],kind: String) -> void:
	for child in node.get_children():
		if child is MeshInstance3D:
			child.layers=2
			for surface in child.mesh.get_surface_count():
				var source=child.get_active_material(surface) as StandardMaterial3D
				if source==null:continue
				var mat := source.duplicate() as StandardMaterial3D
				mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS;mat.roughness=.95
				var tint := Color(.65,.66,.59) if kind=="walker" else Color(.65,.48,.36)
				if source.resource_name=="Glow":tint=Color(.30,.40,.34) if kind=="walker" else Color(.65,.25,.08)
				mat.albedo_color=tint;mat.emission_enabled=false;mat.set_meta("motion19_tint",tint)
				child.set_surface_override_material(surface,mat);materials.append(mat)
		else:_minion_materials(child,materials,kind)
func consume(events: Array) -> void:
	for event in events:
		if int(event.seq)<=_motion19_event:continue
		_motion19_event=int(event.seq)
		if event.type=="enemy_attack":
			var e: Dictionary=view.run.enemies.get(event.target_id,{})
			_minion_attacks[event.target_id]={"tick":int(event.tick),"end":int(e.get("state_until",event.tick))}
	super.consume(events)
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	if not actor.has_meta("minion19"):
		super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast);return
	var entity := _entity(actor)
	if entity.is_empty():return
	var state: Dictionary=actor.get_meta("minion19")
	if not playing and not dead and not String(state.clip).is_empty():return
	var player: AnimationPlayer=state.player
	var fraction := clampf(Engine.get_physics_interpolation_fraction(),0,1) if playing else 0.0
	var clip := "Idle_Combat";var time_ := 0.0
	var attack := "2H_Melee_Attack_Chop" if entity.elite else "Unarmed_Melee_Attack_Punch_A"
	var release: float=player.get_animation(attack).length*.42
	if playing and direction.length_squared()>.001:actor.rotation.y=lerp_angle(actor.rotation.y,atan2(direction.x,direction.y),1-exp(-_render_delta*18))
	if dead:
		clip="Death_A"
		if view.run.mode not in ["paused","choice","inventory","equipment"]:state.death_age=maxf(float(state.death_age)+_render_delta,float(tick-int(entity.dead_tick))/60.0)
		time_=float(state.death_age)
	elif entity.state=="windup":
		clip=attack
		var duration: int=entity.get("definition",{}).get("windup",view.run.ENEMY_DEFS[entity.kind].windup)
		time_=release*clampf(1.0-(float(int(entity.state_until)-tick)-fraction)/maxf(1,duration),0,1)
	elif entity.state=="recover" and _minion_attacks.has(entity.id):
		clip=attack
		var paid: Dictionary=_minion_attacks[entity.id]
		var freeze_extension := maxi(0,int(entity.state_until)-int(paid.end))
		time_=release+maxf(0,float(tick-int(paid.tick)-freeze_extension)+fraction)/60.0
		if time_>=player.get_animation(clip).length:clip="Idle_Combat";time_=0
	elif moving:
		clip="Walking_D_Skeletons"
		var sample: Dictionary=actor.get_meta("motion_sample",{})
		var phase: float=float(sample.get("phase",0.0))+float((int(entity.id)*37)%101)/101.0
		time_=fposmod(phase,1)*player.get_animation(clip).length
	else:time_=fposmod(float(tick)/60.0+float(entity.id)*.113,player.get_animation(clip).length)
	# Far walking poses update at20Hz; planted attacks and death retain full rate.
	var near_: bool=entity.position.distance_squared_to(view.run.hero.position)<30.25
	var bucket: int=tick/3
	if moving and not near_ and state.clip==clip and int(state.bucket)==bucket:return
	state.clip=clip;state.bucket=bucket
	player.play(clip,0);player.seek(minf(time_,player.get_animation(clip).length),true);player.advance(0)
	actor.set_meta("minion19_pose",{"clip":clip,"time":time_,"dead":dead,"tick":tick});motion19_samples+=1
func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	for id_ in _minion_attacks.keys():
		if not run.enemies.has(id_):_minion_attacks.erase(id_)
	for key in actors:
		var actor: Node3D=actors[key]
		if not actor.has_meta("minion19"):continue
		var entity := _entity(actor)
		if entity.is_empty():continue
		var state: Dictionary=actor.get_meta("minion19")
		var alpha := 1.0
		if entity.hp_raw<=0:alpha=1-clampf((float(state.death_age)-.6)/.65,0,1)
		if _cold_corpses.has(key):
			var record: Dictionary=_cold_corpses[key]
			if run.mode not in ["paused","choice","inventory","equipment"]:record.age=maxf(float(record.age)+maxf(0,delta),float(run.tick-int(record.tick))/60.0)
			alpha*=1-smoothstep(.025,.22,float(record.age))
		for material in state.materials:
			var color: Color=material.get_meta("motion19_tint")
			if _cold_corpses.has(key) or (entity.hp_raw>0 and run.tick<int(entity.frozen_until)):color*=Color(.48,.86,1.16)
			elif run.tick<int(_enemy_hit_until.get(entity.id,-1))-9:color*=Color(1.3,1.2,1.05)
			color.a=alpha*float(state.fade);material.albedo_color=color
func _overlaps_hero(actor: Node3D,camera: Camera3D) -> bool:
	if not actor.has_meta("minion19"):return super._overlaps_hero(actor,camera)
	if camera==null or (actor.global_position-hero.global_position).dot(camera.global_basis.z)<=.04:return false
	var rig: Skeleton3D=actor.get_meta("minion19").skeleton
	var a := camera.unproject_position(_bone_point(rig,"hips"));var b := camera.unproject_position(_bone_point(rig,"head"))
	var ha := camera.unproject_position(hero.global_position+Vector3.UP*.32);var hb := camera.unproject_position(hero.global_position+Vector3.UP*1.95)
	var nearest := Geometry2D.get_closest_points_between_segments(a,b,ha,hb)
	var radius := _screen_radius(camera,actor.global_position+Vector3.UP,.40)+_screen_radius(camera,hero.global_position+Vector3.UP,.32)
	return nearest[0].distance_squared_to(nearest[1])<radius*radius
func _sync_hero_rim(camera: Camera3D,overlapping: bool) -> void:
	super._sync_hero_rim(camera,overlapping)
	for actor in actors.values():
		if not actor.has_meta("minion19"):continue
		var state: Dictionary=actor.get_meta("minion19")
		var target := .4 if overlapping and _overlaps_hero(actor,camera) else 1.0
		state.fade=lerpf(float(state.fade),target,1-exp(-_render_delta*18))
func reset() -> void:
	super.reset();_motion19_event=-1;_minion_attacks.clear();motion19_samples=0
