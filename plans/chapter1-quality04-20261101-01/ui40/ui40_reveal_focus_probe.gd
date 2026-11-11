extends SceneTree
## Narrow initial-victory reveal/focus check; no save or real victory claim.
var view: Node3D
var checks: Array[Dictionary]=[]
var output := ""
func _initialize() -> void:call_deferred("_probe")
func _probe() -> void:
	if not "--chapter1-profile-off" in OS.get_cmdline_user_args():quit(2);return
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--ui40-output="):output=arg.trim_prefix("--ui40-output=")
	if output.is_empty():quit(2);return
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1600,900)
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view.set_process(false);view.set_physics_process(false);view.audio.set_muted(true)
	view.start_run("chapter1.skill.frost");view.audio.set_muted(true)
	view.hud.sync(view.run,.016);await process_frame
	view.run.mode="victory";view.hud.invalidate()
	view.hud.sync(view.run,.016);await process_frame
	_check("initial victory remains hidden",not view.hud.overlay.visible)
	_check("initial terminal modal has one content box",view.hud.modal.get_child_count()==1)
	for i in 14:
		view.hud.sync(view.run,.1);await process_frame
	_check("victory becomes visible after inherited delay",view.hud.overlay.visible)
	var focused := root.gui_get_focus_owner()
	_check("reveal assigns terminal focus",focused!=null and view.hud.modal.is_ancestor_of(focused))
	var press := InputEventKey.new();press.keycode=KEY_TAB;press.pressed=true
	Input.parse_input_event(press);await process_frame
	var release := InputEventKey.new();release.keycode=KEY_TAB;release.pressed=false
	Input.parse_input_event(release);await process_frame
	var after_tab := root.gui_get_focus_owner()
	_check("Tab moves within revealed terminal",after_tab!=null and after_tab!=focused and view.hud.modal.is_ancestor_of(after_tab))
	await RenderingServer.frame_post_draw
	_check("capture",root.get_texture().get_image().save_png(output.path_join("victory-revealed-1280x720.png"))==OK)
	var success := true
	for check in checks:
		if not check.passed:success=false
	var report := {"success":success,"checks":checks,"scope":"Synthetic initial victory reveal and keyboard focus only; no profile access/manual victory/performance claim"}
	var file := FileAccess.open(output.path_join("RESULT.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  "));file.close()
	print("UI40_REVEAL_RESULT ",JSON.stringify(report));view.audio.reset();quit(0 if success else 1)
func _check(name_: String,passed: bool) -> void:
	checks.append({"name":name_,"passed":passed});print("UI40_REVEAL ",name_," = ",passed)
