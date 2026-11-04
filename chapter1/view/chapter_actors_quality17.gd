extends "res://chapter1/view/chapter_actors_quality16.gd"
## Reuse authored frames with distinct distance phases and actual windup timing.
## Sprite lean is bounded; root positions, hurtboxes, and the Warden rig stay intact.
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	if actor==hero or actor.has_meta("enemy_rig") or not actor.has_meta("sprite"):
		super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast);return
	var entity := _entity(actor)
	var sample: Dictionary=actor.get_meta("motion_sample",{})
	var original_phase := float(sample.get("phase",0.0))
	if not entity.is_empty():
		sample.phase=fposmod(original_phase+float((int(entity.id)*37)%101)/101.0,1.0);actor.set_meta("motion_sample",sample)
	super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast)
	if not sample.is_empty():sample.phase=original_phase;actor.set_meta("motion_sample",sample)
	var sprite: AnimatedSprite3D=actor.get_meta("sprite")
	if dead:sprite.rotation.z=0;return
	if not playing or entity.is_empty():return
	var camera := view.get_viewport().get_camera_3d()
	var side := direction.dot(Vector2(camera.global_basis.x.x,camera.global_basis.x.z).normalized())
	var lean := 0.0
	if entity.state=="windup":
		var length_: int=entity.get("definition",{}).get("windup",36)
		var progress := 1.0-clampf(float(int(entity.state_until)-tick)/maxf(1,length_),0,1)
		lean=-side*.085*sin(progress*PI*.5)
	elif entity.state=="dash":lean=side*.10
	elif moving:lean=side*.025*sin(original_phase*TAU)
	sprite.rotation.z=lerpf(sprite.rotation.z,lean,1.0-exp(-_render_delta*22))
