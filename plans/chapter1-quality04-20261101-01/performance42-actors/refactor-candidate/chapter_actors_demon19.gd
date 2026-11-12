extends "res://chapter1/view/chapter_actors_quality17.gd"
## Independent creature-family study on the already licensed Mophs model.
## Ordinary bodies omit chain geometry; boss keeps its original mesh/presenter.
var _body_cache: Dictionary={}
var _demon19_attacks: Dictionary={}
var _demon19_event := -1
var motion19_samples := 0
func _create(kind: String) -> Node3D:
	if kind not in ["walker","elite"] or (kind=="elite" and view.run.zone==2):return super._create(kind)
	var actor := Node3D.new();actor.set_meta("kind",kind)
	var model: Node3D=load(WARDEN).instantiate();model.scale=Vector3.ONE*(.80 if kind=="elite" else .52);actor.add_child(model)
	var player: AnimationPlayer=model.find_child("AnimationPlayer",true,false)
	var rig: Skeleton3D=model.find_child("Skeleton3D",true,false)
	player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	var materials: Array[StandardMaterial3D]=[]
	_demon19_materials(model,materials,kind)
	actor.set_meta("minion19",{"model":model,"player":player,"skeleton":rig,"materials":materials,"fade":1.0,"death_age":0.0,"clip":"","bucket":-1})
	player.play("idle",0);player.seek(0,true);player.advance(0)
	return actor
func _demon19_materials(node: Node,materials: Array[StandardMaterial3D],kind: String) -> void:
	for child in node.get_children():
		if child is MeshInstance3D:
			child.layers=2
			var signature: int=child.mesh.get_instance_id()
			if not _body_cache.has(signature):
				var body := ArrayMesh.new()
				for surface in child.mesh.get_surface_count():
					var source=child.get_active_material(surface) as StandardMaterial3D
					if source and source.resource_name.begins_with("WardenChain"):continue
					body.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,child.mesh.surface_get_arrays(surface))
					body.surface_set_material(body.get_surface_count()-1,source)
				_body_cache[signature]=body
			child.mesh=_body_cache[signature]
			for surface in child.mesh.get_surface_count():
				var source=child.mesh.surface_get_material(surface) as StandardMaterial3D
				if source==null:continue
				var mat := source.duplicate() as StandardMaterial3D
				var tint := Color(.36,.42,.39) if kind=="walker" else Color(.48,.32,.24)
				if source.resource_name.begins_with("WardenMask"):tint=Color(.42,.46,.42) if kind=="walker" else Color(.72,.54,.38)
				mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS;mat.roughness=.9;mat.metallic=0
				mat.albedo_color=tint;mat.set_meta("demon19_tint",tint);child.set_surface_override_material(surface,mat);materials.append(mat)
		else:_demon19_materials(child,materials,kind)
func consume(events: Array) -> void:
	for event in events:
		if int(event.seq)<=_demon19_event:continue
		_demon19_event=int(event.seq)
		if event.type=="enemy_attack":
			var e: Dictionary=view.run.enemies.get(event.target_id,{})
			_demon19_attacks[event.target_id]={"tick":int(event.tick),"end":int(e.get("state_until",event.tick)),"kind":event.get("attack_kind","")}
	super.consume(events)
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	if not actor.has_meta("minion19"):
		super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast);return
	var e := _entity(actor)
	if e.is_empty():return
	var state: Dictionary=actor.get_meta("minion19")
	if not playing and not dead and not String(state.clip).is_empty():return
	var player: AnimationPlayer=state.player
	var fraction := clampf(Engine.get_physics_interpolation_fraction(),0,1) if playing else 0.0
	if playing and direction.length_squared()>.001:actor.rotation.y=lerp_angle(actor.rotation.y,atan2(direction.x,direction.y),1-exp(-_render_delta*18))
	var clip := "idle";var time_ := 0.0
	if dead:
		clip="death"
		if view.run.mode not in ["paused","choice","inventory","equipment"]:state.death_age=maxf(float(state.death_age)+_render_delta,float(tick-int(e.dead_tick))/60.0)
		time_=state.death_age
	elif e.state=="windup":
		var kind_ := "fan" if e.attack_kind in ["fan","frost_cross"] else "slam"
		var left := maxf(0,float(int(e.state_until)-tick)-fraction)
		var duration: int=e.get("definition",{}).get("windup",view.run.ENEMY_DEFS[e.kind].windup)
		if left>6:
			clip="windup_"+kind_;time_=clampf(1-(left-6)/float(maxi(1,duration-6)),0,1)*player.get_animation(clip).length
		else:clip=kind_;time_=RELEASE_TIME*(1-left/6.0)
	elif e.state=="recover" and _demon19_attacks.has(e.id):
		var paid: Dictionary=_demon19_attacks[e.id]
		clip="fan" if paid.kind in ["fan","frost_cross"] else "slam"
		var frozen_extension := maxi(0,int(e.state_until)-int(paid.end))
		time_=RELEASE_TIME+maxf(0,float(tick-int(paid.tick)-frozen_extension)+fraction)/60.0
		if time_>=player.get_animation(clip).length:clip="idle";time_=0
	elif moving:
		clip="walk"
		var sample: Dictionary=actor.get_meta("motion_sample",{})
		var phase: float=float(sample.get("phase",0.0))+float((int(e.id)*37)%101)/101.0
		time_=fposmod(phase,1)*player.get_animation(clip).length
	else:time_=fposmod(float(tick)/60.0+float(e.id)*.113,player.get_animation(clip).length)
	var near_: bool=e.position.distance_squared_to(view.run.hero.position)<30.25
	var bucket: int=tick/3
	if moving and not near_ and state.clip==clip and int(state.bucket)==bucket:return
	state.clip=clip;state.bucket=bucket
	_sample_actor42(player,clip,minf(time_,player.get_animation(clip).length))
	actor.set_meta("minion19_pose",{"clip":clip,"time":time_,"dead":dead,"tick":tick});motion19_samples+=1
