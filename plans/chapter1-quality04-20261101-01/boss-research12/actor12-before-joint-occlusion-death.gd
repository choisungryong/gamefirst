extends "res://chapter1/view/rigged_hero_actors.gd"
## Research integration: actual final-boss rig. Chapter11 remains archived.
## Source timing is explicitly mapped onto paid windup/release; never changes AI.
const WARDEN := "res://chapter1/art/chained_warden/v01/chained_demon_animated.glb"
const RELEASE_TICKS := 8
const RELEASE_TIME := .1375
var _entities: Dictionary={}
var _paid_attacks: Dictionary={}
var _warden_event := -1
var _warden_phase := 1

func _create(kind: String) -> Node3D:
	if kind!="elite" or view.run.zone!=2:return super._create(kind)
	var actor := Node3D.new();actor.set_meta("kind",kind)
	var model=load(WARDEN).instantiate();model.scale=Vector3.ONE*1.15;actor.add_child(model)
	var player: AnimationPlayer=model.find_child("AnimationPlayer",true,false)
	var skeleton: Skeleton3D=model.find_child("Skeleton3D",true,false)
	player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	var materials: Array[StandardMaterial3D]=[]
	_warden_materials(model,materials)
	actor.set_meta("enemy_rig",{"model":model,"player":player,"skeleton":skeleton,"materials":materials,"owner_fade":1.0})
	player.play("idle",0);player.seek(0,true);player.advance(0)
	print("CHAPTER1_WARDEN_RIG ",JSON.stringify({"bones":skeleton.get_bone_count(),"clips":Array(player.get_animation_list()),"source":WARDEN,"scope":"Own animations on Mophs CC-BY3.0 model; quality comparison candidate"}))
	return actor

func _warden_materials(node: Node,materials: Array[StandardMaterial3D]) -> void:
	for child in node.get_children():
		if child is MeshInstance3D:
			child.layers=2
			for surface in child.mesh.get_surface_count():
				var original=child.get_active_material(surface) as StandardMaterial3D
				if original:
					var material=original.duplicate() as StandardMaterial3D
					material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
					var tint := Color(.52,.55,.51)
					if original.resource_name.begins_with("WardenMask"):tint=Color(.74,.78,.81)
					elif original.resource_name.begins_with("WardenChain"):tint=Color(.56,.60,.63)
					material.albedo_color=tint;material.set_meta("warden_tint",tint)
					material.rim_enabled=true;material.rim=.24;material.rim_tint=.18
					child.set_surface_override_material(surface,material);materials.append(material)
		else:_warden_materials(child,materials)

func consume(events: Array) -> void:
	for event in events:
		if int(event.seq)<=_warden_event:continue
		_warden_event=int(event.seq)
		if event.type=="enemy_attack" and event.kind=="elite":
			var entity: Dictionary=view.run.enemies.get(event.target_id,{})
			_paid_attacks[event.target_id]={"tick":int(event.tick),"kind":event.attack_kind,"recover_end":int(entity.get("state_until",event.tick))}
		elif event.type=="boss_phase":_warden_phase=int(event.phase)
	super.consume(events)

func sync(run: RefCounted,delta: float) -> void:
	_entities.clear()
	for e in run.enemies.values():_entities["%d:%d"%[e.generation,e.id]]=e
	super.sync(run,delta)

func _entity(actor: Node3D) -> Dictionary:
	var key: String=actor.get_meta("entity_key","")
	if key.is_empty():
		for candidate in actors:
			if actors[candidate]==actor:key=candidate;actor.set_meta("entity_key",key);break
	return _entities.get(key,{})

