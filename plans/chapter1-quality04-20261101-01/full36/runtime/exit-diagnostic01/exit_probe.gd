extends SceneTree
## Bounded observer-lifecycle diagnostic. No profile reads/writes or terminal rewards.
var view: Node3D
var mode := ""
var folder := ""
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--exit-mode="):mode=arg.trim_prefix("--exit-mode=")
		if arg.begins_with("--exit-dir="):folder=arg.trim_prefix("--exit-dir=")
	if mode not in ["observer_live","observer_cleanup","scene_only"] or folder.is_empty():quit(2);return
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view.set_process(false);view.set_physics_process(false)
	if not view._profile_off or view.profile.available:push_error("Profile must remain disabled");quit(2);return
	var reload_profile=load("res://chapter1/core/chapter_profile.gd").new()
	var reference=load("res://chapter1/core/chapter_run_quality36.gd").new()
	var pilot=load("res://chapter1/core/chapter_pilot.gd").new();pilot.run=reference
	if mode!="scene_only":
		reference.start(90131,"chapter1.skill.frost")
		for index in 120:reference.step(pilot.decide())
	var report={"mode":mode,"profile_off":view._profile_off,"profile_available":view.profile.available,"reference_tick":reference.tick,"scope":"120-tick no-reward lifecycle probe; not original first-acquisition rerun or full victory regression"}
	var file=FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t"));file.close()
	view.audio.reset()
	if mode!="observer_live":
		file=null;pilot.run=null;pilot=null;reference=null;reload_profile=null
		view.queue_free()
		for index in 4:await process_frame
		view=null
	else:
		for index in 4:await process_frame
	quit(0)
