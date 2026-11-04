extends "res://chapter1/chapter_one_view.gd"
## Explicit pose/event placement fixture. Does not simulate a real boss victory.
var shots := {}
var _phase_previous := -1
var _phase_tick := 0
var _sent_paid := false
var _boss_id := -1
var _freeze_poses: Array[Transform3D]=[]
var _freeze_checked := false
const NAMES := ["idle","walk","circle","fan","hit","death","foreground","closeup","frozen","resume"]
func _ready() -> void:
	super._ready()
	run.enemies.clear();run.projectiles.clear();run.orbs.clear();run.items.clear();effects.reset();actors.reset()
	run.zone=2;run.hero.position=Vector2(96,0);run.hero.direction=Vector2.DOWN
	run._spawn("elite",Vector2(94.4,-1.3));_boss_id=run._enemy_sequence
	var e: Dictionary=run.enemies[_boss_id];e.chapter_boss=true;e.title="회랑의 파수왕 · 외형 검사"
	e.definition.windup=54;e.definition.recover=90;e.hp_raw=4500*256;e.max_hp_raw=e.hp_raw
	run.events.clear();world.update_camera(run.hero.position,0)
	print("WARDEN_FIXTURE_SCOPE Explicit pose placement, not normal gameplay, clear, or performance")
func _physics_process(_delta: float) -> void:
	run.tick+=1
	var phase := mini(9,int(_wall_age/1.5))
	if phase!=_phase_previous:_phase_tick=run.tick;_phase_previous=phase;_sent_paid=false
	var local_tick: int=run.tick-_phase_tick
	var e: Dictionary=run.enemies[_boss_id]
	e.position=Vector2(94.4,-1.3);e.direction=Vector2.DOWN;e.attack_direction=Vector2.DOWN;e.state="recover";e.hp_raw=4500*256;e.frozen_until=0
	if phase==1:e.position.x+=float(local_tick)/60*.9;e.state="move";e.direction=Vector2.RIGHT
	elif phase in [2,3]:
		e.attack_kind="circle" if phase==2 else "fan";e.state_until=_phase_tick+54
		if local_tick<54:e.state="windup"
		else:
			e.state="recover";e.state_until=_phase_tick+54+90
			if not _sent_paid:
				_sent_paid=true;run._emit("enemy_attack",e.position,{"target_id":e.id,"kind":"elite","direction":e.attack_direction,"attack_kind":e.attack_kind})
	elif phase==4 and local_tick in [15,35,55]:run._emit("hit",e.position,{"target_id":e.id,"skill_id":"chapter1.skill.ember"})
	elif phase==5:e.hp_raw=0;e.dead_tick=_phase_tick
	elif phase==6:
		var camera: Camera3D=world.camera;var near := Vector2(camera.global_basis.z.x,camera.global_basis.z.z).normalized()
		e.position=run.hero.position+near*.8
	elif phase==7:world.camera.size=12
	elif phase==8:e.frozen_until=run.tick+600
	actors.consume(run.events)
func _process(delta: float) -> void:
	super._process(delta)
	var phase := mini(9,int(_wall_age/1.5))
	if phase==8:
		for actor in actors.actors.values():
			if not actor.has_meta("enemy_rig"):continue
			var rig: Skeleton3D=actor.get_meta("enemy_rig").skeleton
			if _freeze_poses.is_empty():
				for i in rig.get_bone_count():_freeze_poses.append(rig.get_bone_pose(i))
			elif not _freeze_checked and fmod(_wall_age,1.5)>1.0:
				_freeze_checked=true;var equal_ := true
				for i in rig.get_bone_count():equal_=equal_ and _freeze_poses[i].is_equal_approx(rig.get_bone_pose(i))
				print("WARDEN_FREEZE_CHECK ",JSON.stringify({"same_bones":equal_,"count":_freeze_poses.size(),"tick_advanced_while_frozen":true,"scope":"Presenter freeze fixture, not core freeze duration validation"}))
				if not equal_:push_error("Frozen warden pose advanced");get_tree().quit(1)
	for part in 3:
		var key: String=NAMES[phase]+"-%d"%part
		if fmod(_wall_age,1.5)>=[.35,.8,1.15][part]and not shots.has(key):
			shots[key]=true
			await RenderingServer.frame_post_draw
			var path := "res://plans/chapter1-quality04-20261101-01/boss-research12/fixture01/captures/"+key+".png"
			DirAccess.make_dir_recursive_absolute(path.get_base_dir())
			if not FileAccess.file_exists(path):get_viewport().get_texture().get_image().save_png(path)
			for actor in actors.actors.values():
				if actor.has_meta("enemy_rig"):print("WARDEN_FIXTURE_POSE ",JSON.stringify({"phase":NAMES[phase],"pose":actor.get_meta("warden_pose"),"fade":actor.get_meta("enemy_rig").owner_fade,"scope":"Explicit pose placement; not normal victory"}))
