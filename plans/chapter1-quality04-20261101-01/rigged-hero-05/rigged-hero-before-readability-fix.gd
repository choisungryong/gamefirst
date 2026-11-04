extends "res://chapter1/view/chapter_actors.gd"
## Research presenter: actual skeleton, distance gait and upper-body release.
## No physics/hitbox/skill/loot changes. Source09 sprite presenter is preserved.
const MODEL := "res://chapter1/art/rigged_mage/v01/mage_animated.glb"
const Staff=preload("res://chapter1/view/ember_staff_visual.gd")
var rig_model: Node3D
var rig_player: AnimationPlayer
var rig_skeleton: Skeleton3D
var _upper: Dictionary={}
var _render_delta := 0.0
var _render_playing := false
var _phase := 0.0
var _idle_age := 0.0
var _death_age := 0.0
var _was_dead := false
var _hero_rect := Rect2()
var _bounds_frame := -1
var _pose_samples := 0
var _staff: Node3D
var _hand := -1
var _finger := -1
var _grip_basis := Basis.IDENTITY
var _grip_ready := false

func _load_sprite(kind: String) -> void:
	if kind!="hero":super._load_sprite(kind)

func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	_setup_artist_lights()
	_staff=Staff.new();hero.add_child(_staff)
	_hand=rig_skeleton.find_bone("hand_cr_r");_finger=rig_skeleton.find_bone("finger_middle.01.r")
	_sample("idle",0)
	temporary_art=false
	print("RIGGED_HERO_READY ",JSON.stringify({"source":MODEL,"bones":rig_skeleton.get_bone_count(),"clips":Array(rig_player.get_animation_list()),"upper_body_bones":_upper.size(),"scope":"Research comparison, not final motion/art approval"}))

func _setup_artist_lights() -> void:
	# Sprite art carries baked light. Give the live mesh a matched key/fill on
	# a separate visual layer, without adding a moving light patch to terrain.
	for pair in [[Vector3(-42,-35,0),Color("eddbc4"),1.6],[Vector3(-28,145,0),Color("7faad8"),.85]]:
		var light := DirectionalLight3D.new();light.rotation_degrees=pair[0];light.light_color=pair[1];light.light_energy=pair[2];light.light_cull_mask=2;light.shadow_enabled=false
		view.add_child(light)

func _create(kind: String) -> Node3D:
	if kind!="hero":
		var enemy := super._create(kind)
		if enemy.has_meta("sprite"):
			var sprite: AnimatedSprite3D=enemy.get_meta("sprite")
			# Hidden hero fragments need the enemy's opaque pixels in scene depth.
			# Preserve smooth fractional-alpha edges, unlike a hard cutout.
			sprite.alpha_cut=SpriteBase3D.ALPHA_CUT_OPAQUE_PREPASS
		return enemy
	var actor := Node3D.new();actor.set_meta("kind","hero")
	var scene := load(MODEL) as PackedScene
	if scene==null:push_error("Rigged hero import missing");return actor
	rig_model=scene.instantiate();actor.add_child(rig_model)
	rig_player=rig_model.find_child("AnimationPlayer",true,false)
	rig_skeleton=rig_model.find_child("Skeleton3D",true,false)
	if rig_player==null or rig_skeleton==null:push_error("Rigged hero skeleton/animations missing");return actor
	rig_player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	for i in rig_skeleton.get_bone_count():
		var name_: String=rig_skeleton.get_bone_name(i)
		if name_.begins_with("spine_") or name_.begins_with("neck_") or name_.begins_with("head_") or name_.contains("arm_") or name_.begins_with("shoulder_") or name_.begins_with("hand_") or name_.begins_with("finger_") or name_.begins_with("thumb."):_upper[i]=true
	_setup_materials(rig_model)
	return actor

func _setup_materials(node: Node) -> void:
	for child in node.get_children():
		if child is MeshInstance3D:
			var original: MeshInstance3D=child
			original.layers=2
			for surface in original.mesh.get_surface_count():
				var source := original.get_active_material(surface) as StandardMaterial3D
				if source:
					var material := source.duplicate() as StandardMaterial3D
					material.albedo_color=Color(1.35,1.25,1.18);material.rim_enabled=true;material.rim=.28;material.rim_tint=.25
					original.set_surface_override_material(surface,material)
		else:_setup_materials(child)

