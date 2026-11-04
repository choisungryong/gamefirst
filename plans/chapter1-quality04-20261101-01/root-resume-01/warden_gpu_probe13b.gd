extends "res://chapter1/chapter_one_view.gd"
## Synthetic placement and stopped-core death presentation, not normal victory.
var checks := 0
var failed := false
func _physics_process(_delta: float) -> void:pass
func _process(_delta: float) -> void:pass
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:failed=true;push_error("WARDEN_VISIBILITY_FAILED "+message)
func _ready() -> void:
	super._ready()
	run.enemies.clear();run.projectiles.clear();run.orbs.clear();run.items.clear();actors.reset();effects.reset()
	run.zone=2;run.hero.position=Vector2(96,0);world.update_camera(run.hero.position,10)
	run._spawn("elite",Vector2(96,1));var e: Dictionary=run.enemies[run._enemy_sequence]
	e.chapter_boss=true;e.state="recover";e.hp_raw=4500*256;e.max_hp_raw=e.hp_raw
	var near := Vector2(world.camera.global_basis.z.x,world.camera.global_basis.z.z).normalized()
	var right := Vector2(world.camera.global_basis.x.x,world.camera.global_basis.x.z).normalized()
	var cases := [{"name":"behind","point":-near*.8,"expected":false},{"name":"front_close","point":near*.8,"expected":true},{"name":"front_clear5m","point":near*5.0,"expected":false},{"name":"lateral","point":near*.8+right*2.8,"expected":false}]
	var samples: Array=[]
	var actor: Node3D
	for sample in cases:
		run.tick+=1;e.position=run.hero.position+sample.point;actors.consume(run.events);actors.sync(run,1.0)
		actor=actors.actors.values()[0]
		var overlaps: bool=actors._overlaps_hero(actor,world.camera)
		var alpha: float=actor.get_meta("enemy_rig").owner_fade
		check(overlaps==sample.expected,sample.name+" current-pose coverage")
		check(absf(alpha-(.56 if sample.expected else 1.0))<.001,sample.name+" settled alpha")
		samples.append({"name":sample.name,"overlaps":overlaps,"alpha":alpha})
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("res://plans/chapter1-quality04-20261101-01/boss-research12/gpu09/captures/"+sample.name+".png")
	var rig: Skeleton3D=actor.get_meta("enemy_rig").skeleton
	var head := rig.find_bone("Head")
	var before: Vector3=(rig.global_transform*rig.get_bone_global_pose(head)).origin
	run.mode="victory";e.hp_raw=0;e.dead_tick=run.tick
	var stopped_tick: int=run.tick
	for i in 80:
		actors.sync(run,1.0/60.0)
		if i in [0,20,40,79]:
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png("res://plans/chapter1-quality04-20261101-01/boss-research12/gpu09/captures/death-%02d.png"%i)
	var after: Vector3=(rig.global_transform*rig.get_bone_global_pose(head)).origin
	var pose: Dictionary=actor.get_meta("warden_pose")
	check(run.tick==stopped_tick,"terminal core clock stayed stopped")
	check(pose.clip=="death" and float(pose.time)>=1.1,"death presentation progresses despite stopped core")
	check(before.y-after.y>.5,"actual head collapses rather than standing under victory UI")
	var result := {"checks":checks,"failed":failed,"coverage":samples,"death":{"core_tick":run.tick,"clip":pose,"head_y_before":before.y,"head_y_after":after.y},"scope":"Presenter placement and synthetic terminal-state probe; no normal victory/performance/art approval."}
	print("WARDEN_VISIBILITY_PROBE ",JSON.stringify(result))
	var file := FileAccess.open("res://plans/chapter1-quality04-20261101-01/boss-research12/gpu09/result.json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close()
	for voice in audio.voices:voice.stop();voice.stream=null
	audio.voices.clear();audio.streams.clear();audio.ambience=null
	await get_tree().create_timer(.2).timeout
	get_tree().quit(1 if failed else 0)