func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	for id_ in _demon19_attacks.keys():
		if not run.enemies.has(id_):_demon19_attacks.erase(id_)
	for key in actors:
		var actor: Node3D=actors[key]
		if not actor.has_meta("minion19"):continue
		var e := _entity(actor)
		if e.is_empty():continue
		var state: Dictionary=actor.get_meta("minion19")
		var alpha := 1.0
		if e.hp_raw<=0:alpha=1-clampf((float(state.death_age)-.6)/.65,0,1)
		if _cold_corpses.has(key):
			var record: Dictionary=_cold_corpses[key]
			if run.mode not in ["paused","choice","inventory","equipment"]:record.age=maxf(float(record.age)+maxf(0,delta),float(run.tick-int(record.tick))/60.0)
			alpha*=1-smoothstep(.025,.22,float(record.age))
		for mat in state.materials:
			var color: Color=mat.get_meta("demon19_tint")
			if _cold_corpses.has(key) or (e.hp_raw>0 and run.tick<int(e.frozen_until)):color*=Color(.48,.86,1.16)
			elif run.tick<int(_enemy_hit_until.get(e.id,-1))-9:color*=Color(1.3,1.2,1.05)
			color.a=alpha*float(state.fade);_set_color42(mat,color)
func _overlaps_hero(actor: Node3D,camera: Camera3D) -> bool:
	if not actor.has_meta("minion19"):return super._overlaps_hero(actor,camera)
	if camera==null or (actor.global_position-hero.global_position).dot(camera.global_basis.z)<=.04:return false
	var rig: Skeleton3D=actor.get_meta("minion19").skeleton
	var a := camera.unproject_position(_bone_point(rig,"Spine1"));var b := camera.unproject_position(_bone_point(rig,"Head"))
	var ha := camera.unproject_position(hero.global_position+Vector3.UP*.32);var hb := camera.unproject_position(hero.global_position+Vector3.UP*1.95)
	var nearest := Geometry2D.get_closest_points_between_segments(a,b,ha,hb)
	var radius := _screen_radius(camera,actor.global_position+Vector3.UP,.42)+_screen_radius(camera,hero.global_position+Vector3.UP,.32)
	return nearest[0].distance_squared_to(nearest[1])<radius*radius
func _sync_hero_rim(camera: Camera3D,overlapping: bool) -> void:
	super._sync_hero_rim(camera,overlapping)
	for actor in actors.values():
		if not actor.has_meta("minion19"):continue
		var state: Dictionary=actor.get_meta("minion19")
		state.fade=lerpf(float(state.fade),.4 if overlapping and _overlaps_hero(actor,camera) else 1.0,1-exp(-_render_delta*18))
func reset() -> void:
	super.reset();_demon19_event=-1;_demon19_attacks.clear();motion19_samples=0

## Default hook preserves legacy sampling exactly; only Actor42 overrides it.
func _sample_actor42(player: AnimationPlayer,clip: String,time_: float) -> void:
	player.play(clip,0);player.seek(time_,true);player.advance(0)

func _set_color42(material: StandardMaterial3D,color: Color) -> void:
	material.albedo_color=color