func sync(run: RefCounted,delta: float) -> void:
	_render_delta=delta;_render_playing=run.mode=="playing"
	super.sync(run,delta)
	if _staff!=null and _hand>=0 and _finger>=0:
		var hand := rig_skeleton.global_transform*rig_skeleton.get_bone_global_pose(_hand)
		var finger := rig_skeleton.global_transform*rig_skeleton.get_bone_global_pose(_finger)
		_staff.global_position=hand.origin.lerp(finger.origin,.5)
		if not _grip_ready:_grip_basis=hand.basis.orthonormalized().inverse()*hero.global_basis;_grip_ready=true
		if run.hero.hp_raw<=0:_staff.global_basis=(hand.basis.orthonormalized()*_grip_basis).orthonormalized()
		else:_staff.basis=Basis.from_euler(Vector3(deg_to_rad(-3+sin(_phase*TAU)*4),0,deg_to_rad(5)))
		var bottom: Vector3=_staff.global_transform*Vector3(0,-1.05,0)
		if bottom.y<.025:_staff.global_position.y+=.025-bottom.y
		var color: Color={"chapter1.skill.ember":Color("ed913e"),"chapter1.skill.frost":Color("89dbe6"),"chapter1.skill.arc":Color("a3b8ef")}.get(run.growth.snapshot().get("primary",""),Color("89dbe6"))
		_staff.set_element(color,clampf(1.0-float(run.tick-_cast_tick)/8.0,0,1))

func _sample(clip: String,time_: float) -> Array[Transform3D]:
	rig_player.play(clip,0.0)
	rig_player.seek(time_,true)
	rig_player.advance(0)
	var values: Array[Transform3D]=[]
	for i in rig_skeleton.get_bone_count():values.append(rig_skeleton.get_bone_pose(i))
	_pose_samples+=1
	return values

func _write_pose(values: Array[Transform3D]) -> void:
	for i in values.size():rig_skeleton.set_bone_pose(i,values[i])

func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	if actor!=hero:super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast);return
	if rig_player==null:return
	if dead:
		if not _was_dead:_death_age=0
		_was_dead=true;_death_age=minf(.9,_death_age+_render_delta)
		_sample("death",_death_age);return
	_was_dead=false
	if _render_playing:
		_idle_age+=_render_delta
		var facing := direction
		if not moving and casting:facing=_cast_direction
		if facing.length_squared()>.001:actor.rotation.y=lerp_angle(actor.rotation.y,atan2(facing.x,facing.y),1.0-exp(-_render_delta*20))
		if moving:
			var sample: Dictionary=actor.get_meta("motion_sample",{})
			var fraction := clampf(Engine.get_physics_interpolation_fraction(),0,1)
			var stride_step: float=Vector2(sample.get("previous",Vector2.ZERO)).distance_to(sample.get("current",Vector2.ZERO))/HERO_STRIDE
			_phase=fposmod(float(sample.get("phase",0.0))-(1.0-fraction)*stride_step,1)
	var poses := _sample("run" if moving else "idle",_phase*.6 if moving else fposmod(_idle_age,1.2))
	if casting:
		var age := clampf(float(tick-_cast_tick)/60.0,0,.2)
		var released := _sample("cast",.15+age*2.25)
		var weight := 1.0-smoothstep(.04,.2,age)
		for i in poses.size():
			if _upper.has(i):poses[i]=poses[i].interpolate_with(released[i],weight)
	if hit:
		var age := clampf(float(tick-(_hit_until-6))/60.0,0,.1)
		var struck := _sample("hit",age*3)
		for i in poses.size():
			if _upper.has(i):poses[i]=poses[i].interpolate_with(struck[i],.55*sin(PI*age/.1))
	_write_pose(poses)

func _overlaps_hero(actor: Node3D,camera: Camera3D) -> bool:
	if camera==null or not actor.has_meta("sprite"):return false
	if (actor.global_position-hero.global_position).dot(camera.global_basis.z)<=.04:return false
	if _bounds_frame!=Engine.get_process_frames():
		_bounds_frame=Engine.get_process_frames()
		var first := true
		for x in [-.85,.85]:
			for y in [0.0,2.35]:
				for z in [-.7,.7]:
					var screen := camera.unproject_position(hero.global_transform*Vector3(x,y,z))
					if first:_hero_rect=Rect2(screen,Vector2.ZERO);first=false
					else:_hero_rect=_hero_rect.expand(screen)
	return _hero_rect.intersects(_projected_frame(actor,camera))

func _sync_hero_rim(camera: Camera3D,overlapping: bool) -> void:
	# Fade only nearer enemy sprites that cover the owner. A duplicate mesh
	# depth tint also revealed the robe's internally occluded surfaces, so it
	# is deliberately unused. Preserve enemy RGB hit/freeze modulation.
	for actor in actors.values():
		if not actor.has_meta("sprite"):continue
		var sprite: AnimatedSprite3D=actor.get_meta("sprite")
		var target := .32 if overlapping and _overlaps_hero(actor,camera) else 1.0
		var alpha := lerpf(float(actor.get_meta("owner_fade",1.0)),target,1.0-exp(-_render_delta*18.0))
		if alpha>.995:alpha=1.0
		actor.set_meta("owner_fade",alpha);sprite.modulate.a=alpha

func reset() -> void:
	super.reset();_phase=0;_idle_age=0;_death_age=0;_was_dead=false;_bounds_frame=-1;_grip_ready=false
