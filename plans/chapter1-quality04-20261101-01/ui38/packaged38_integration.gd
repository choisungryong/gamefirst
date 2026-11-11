extends SceneTree
## Actual38 release PCK; reads fork38 profile, never requests any profile mutation.
const HUD38=preload("res://chapter1/view/ui38/chapter_hud_quality38.gd")
var view: Node3D
var output := ""
var result: Dictionary={"success":false,"checks":[],"scope":"Actual38 release PCK native Forward+ input/profile-read integration; no full win/performance claim"}
var original_profile := ""
var choice_count := 0
func _initialize() -> void:call_deferred("_probe")
func _probe() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--ui38-output="):output=arg.trim_prefix("--ui38-output=")
	if output.is_empty():quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1600,900);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	original_profile=FileAccess.get_file_as_string("user://chapter-one-profile-v1.json")
	_check("separate38 userdata",OS.get_user_data_dir().ends_with("AshenCloisterChapterOneQuality38"))
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view.set_process(false);view.set_physics_process(false);view.audio.set_muted(true)
	_check("actual HUD38 script",view.hud.get_script()==HUD38)
	_check("fork profile loaded and valid",view.profile.available and not original_profile.is_empty())
	result.profile_summary={"revision":view.profile.state.revision,"items":view.profile.state.items.size(),"equipped":view.profile.state.equipped,"completed_runs":view.profile.state.completed_runs}
	await _sync();await _capture("menu")
	_check("menu initial keyboard focus",root.gui_get_focus_owner() is Button)
	view.hud.stash_show.emit();await _sync();await _capture("stash")
	_check("read-only stash opened",view.hud.stash_open and view.hud.overlay.visible)
	var controls: Array[Control]=[];view.hud._collect_focus38(view.hud.modal,controls)
	controls[-1].grab_focus();await _key(KEY_ENTER);await _sync()
	_check("stash closes by keyboard",not view.hud.stash_open and view.run.mode=="menu")
	await _key(KEY_ENTER);await _sync()
	_check("keyboard starts actual core",view.run.mode=="playing" and not view.run.hero.is_empty())
	_check("starting gear continuity",view.run.equipped.size()==view.profile.state.equipped.size())
	await _capture("combat")
	await _key(KEY_I);await _sync();await _capture("inventory")
	_check("I opens equipment",view.run.mode=="inventory" and is_instance_valid(view.hud._gear_scroll))
	await _key(KEY_ESCAPE);await _sync()
	_check("Esc closes equipment",view.run.mode=="playing")
	await _key(KEY_ESCAPE);await _sync();_check("Esc pauses",view.run.mode=="paused")
	await _key(KEY_ESCAPE);await _sync();_check("Esc resumes",view.run.mode=="playing")
	view.run.growth.award_xp(12);view.run._refresh_mode();view.hud.invalidate();await _sync()
	await _capture("growth")
	_check("growth keyboard focus",view.hud.modal.is_ancestor_of(root.gui_get_focus_owner()))
	var original_offer: Dictionary=view.run.get_offer()
	var prior_focus := root.gui_get_focus_owner();await _key(KEY_TAB)
	_check("Tab stays within growth modal",root.gui_get_focus_owner()!=prior_focus and view.hud.modal.is_ancestor_of(root.gui_get_focus_owner()))
	view.hud.choice.connect(func(_token: String,_card: String):choice_count+=1)
	await _key(KEY_ENTER);await _sync()
	_check("one authoritative growth selection",view.run.mode=="playing" and choice_count==1)
	_check("old offer rejected",not view.run.choose(original_offer.token,original_offer.cards[0].id))
	_check("profile bytes unchanged",FileAccess.get_file_as_string("user://chapter-one-profile-v1.json")==original_profile)
	var failed := false
	for check in result.checks:
		if not check.passed:failed=true
	result.success=not failed
	var file := FileAccess.open(output.path_join("PACKAGED-INTEGRATION.json"),FileAccess.WRITE);file.store_string(JSON.stringify(result,"  "));file.close()
	view.audio.reset();print("PACKAGED38_INTEGRATION ",JSON.stringify(result));quit(1 if failed else 0)
func _sync() -> void:
	for i in 6:
		if not view.run.hero.is_empty():
			view.world.update_camera(view.run.hero.position,.016);view.actors.sync(view.run,.016);view.effects.sync(view.run,.016)
		view.hud.sync(view.run,.016);await process_frame
func _key(code: Key) -> void:
	var event := InputEventKey.new();event.keycode=code;event.pressed=true;Input.parse_input_event(event);await process_frame
	event=InputEventKey.new();event.keycode=code;event.pressed=false;Input.parse_input_event(event);await _sync()
func _capture(label: String) -> void:
	await RenderingServer.frame_post_draw
	_check("capture "+label,root.get_texture().get_image().save_png(output.path_join(label+"-1280x720.png"))==OK)
func _check(label: String,passed: bool) -> void:
	result.checks.append({"name":label,"passed":passed});print("PACKAGED38 ",label," = ",passed)
