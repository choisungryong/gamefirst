extends "res://chapter1/view/chapter_actors_quality30c.gd"
## Opt-in source combat preview. Unbound roles and final boss keep current3D.
const Slot=preload("res://chapter1/presentation/sprite_asset_presenter_v2.gd")
var registry=preload("res://chapter1/presentation/sprite_role_registry.gd").new()
var _hero_slot: Node3D
var slot_samples := 0
var slot_fallbacks := 0
func setup(owner_view: Node3D) -> void:
	assert(registry.loaded,"Configure a role registry before setup")
	super.setup(owner_view)
	for actor in _pool25_root.get_children():_slot_for(actor)
	if registry.bindings.has("hero"):
		_hero_slot=_slot_for(hero);rig_model.visible=false;_staff.visible=false
func _create(kind: String) -> Node3D:
	var actor := super._create(kind)
	_slot_for(actor)
	return actor
func _slot_for(actor: Node3D) -> Node3D:
	var kind: String=actor.get_meta("kind","")
	if not registry.bindings.has(kind) or actor.has_meta("enemy_rig"):return null
	if kind=="hero":
		if _hero_slot!=null:return _hero_slot
	else:
		if not actor.has_meta("minion19"):return null
		var state: Dictionary=actor.get_meta("minion19")
		state.model.visible=false
		if state.has("staff21"):state.staff21.visible=false
		if state.has("sprite_slot"):return state.sprite_slot
	var slot := Slot.new();slot.name="RegisteredSpriteSlot";actor.add_child(slot)
	var ok: bool=slot.configure(registry.bindings[kind].asset)
	assert(ok,"Registered sprite could not load")
	if not ok:slot.queue_free();return null
	if kind=="hero":_hero_slot=slot
	else:actor.get_meta("minion19").sprite_slot=slot
	return slot
func _facing(direction: Vector2,actor: Node3D) -> String:
	if direction.length_squared()<.001:return actor.get_meta("slot_facing","south")
	var camera := view.get_viewport().get_camera_3d()
	if camera==null:return "south"
	var right := Vector2(camera.global_basis.x.x,camera.global_basis.x.z).normalized()
	var forward := Vector2(-camera.global_basis.z.x,-camera.global_basis.z.z).normalized()
	var screen := Vector2(direction.dot(right),-direction.dot(forward))
	var facing := ("east" if screen.x>0 else "west") if absf(screen.x)>absf(screen.y) else ("south" if screen.y>0 else "north")
	actor.set_meta("slot_facing",facing)
	return facing
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast)
	var slot := _slot_for(actor)
	if slot==null:return
	if not playing and not dead and not slot.last_sample.is_empty():return
	var kind: String=actor.get_meta("kind")
	var e: Dictionary={} if actor==hero else _entity(actor)
	if not e.is_empty() and e.state=="recover":direction=e.attack_direction
	var facing := _facing(direction,actor)
	var action := "idle";var phase := float(tick)/60.0
	if dead:
		action="death"
		var age: float=_death_age if actor==hero else actor.get_meta("minion19").death_age
		phase=age/slot.duration_for(action,facing)
	elif not e.is_empty() and e.state in ["windup","recover","dash"]:
		action="cast"
		var release: int=registry.bindings[kind].release_frame
		var pivot: float=slot.release_phase(facing,release) if release>=0 else 0.0
		if e.state=="windup":
			var definition: Dictionary=view.run._enemy_definition(e)
			var duration := maxi(1,int(definition.windup))
			var progress := clampf(1-float(int(e.state_until)-tick)/duration,0,1)
			phase=progress*maxf(0,pivot-.00001)
		else:
			var definition: Dictionary=view.run._enemy_definition(e)
			var duration := maxi(1,int(definition.get("recover",30)))
			var progress := clampf(1-float(int(e.state_until)-tick)/duration,0,1)
			phase=pivot+progress*(1-pivot)
	elif actor==hero and casting:
		action="cast";var release: int=registry.bindings.hero.release_frame
		var pivot: float=slot.release_phase(facing,release) if release>=0 else 0.0
		phase=pivot+clampf(float(tick-_cast_tick)/12.0,0,1)*(1-pivot)
	elif hit:
		action="hit"
		var until: int=_hit_until if actor==hero else int(_enemy_hit_until.get(e.id,tick))
		phase=clampf(1-float(until-tick)/(6.0 if actor==hero else 12.0),0,1)
	elif moving:
		action="move";phase=float(actor.get_meta("motion_sample",{}).get("phase",0.0))
	var ok: bool=slot.sample(action,facing,phase)
	assert(ok)
	slot_samples+=1
	if slot.last_sample.fallback:slot_fallbacks+=1
func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	if _hero_slot!=null:rig_model.visible=false;_staff.visible=false
	for actor in actors.values():
		if not actor.has_meta("minion19"):continue
		var state: Dictionary=actor.get_meta("minion19")
		if not state.has("sprite_slot"):continue
		var e := _entity(actor)
		if e.is_empty():continue
		var color := Color(.55,.88,1.05) if run.tick<int(e.frozen_until) else Color.WHITE
		color.a=state.materials[0].albedo_color.a
		state.sprite_slot.sprite.modulate=color
