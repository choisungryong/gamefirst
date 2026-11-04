extends "res://chapter1/chapter_one_view.gd"
## Isolated presenter/core integration, not a normal run or victory.
var _id := -1
var checks := 0
var _failed := false
func _physics_process(_delta: float) -> void:pass
func _process(_delta: float) -> void:pass
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:_failed=true;push_error("WARDEN_CLOCK_FAILED "+message)
func _ready() -> void:
	super._ready()
	run.enemies.clear();run.projectiles.clear();run.orbs.clear();run.items.clear();actors.reset();effects.reset()
	run.zone=2;run.hero.position=Vector2(96,0);run.hero.direction=Vector2.DOWN
	run._next_spawn=999999;run._next_ward=999999
	run._spawn("elite",Vector2(96,1.7));_id=run._enemy_sequence
	var e: Dictionary=run.enemies[_id];e.chapter_boss=true;e.definition.windup=54;e.definition.recover=90;e.hp_raw=4500*256;e.max_hp_raw=e.hp_raw
	run._champion_id=_id;run._boss_phase=1
	var waited := 0
	while e.state!="recover" and waited<200 and run.mode=="playing":step_once();waited+=1
	check(e.state=="recover","actual core reaches paid recover")
	check(actors._paid_attacks.has(_id),"actual enemy_attack is consumed")
	for i in 8:step_once()
	var actor: Node3D=actors.actors.values()[0]
	var before: Dictionary=actor.get_meta("warden_pose").duplicate(true)
	var end_before: int=e.state_until
	check(before.clip=="slam","circle dispatches slam")
	var rig: Skeleton3D=actor.get_meta("enemy_rig").skeleton
	var poses: Array[Transform3D]=[]
	for i in rig.get_bone_count():poses.append(rig.get_bone_pose(i))
	var freeze_start: int=run.tick;e.frozen_until=run.tick+30
	for i in 29:step_once()
	var frozen: Dictionary=actor.get_meta("warden_pose").duplicate(true)
	var all_equal := true
	for i in rig.get_bone_count():all_equal=all_equal and poses[i].is_equal_approx(rig.get_bone_pose(i))
	check(all_equal,"all73 bone poses held while core freezes recovery")
	check(int(e.state_until)==end_before+29,"actual core extends recover29 ticks")
	check(is_equal_approx(float(before.time),float(frozen.time)),"held animation time unchanged")
	step_once()
	var thawed: Dictionary=actor.get_meta("warden_pose").duplicate(true)
	var delta_time: float=float(thawed.time)-float(before.time)
	check(delta_time>=.005 and delta_time<=.035,"thaw advances one step rather than skipping half a second")
	check(thawed.clip=="slam","thaw stays in paid recovery clip")
	var result := {"checks":checks,"failed":_failed,"before":before,"frozen":frozen,"thawed":thawed,"thaw_animation_delta_seconds":delta_time,"freeze_ticks":run.tick-freeze_start,"scope":"Actual ChapterRun.step and presenter, isolated boss/spawn/ward suppression; manual frozen_until assignment. No normal gameplay or quality approval."}
	print("WARDEN_CLOCK_PROBE ",JSON.stringify(result))
	var file := FileAccess.open("res://plans/chapter1-quality04-20261101-01/boss-research12/clock04/result.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"\t"));file.close()
	for voice in audio.voices:voice.stop();voice.stream=null
	audio.voices.clear();audio.streams.clear();audio.ambience=null
	await get_tree().create_timer(.2).timeout
	get_tree().quit(1 if _failed else 0)
func step_once() -> void:
	run.step(Vector2.ZERO);actors.consume(run.events);actors.sync(run,1.0/60.0)
