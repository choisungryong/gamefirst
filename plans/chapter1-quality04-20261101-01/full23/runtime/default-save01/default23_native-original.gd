extends SceneTree
var view: Node
var previous := ""
var victory_at := -1.0
var captured: Dictionary={}
var reload_only := false
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	reload_only="--default23-reload" in OS.get_cmdline_user_args()
	var namespace: String=ProjectSettings.get_setting("application/config/custom_user_dir_name","")
	if namespace!="AshenCloisterChapterOneQuality23":push_error("Wrong default profile namespace");quit(1);return
	var exists := FileAccess.file_exists("user://chapter-one-profile-v1.json")
	if exists!=reload_only:push_error("Preserve existing default profile; expected fresh for first run, present for reload");quit(1);return
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	if not view.profile.available or view._profile_off or view.profile.path!="user://chapter-one-profile-v1.json":push_error("Actual default profile unavailable");quit(1);return
	view.tree_exiting.connect(_save)
	if not reload_only:
		while view.run.tick<23830:view.run.step(view.full_pilot.decide())
		view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
		view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.hud.sync(view.run,0)
	print("DEFAULT23_READY ",JSON.stringify({"reload":reload_only,"default_path":ProjectSettings.globalize_path(view.profile.path),"items":view.profile.state.items.size(),"revision":view.profile.state.revision,"scope":"Actual23 default user:// path, no configure override. First run normal earned23830tick checkpoint then live ending; reload uses native UI. Not manual fullrun."}))
func _process(_delta: float) -> bool:
	if not is_instance_valid(view):return false
	if not reload_only and view.run.mode=="victory" and victory_at<0:
		victory_at=view._wall_age;view._quit_after=view._wall_age+2.3
	if victory_at>=0:
		for at in [.35,.9,1.6]:
			if view._wall_age-victory_at>=at and not captured.has(str(at)):
				captured[str(at)]=true;view._capture_file("default23-ending-%.2f.png"%at)
	var signature := str([view.run.mode,view.hud.stash_open,view.run.equipped,view.profile.state.revision,view.profile.state.equipped])
	if signature!=previous:
		previous=signature;print("DEFAULT23_UI_STATE ",JSON.stringify({"mode":view.run.mode,"stash":view.hud.stash_open,"run_equipped":view.run.equipped,"profile":view.profile.state,"profile_note":view.hud.profile_note}))
	return false
func _save() -> void:
	print("DEFAULT23_FINAL ",JSON.stringify({"mode":view.run.mode,"tick":view.run.tick,"profile":view.profile.state,"default_path":ProjectSettings.globalize_path(view.profile.path),"profile_path":view.profile.path,"profile_available":view.profile.available,"saved_receipt":view._saved_receipt,"scope":"Actual23 default user path and UI evidence; normal checkpoint/policy ending is not manual fullrun."}))
