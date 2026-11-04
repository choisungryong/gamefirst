extends "res://chapter1/chapter_one_view.gd"
var checks: Dictionary={}
var details: Dictionary={}
func _ready() -> void:
	super._ready()
	set_process(false);set_physics_process(false)
	var original: Dictionary=run.snapshot().duplicate(true)
	var originals: Dictionary=run.enemies
	var source: Dictionary=originals.values()[0].duplicate(true)
	var e: Dictionary=source.duplicate(true)
	run.enemies={e.id:e}
	e.kind="walker";e.elite=false;e.position=run.hero.position+Vector2(0,-1.4);e.state="move";e.frozen_until=0
	actors.reset();actors.sync(run,.1)
	var key := "%d:%d"%[e.generation,e.id]
	var actor: Node3D=actors.actors[key]
	checks.rig_created=actor.has_meta("minion19")
	var state: Dictionary=actor.get_meta("minion19")
	for direction in [Vector2.UP,Vector2.RIGHT,Vector2.DOWN,Vector2.LEFT]:
		e.direction=direction;actors.sync(run,1.0)
		checks["facing_"+str(direction)]=absf(angle_difference(actor.rotation.y,atan2(direction.x,direction.y)))<.001
	var definition: Dictionary=run._enemy_definition(e)
	e.state="windup";e.attack_kind="circle";e.attack_direction=Vector2.RIGHT;e.state_until=run.tick+int(definition.windup)
	actors.sync(run,.016)
	checks.walker_windup=actor.get_meta("minion19_pose").clip=="windup_slam"
	e.state_until=run.tick+6;actors.sync(run,.016)
	checks.walker_last6=actor.get_meta("minion19_pose").clip=="slam" and actor.get_meta("minion19_pose").time<=.03
	e.state="recover";e.state_until=run.tick+int(definition.recover)
	actors.consume([{"seq":100000,"type":"enemy_attack","target_id":e.id,"position":e.position,"tick":run.tick,"attack_kind":"circle","kind":"walker"}]);actors.sync(run,.016)
	checks.walker_paid_release=actor.get_meta("minion19_pose").clip=="slam" and absf(float(actor.get_meta("minion19_pose").time)-.157)<.03
	await _fixture_shot("walker-paid-release")
	var pose: Dictionary=actor.get_meta("minion19_pose").duplicate(true)
	e.frozen_until=run.tick+60;actors.sync(run,.2)
	checks.frozen_pose_held=pose==actor.get_meta("minion19_pose")
	e.frozen_until=0
	var overlap := false
	var camera := get_viewport().get_camera_3d()
	for x in [-.5,0,.5]:
		for z in [-2.0,-1.0,.5,1.0,2.0]:
			e.position=run.hero.position+Vector2(x,z);actors.sync(run,.1)
			if actors._overlaps_hero(actor,camera):overlap=true
	checks.owner_overlap_found=overlap
	e.position=run.hero.position+Vector2(10,10);actors.sync(run,1)
	checks.distant_owner_not_overlapped=not actors._overlaps_hero(actor,camera)
	var seq := 100001
	for fixture in [{"name":"frost_walker","elite":false,"kind":"walker","skill":"chapter1.skill.frost","hidden":true},{"name":"fire_walker","elite":false,"kind":"walker","skill":"chapter1.skill.ember","hidden":false},{"name":"frost_elite","elite":true,"kind":"elite","skill":"chapter1.skill.frost","hidden":false}]:
		actors.reset();e.kind=fixture.kind;e.elite=fixture.elite;e.hp_raw=0;e.dead_tick=run.tick;e.position=run.hero.position+Vector2(2,-2)
		actors.consume([{"seq":seq,"type":"death","target_id":e.id,"position":e.position,"tick":run.tick,"skill_id":fixture.skill,"kind":e.kind,"elite":e.elite}]);seq+=1
		actors.sync(run,.25);actor=actors.actors[key];state=actor.get_meta("minion19")
		var alpha: float=state.materials[0].albedo_color.a
		checks[fixture.name]=(alpha<.001) if fixture.hidden else (alpha>.9)
		details[fixture.name]={"alpha":alpha,"tracked":actors._cold_corpses.has(key)}
		await _fixture_shot(fixture.name)
	actors.reset()
	checks.reset_records=actors._cold_corpses.is_empty() and actors._demon19_attacks.is_empty() and actors._demon19_event==-1 and actors.motion19_samples==0
	run.enemies=originals;actors.sync(run,0)
	checks.full_core_restored=original==run.snapshot()
	var f := FileAccess.open("res://fixture-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"details":details,"scope":"Synthetic presentation fixtures on one copied entity, no normal-play/performance claim; original complete core restored."},"\t"));f.close()
	var failed := false
	for value in checks.values():if not value:failed=true
	audio.reset()
	for i in 4:await get_tree().process_frame
	get_tree().quit(1 if failed else 0)
func _fixture_shot(label: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://fixture-shots")
	get_viewport().get_texture().get_image().save_png("res://fixture-shots/"+label+".png")
