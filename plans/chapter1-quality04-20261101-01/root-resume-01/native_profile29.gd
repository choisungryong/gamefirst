extends SceneTree
var view: Node
var folder := ""
var phase := ""
var previous := ""
var ending := false
var count := 0
class InputLog extends Node:
	func _input(event: InputEvent) -> void:
		if event is InputEventMouseButton and event.pressed:print("NATIVE29_INPUT ",JSON.stringify({"mouse":event.button_index,"position":event.position}))
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--native29-dir="):folder=arg.trim_prefix("--native29-dir=")
		if arg.begins_with("--native29-phase="):phase=arg.trim_prefix("--native29-phase=")
	if folder.is_empty() or DirAccess.dir_exists_absolute(folder) or phase not in ["equip","reload"]:push_error("Fresh evidence directory required");quit(1);return
	DirAccess.make_dir_recursive_absolute(folder)
	if ProjectSettings.get_setting("application/config/custom_user_dir_name","")!="AshenCloisterChapterOneQuality29":push_error("Wrong namespace");quit(1);return
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view);root.add_child(InputLog.new())
	if not view.profile.available or view._profile_off:push_error("Default profile required");quit(1);return
	_record("initial")
func _record(label: String) -> void:
	var file := FileAccess.open(folder.path_join(label+".json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"phase":phase,"mode":view.run.mode,"tick":view.run.tick,"profile":view.profile.state,"hero":view.run.hero,"equipped":view.run.equipped,"inventory":view.run.inventory,"profile_path":ProjectSettings.globalize_path(view.profile.path),"scope":"Actual29 default profile/native UI observer. No direct equip/start/gear edits. Reload start freezes immediately for stat inspection; not manual whole run."},"\t"));file.close()
func _process(_delta: float) -> bool:
	if view==null or ending:return false
	var signature := str([view.run.mode,view.hud.stash_open,view.profile.state.revision,view.profile.state.equipped])
	if signature!=previous:
		previous=signature;count+=1;_record("state-%02d"%count);call_deferred("_capture","state-%02d"%count)
	if (phase=="equip" and int(view.profile.state.revision)>1) or (phase=="reload" and view.run.mode!="menu"):
		ending=true;view.set_process(false);view.set_physics_process(false);_record("RESULT");call_deferred("_finish")
	return false
func _capture(label: String) -> void:
	await process_frame
	var image := root.get_texture().get_image()
	if image:image.save_png(folder.path_join(label+".png"))
func _finish() -> void:
	await _capture("final")
	await create_timer(3).timeout
	view.audio.reset()
	for i in 4:await process_frame
	quit(0)