func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	if not actor.has_meta("enemy_rig"):super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast);return
	var state: Dictionary=actor.get_meta("enemy_rig");var entity := _entity(actor)
	if entity.is_empty():return
	if actor.get_meta("warden_pose_ready",false) and not playing and not dead:return
	var player: AnimationPlayer=state.player
	var clip := "idle";var time_ := 0.0
	var fraction := clampf(Engine.get_physics_interpolation_fraction(),0,1) if playing else 0.0
	if playing and direction.length_squared()>.001:actor.rotation.y=lerp_angle(actor.rotation.y,atan2(direction.x,direction.y),1-exp(-_render_delta*18))
	if dead:
		clip="death";time_=maxf(0,float(tick-int(entity.dead_tick))/60.0)
	elif entity.state=="windup":
		var kind := "fan" if entity.attack_kind=="fan" else "slam"
		var left := maxf(0,float(int(entity.state_until)-tick)-fraction)
		if left>RELEASE_TICKS:
			clip="windup_"+kind
			var progress := clampf(1.0-(left-RELEASE_TICKS)/float(maxi(1,int(entity.definition.windup)-RELEASE_TICKS)),0,1)
			time_=progress*player.get_animation(clip).length
		else:clip=kind;time_=RELEASE_TIME*(1-left/RELEASE_TICKS)
	elif entity.state=="recover" and _paid_attacks.has(entity.id):
		var paid: Dictionary=_paid_attacks[entity.id]
		clip="fan" if paid.kind=="fan" else "slam"
		# The core extends recovery's end on each frozen tick. Remove that
		# extension so thaw resumes the held pose instead of skipping recovery.
		var frozen_ticks := maxi(0,int(entity.state_until)-int(paid.recover_end))
		time_=RELEASE_TIME+maxf(0,float(tick-int(paid.tick)-frozen_ticks)+fraction)/60.0
		if time_>=player.get_animation(clip).length:clip="idle";time_=fposmod(float(tick)/60.0,player.get_animation(clip).length)
	elif moving:
		clip="walk"
		var sample: Dictionary=actor.get_meta("motion_sample",{})
		var stride_step: float=Vector2(sample.get("previous",Vector2.ZERO)).distance_to(sample.get("current",Vector2.ZERO))/1.45
		var phase := fposmod(float(sample.get("phase",0.0))-(1-fraction)*stride_step,1)
		time_=phase*player.get_animation(clip).length
	else:time_=fposmod(float(tick)/60.0,player.get_animation("idle").length)
	player.play(clip,0);player.seek(minf(time_,player.get_animation(clip).length),true);player.advance(0)
	if hit:
		var hit_age := float(tick-(int(_enemy_hit_until.get(entity.id,-100))-12))
		if hit_age>=0 and hit_age<6:
			var rig: Skeleton3D=state.skeleton
			for name_ in ["Spine2","Head"]:
				var bone := rig.find_bone(name_)
				if bone>=0:rig.set_bone_pose_rotation(bone,rig.get_bone_pose_rotation(bone)*Quaternion(Vector3.RIGHT,-.06*sin(PI*hit_age/6)))
	actor.set_meta("warden_pose",{"clip":clip,"time":time_,"tick":tick,"state":entity.state})
	actor.set_meta("warden_pose_ready",true)

func _overlaps_hero(actor: Node3D,camera: Camera3D) -> bool:
	if not actor.has_meta("enemy_rig"):return super._overlaps_hero(actor,camera)
	if camera==null or (actor.global_position-hero.global_position).dot(camera.global_basis.z)<=.04:return false
	var first := true;var hero_rect := Rect2();var boss_rect := Rect2()
	for x in [-.85,.85]:
		for y in [0.0,2.5]:
			for z in [-.7,.7]:
				var p := camera.unproject_position(hero.global_transform*Vector3(x,y,z))
				if first:hero_rect=Rect2(p,Vector2.ZERO);first=false
				else:hero_rect=hero_rect.expand(p)
	first=true
	for x in [-1.7,1.7]:
		for y in [0.0,4.9]:
			for z in [-1.2,1.2]:
				var p := camera.unproject_position(actor.global_transform*Vector3(x,y,z))
				if first:boss_rect=Rect2(p,Vector2.ZERO);first=false
				else:boss_rect=boss_rect.expand(p)
	return hero_rect.intersects(boss_rect)

func _sync_hero_rim(camera: Camera3D,overlapping: bool) -> void:
	super._sync_hero_rim(camera,overlapping)
	for actor in actors.values():
		if not actor.has_meta("enemy_rig"):continue
		var state: Dictionary=actor.get_meta("enemy_rig");var entity := _entity(actor)
		var target := .32 if overlapping and _overlaps_hero(actor,camera) else 1.0
		state.owner_fade=lerpf(state.owner_fade,target,1-exp(-_render_delta*18))
		if state.owner_fade>.995:state.owner_fade=1.0
		var corpse_alpha := 1.0
		if not entity.is_empty() and entity.hp_raw<=0:corpse_alpha=1.0-clampf(float(view.run.tick-int(entity.dead_tick)-36)/39.0,0,1)
		for material in state.materials:
			var color: Color=material.get_meta("warden_tint",Color(.52,.55,.51))
			if not entity.is_empty() and entity.hp_raw>0 and view.run.tick<int(entity.frozen_until):color*=Color(.60,.90,1.16)
			elif _warden_phase>=2:color*=Color(1.03,.89,.88)
			color.a=state.owner_fade*corpse_alpha;material.albedo_color=color

func reset() -> void:
	super.reset();_entities.clear();_paid_attacks.clear();_warden_event=-1;_warden_phase=1
