extends SceneTree
var folder := ""
var variant := "26"
var view: Node3D
var begin := -1
var previous := -1
var measuring := false
var ending := false
var intervals: Array[int]=[]
var draws: Array[int]=[]
var start_tick := -1
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--flame33-dir="):folder=arg.trim_prefix("--flame33-dir=")
		if arg.begins_with("--flame33-actor="):variant=arg.trim_prefix("--flame33-actor=")
	if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
	DirAccess.make_dir_recursive_absolute(folder)
	view=load("res://chapter1/ChapterOne.tscn").instantiate();view.effects=load("res://chapter1/view/chapter_elements_quality%s.gd"%variant).new();root.add_child(view)
	while view.run.tick<16000:view.run.step(view.full_pilot.decide())
	view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear();view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(folder.path_join("before.png"));begin=Time.get_ticks_usec()
func _process(_delta: float) -> bool:
	if begin<0 or ending:return false
	var now := Time.get_ticks_usec()
	if not measuring:
		if now-begin>=2000000:measuring=true;previous=now;begin=now;start_tick=view.run.tick
		return false
	intervals.append(now-previous);previous=now;draws.append(int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)))
	if now-begin>=10000000:
		ending=true;view.set_process(false);view.set_physics_process(false);call_deferred("_finish")
	return false
func _finish() -> void:
	var reference=load("res://chapter1/core/chapter_run_quality16.gd").new();var policy=load("res://chapter1/core/chapter_pilot.gd").new();policy.run=reference
	var started: bool=reference.start(view.seed_,view.primary)
	while reference.tick<view.run.tick:reference.step(policy.decide())
	var same: bool=started and reference.snapshot()==view.run.snapshot()
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image();img.save_png(folder.path_join("after.png"))
	var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"actor":variant,"start_tick":start_tick,"end_tick":view.run.tick,"intervals_us":intervals,"draws":draws,"same_complete_core":same,"image":[img.get_width(),img.get_height()],"scope":"Source32 Actor32b FX26/33 fire billboard visibility comparison, earned16000checkpoint,2s warmup+10s OS-clock callback intervals,uncapped/vsync off/no capture in sample. Ignore-focus normalpolicy, not focused actual package final formal performance."},"\t"));f.close()
	view.audio.reset()
	for i in 4:await process_frame
	quit(0 if same else 1)
