extends SceneTree
## Core-only terminal lifetime diagnostic. Does not instantiate a game view/profile.
var mode := ""
var folder := ""
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--exit-mode="):mode=arg.trim_prefix("--exit-mode=")
		if arg.begins_with("--exit-dir="):folder=arg.trim_prefix("--exit-dir=")
	if mode not in ["model_live","model_cleanup"] or folder.is_empty():quit(2);return
	var reference=load("res://chapter1/core/chapter_run_quality36.gd").new()
	var pilot=load("res://chapter1/core/chapter_pilot.gd").new();pilot.run=reference
	var started: bool=reference.start(90131,"chapter1.skill.frost")
	var gear: Array[Dictionary]=[]
	var imported: bool=reference.import_starting_gear(gear)
	while reference.tick<21498 and reference.mode not in ["victory","defeat"]:reference.step(pilot.decide())
	var report={"mode":mode,"started":started,"imported":imported,"tick":reference.tick,"terminal_mode":reference.mode,"scope":"Core-only terminal lifetime; no view, profile, rewards saved, or native/GPU test"}
	var file=FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	if mode=="model_cleanup":file=null;pilot.run=null;pilot=null;reference=null
	for index in 4:await process_frame
	quit(0 if started and imported else 2)
