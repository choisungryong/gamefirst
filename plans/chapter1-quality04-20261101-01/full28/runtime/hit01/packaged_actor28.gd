extends SceneTree
var folder := ""
var view: Node3D
var ready_ := false
var ending := false
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--actor28-dir="):folder=arg.trim_prefix("--actor28-dir=")
	if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
	DirAccess.make_dir_recursive_absolute(folder)
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	while view.run.tick<2800:view.run.step(view.full_pilot.decide())
	view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
	view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(folder.path_join("before.png"));ready_=true
func _process(_delta: float) -> bool:
	if ready_ and not ending and view.run.tick>=3400:
		ending=true;view.set_process(false);view.set_physics_process(false);call_deferred("_finish")
	return false
func _finish() -> void:
	var reference=load("res://chapter1/core/chapter_run_quality16.gd").new();var policy=load("res://chapter1/core/chapter_pilot.gd").new();policy.run=reference
	var started: bool=reference.start(view.seed_,view.primary)
	while reference.tick<view.run.tick:reference.step(policy.decide())
	var same: bool=started and reference.snapshot()==view.run.snapshot()
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image();img.save_png(folder.path_join("after.png"))
	var blends: int=view.actors.hit28_blends
	var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"same_complete_core":same,"tick":view.run.tick,"hit_blends":blends,"actor_script":view.actors.get_script().resource_path,"hud_script":view.hud.get_script().resource_path,"fx_script":view.effects.get_script().resource_path,"image":[img.get_width(),img.get_height()],"pool_created":view.actors.pool25_created,"pool_hits":view.actors.pool25_hits,"profile_off":view._profile_off,"scope":"Actual28 EXE/PCK normal earned2800tick checkpoint then original live policy/controllers until3400tick, independent full core equality. Actual GPU before/after screenshots. Not manual/full chapter/hearing/formal performance."},"\t"));f.close()
	view.audio.reset()
	for i in 4:await process_frame
	quit(0 if same and blends>0 else 1)
