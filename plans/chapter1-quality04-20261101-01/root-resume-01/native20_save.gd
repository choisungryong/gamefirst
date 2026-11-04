extends SceneTree
var view: Node
var last_state := ""
var captured: Dictionary={}
var victory_at := -1.0
var reload_only := false
const QA_PROFILE := "res://plans/chapter1-quality04-20261101-01/qa-native20/profile.json"
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	reload_only="--native20-reload" in OS.get_cmdline_user_args()
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	DirAccess.make_dir_recursive_absolute(QA_PROFILE.get_base_dir())
	var configured: bool=view.profile.configure(QA_PROFILE,true)
	if not configured:push_error(view.profile.error);quit(1);return
	view._profile_off=false;view._saved_receipt="";view._sync_profile("격리 저장 검증 · 기존 저장과 별도")
	view.tree_exiting.connect(_save)
	if not reload_only:
		while view.run.tick<23830:view.run.step(view.full_pilot.decide())
		view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
		view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.hud.sync(view.run,0)
	print("NATIVE20_READY ",JSON.stringify({"reload":reload_only,"profile":ProjectSettings.globalize_path(QA_PROFILE),"revision":view.profile.state.revision,"items":view.profile.state.items.size(),"tick":view.run.tick,"scope":"Actual package20 resources/UI/profile class; normal earned build resimulated23830 then live ending, isolated QA path; no manual-fullrun claim."}))
func _process(_delta: float) -> bool:
	if not is_instance_valid(view):return false
	if view.run.mode=="victory" and victory_at<0:victory_at=view._wall_age
	if victory_at>=0:
		for at in [.35,.9,1.2,1.6]:
			if view._wall_age-victory_at>=at and not captured.has(str(at)):
				captured[str(at)]=true;view._capture_file("native20-ending-%.2f.png"%at)
	var state_ := str([view.run.mode,view.hud.stash_open,view.run.equipped,view.profile.state.revision,view.profile.state.equipped])
	if state_!=last_state:
		last_state=state_;print("NATIVE20_UI_STATE ",JSON.stringify({"mode":view.run.mode,"stash":view.hud.stash_open,"run_equipped":view.run.equipped,"profile":view.profile.state,"selected":view.hud._selected_item}))
	return false
func _save() -> void:
	print("NATIVE20_FINAL ",JSON.stringify({"mode":view.run.mode,"tick":view.run.tick,"profile":view.profile.state,"profile_path":ProjectSettings.globalize_path(QA_PROFILE),"saved_receipt":view._saved_receipt,"scope":"Isolated QA profile/native UI evidence; default user profile never configured."}))
