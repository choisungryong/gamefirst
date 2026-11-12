extends SceneTree
## Actual42 release PCK. Only the new menu contract plus read-only profile and
## short inherited combat handoff are checked; no terminal save is requested.
const HUD41=preload("res://chapter1/view/ui41/chapter_hud_quality41.gd")
const ACTOR42=preload("res://chapter1/view/chapter_actors_quality42.gd")
const FX39=preload("res://chapter1/view/chapter_elements_quality39.gd")
var view: Node3D
var output := ""
var original_profile := ""
var result: Dictionary={"success":false,"checks":[],"scope":"Actual42 release PCK native Forward+ menu/profile-read/start handoff; no full win/performance claim"}
func _initialize() -> void:call_deferred("_probe")
func _probe() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--ui42-output="):output=arg.trim_prefix("--ui42-output=")
	if output.is_empty():quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	root.size=Vector2i(1280,720);root.content_scale_size=Vector2i(1600,900);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	original_profile=FileAccess.get_file_as_string("user://chapter-one-profile-v1.json")
	_check("separate42 userdata",OS.get_user_data_dir().ends_with("AshenCloisterChapterOneQuality42"))
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view.set_process(false);view.set_physics_process(false);view.audio.set_muted(true)
	_check("actual Actor42 script",view.actors.get_script()==ACTOR42)
	_check("actual HUD41 script",view.hud.get_script()==HUD41)
	_check("actual FX39 script",view.effects.get_script()==FX39)
	_check("fork profile loaded and valid",view.profile.available and not original_profile.is_empty())
	result.profile_summary={"revision":view.profile.state.revision,"items":view.profile.state.items.size(),"equipped":view.profile.state.equipped,"completed_runs":view.profile.state.completed_runs}
	await _sync();await _capture("menu")
	var portrait := view.hud.modal.find_child("PortraitTexture41",true,false) as TextureRect
	_check("packaged portrait texture loaded",is_instance_valid(portrait) and portrait.texture!=null and portrait.texture.resource_path=="res://chapter1/art/portrait41/oath_witch_portrait_v01.png")
	_check("menu initial keyboard focus",root.gui_get_focus_owner() is Button and view.hud.modal.is_ancestor_of(root.gui_get_focus_owner()))
	var prior_focus := root.gui_get_focus_owner();await _key(KEY_TAB)
	_check("Tab stays within menu",root.gui_get_focus_owner()!=prior_focus and view.hud.modal.is_ancestor_of(root.gui_get_focus_owner()))
	view.hud.stash_show.emit();await _sync();await _capture("stash")
	_check("actual read-only stash opened",view.hud.stash_open and view.hud.overlay.visible)
	var stash_controls: Array[Control]=[];view.hud._collect_focus38(view.hud.modal,stash_controls)
	stash_controls[-1].grab_focus();await _key(KEY_ENTER);await _sync()
	_check("stash returns to portrait menu",not view.hud.stash_open and view.run.mode=="menu" and view.hud.modal.find_child("PortraitTexture41",true,false)!=null)
	for spec in [["잿불탄","chapter1.skill.ember"],["연쇄 전류","chapter1.skill.arc"],["서리창","chapter1.skill.frost"]]:
		view.run.mode="menu";view.hud.invalidate();await _sync()
		var controls: Array[Control]=[];view.hud._collect_focus38(view.hud.modal,controls)
		var start: Button
		for control in controls:
			if control is Button and control.text.begins_with(spec[0]):start=control;break
		_check("start exists "+spec[1],is_instance_valid(start))
		if not is_instance_valid(start):_finish();return
		start.grab_focus();await _key(KEY_ENTER);await _sync()
		_check("actual start id "+spec[1],view.run.mode=="playing" and view.run.growth.snapshot().primary==spec[1])
	_check("starting gear continuity",view.run.equipped.size()==view.profile.state.equipped.size())
	var routed := false
	for i in 30:
		view.run.step(Vector2.ZERO);view._consume_events()
		view.world.update_camera(view.run.hero.position,1.0/60.0);view.actors.sync(view.run,1.0/60.0);view.effects.sync(view.run,1.0/60.0);view.hud.sync(view.run,1.0/60.0)
		routed=routed or view.effects.frost39_projectile_count>0 or view.effects.frost39_cast_count>0
		await process_frame
	_check("inherited cold events reach FX39",routed)
	_check("inherited route panel visible",view.hud._route40.visible and view.hud._route_labels40.size()==3)
	await _capture("combat")
	await _actor_states42()
	_check("profile bytes unchanged",FileAccess.get_file_as_string("user://chapter-one-profile-v1.json")==original_profile)
	_finish()
func _finish() -> void:
	var failed := false
	for check in result.checks:
		if not check.passed:failed=true
	result.success=not failed
	var file := FileAccess.open(output.path_join("PACKAGED-INTEGRATION.json"),FileAccess.WRITE);file.store_string(JSON.stringify(result,"  "));file.close()
	view.audio.reset();print("PACKAGED42_INTEGRATION ",JSON.stringify(result));quit(1 if failed else 0)
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
	result.checks.append({"name":label,"passed":passed});print("PACKAGED42 ",label," = ",passed)

func _actor_states42() -> void:
	var actor: Node3D
	var entity: Dictionary={}
	for candidate in view.actors.actors.values():
		if view.actors._is34(candidate):
			var current: Dictionary=view.actors._entity(candidate)
			if not current.is_empty() and current.hp_raw>0:
				actor=candidate;entity=current;break
	_check("live walker available for state checks",is_instance_valid(actor))
	if not is_instance_valid(actor):return
	# Disposable in-memory run only; no profile persist or terminal run is requested.
	var saved := entity.duplicate(true)
	entity.frozen_until=view.run.tick+60
	view.actors.sync(view.run,1.0/60.0)
	_check("frozen walker remains live with pose",entity.hp_raw>0 and actor.has_meta("minion19_pose"))
	entity.frozen_until=0;entity.stunned_until=view.run.tick+60
	var before: Dictionary=actor.get_meta("minion19_pose",{}).duplicate(true)
	var holds: int=view.actors.stun36_pose_holds
	view.actors.sync(view.run,1.0/60.0)
	_check("stun holds prior paid pose",view.actors.stun36_pose_holds>holds and actor.get_meta("minion19_pose",{})==before)
	entity.hp_raw=0;entity.dead_tick=view.run.tick;entity.stunned_until=0
	view.actors.sync(view.run,1.0/60.0)
	var pose: Dictionary=actor.get_meta("minion19_pose",{})
	_check("death uses inherited death clip",pose.get("clip","")=="death" and pose.get("dead",false))
	entity.clear();entity.merge(saved,true)
