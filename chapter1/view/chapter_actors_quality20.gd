extends "res://chapter1/view/chapter_actors_batched19.gd"
var _victory20_age := 0.0
var _victory20_active := false
## Make the paid final-boss death settle onto the ground before reward UI.
## Local visual transform only; entity position/hurtbox/reward remain untouched.
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	var saved_delta := _render_delta
	if dead and actor.has_meta("enemy_rig") and view.run.mode=="inventory":_render_delta=0
	super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast)
	_render_delta=saved_delta
	if not actor.has_meta("enemy_rig"):return
	var model: Node3D=actor.get_meta("enemy_rig").model
	if not dead:
		model.rotation.z=0;model.position.y=0;return
	var age: float=actor.get_meta("warden_death_age",0.0)
	var collapse := smoothstep(.18,1.08,age)
	model.rotation.z=collapse*1.47
	model.position.y=lerpf(0,-.10,collapse)
	actor.set_meta("warden20_collapse",collapse)
func sync(run: RefCounted,delta: float) -> void:
	if run.mode=="victory":_victory20_active=true
	if _victory20_active and run.mode=="victory":_victory20_age+=maxf(0,delta)
	super.sync(run,delta)
	if not _victory20_active:return
	var alpha := 1-smoothstep(.12,.62,_victory20_age)
	for actor in actors.values():
		var e := _entity(actor)
		if e.is_empty() or actor.has_meta("enemy_rig"):continue
		if actor.has_meta("minion19"):
			for mat in actor.get_meta("minion19").materials:mat.albedo_color.a*=alpha
		elif actor.has_meta("sprite"):actor.get_meta("sprite").modulate.a*=alpha
func reset() -> void:
	super.reset();_victory20_age=0;_victory20_active=false
