extends SceneTree
var view: Node3D
var folder := ""
var ending := false
var started_us := 0
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--profile35-dir="):folder=arg.trim_prefix("--profile35-dir=")
	if folder.is_empty() or DirAccess.dir_exists_absolute(folder) or FileAccess.file_exists("user://chapter-one-profile-v1.json"):push_error("Fresh evidence and initially absent default35 profile required");quit(1);return
	DirAccess.make_dir_recursive_absolute(folder)
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view);started_us=Time.get_ticks_usec()
	if view._profile_off or not view.profile.available:push_error("Actual default profile unavailable");quit(1)
func _process(_delta: float) -> bool:
	if view==null or ending:return false
	if view.run.mode=="victory":
		ending=true;view.set_process(false);view.set_physics_process(false);call_deferred("_finish")
	elif view.run.mode=="defeat" or view.run.tick>27000 or (started_us>0 and Time.get_ticks_usec()-started_us>240000000):ending=true;push_error("Default profile earned run did not finish");quit(1)
	return false
func _finish() -> void:
	var reload_profile=load("res://chapter1/core/chapter_profile.gd").new()
	var reloaded: bool=reload_profile.configure()
	var same_profile: bool=reloaded and reload_profile.state==view.profile.state
	var reference=load("res://chapter1/core/chapter_run_quality16.gd").new();var pilot=load("res://chapter1/core/chapter_pilot.gd").new();pilot.run=reference
	var started: bool=reference.start(view.seed_,view.primary)
	var empty_starting_gear: Array[Dictionary]=[]
	var imported: bool=reference.import_starting_gear(empty_starting_gear)
	while reference.tick<view.run.tick:reference.step(pilot.decide())
	var same_core: bool=started and imported and reference.snapshot()==view.run.snapshot()
	var saved: bool=FileAccess.file_exists(view.profile.path) and int(view.profile.state.completed_runs)==1 and view.profile.error.is_empty()
	var file := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"tick":view.run.tick,"kills":view.run.kills,"same_complete_core":same_core,"saved":saved,"same_profile_after_reload":same_profile,"profile_path":view.profile.path,"absolute_profile_path":ProjectSettings.globalize_path(view.profile.path),"profile_state":view.profile.state,"profile_off":view._profile_off,"scope":"Actual35 EXE, initially absent default user profile, original fixed60 headless normal policy from menu/start to earned first victory. Original event/save pipeline, then real default configure reload. No grant/teleport/alternate profile destination. Newly earned user profile must be preserved. Not GPU/native/manual/hearing approval."},"\t"));file.close()
	view.audio.reset()
	for i in 4:await process_frame
	quit(0 if saved and same_profile and same_core else 1)
