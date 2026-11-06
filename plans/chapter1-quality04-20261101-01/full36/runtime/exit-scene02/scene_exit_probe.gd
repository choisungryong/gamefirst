extends SceneTree
## One bounded actual36 profile-OFF full-scene lifecycle, not first-save acquisition.
var view: Node3D
var folder := ""
var started_us := 0
var ending := false
var initial_inventory_count := -1
var initial_equipped: Dictionary={}
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--scene-exit-dir="):folder=arg.trim_prefix("--scene-exit-dir=")
	if folder.is_empty() or FileAccess.file_exists(folder.path_join("RESULT.json")):push_error("Fresh diagnostic output required");quit(2);return
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	started_us=Time.get_ticks_usec()
	initial_inventory_count=view.run.inventory.size();initial_equipped=view.run.equipped.duplicate(true)
	if not view._profile_off or view.profile.available or initial_inventory_count!=0 or not initial_equipped.is_empty():
		push_error("Profile OFF and empty starting gear required");quit(2);return
func _process(_delta: float) -> bool:
	if view==null or ending:return false
	if view.run.mode in ["victory","defeat"]:
		ending=true;view.set_process(false);view.set_physics_process(false);call_deferred("_finish")
	elif view.run.tick>27000 or (started_us>0 and Time.get_ticks_usec()-started_us>160000000):
		ending=true;view.set_process(false);view.set_physics_process(false);call_deferred("_finish")
	return false
func _finish() -> void:
	var report := {"terminal_mode":view.run.mode,"tick":view.run.tick,"kills":view.run.kills,"profile_off":view._profile_off,"profile_available":view.profile.available,"initial_inventory_count":initial_inventory_count,"initial_equipped":initial_equipped,"core_errors":view.run.errors.duplicate(),"core_script":view.run.get_script().resource_path,"scope":"Actual36 profile-OFF scene, normal fixed60 cold90131 pilot; no saved user profile read or written, no reference clone, no GPU/manual/audio/performance approval"}
	var passed: bool=report.terminal_mode=="victory" and report.tick==21498 and report.profile_off and not report.profile_available and initial_inventory_count==0 and initial_equipped.is_empty() and report.core_errors.is_empty()
	report["terminal_predicate_pass"]=passed
	var file := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t"));file.close();file=null
	view.audio.reset();view.queue_free()
	for index in 4:await process_frame
	view=null
	quit(0 if passed else 2)
