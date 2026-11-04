extends SceneTree
const Profile=preload("res://chapter1/core/chapter_profile.gd")
const Items=preload("res://chapter1/core/chapter_items.gd")
const Chapter=preload("res://chapter1/core/chapter_run.gd")
var checks := 0
var failures: Array[String]=[]
func _initialize() -> void:call_deferred("execute")
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:failures.append(message);push_error("PROFILE_PROCESS_FAILED "+message)
func execute() -> void:
	var phase := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--profile-phase="):phase=arg.get_slice("=",1)
	check(phase in ["create","restart","finish"],"recognized isolated phase")
	var qa_user_dir := OS.get_user_data_dir()
	check(qa_user_dir.ends_with("AshenCloisterChapterOneProfileProcessQA20261101B"),"unique QA user directory")
	var profile=Profile.new();check(profile.configure(),"real default user path accepted")
	if phase=="create":
		check(not FileAccess.file_exists(profile.path) and profile.state.items.is_empty(),"new namespace initially empty")
		var items: Array=[]
		for i in 3:items.append(Items.unique(i,8))
		check(profile.record_run("process-run-one",items,[],true,21000),"write three nonempty rewards")
		for id_ in [1,2,3]:check(profile.select_item(id_),"persist selection %d"%id_)
		check(profile.state.items.size()==3 and profile.state.completed_runs==1 and profile.state.revision==4,"create state and revisions")
	else:
		check(profile.state.items.size()==3 and profile.state.equipped=={"weapon":1,"charm":2,"ring":3},"new process reads all gear and selections")
		check(profile.state.completed_runs==1 and profile.state.best_ticks==21000,"completion survived process exit")
		var run=Chapter.new();check(run.start(90131),"fresh actual ChapterRun starts")
		check(run.import_starting_gear(profile.starting_gear()),"selected persisted gear imports")
		check(run.inventory.size()==3 and run.effective_skill("chapter1.skill.ember").effects.projectiles==2,"actual starting inventory and projectile modifier")
		check(run.hero.hp_raw==run.hero.max_hp_raw and run.tick==0,"fresh battle boundary health")
		if phase=="restart":
			var before := FileAccess.get_file_as_string(profile.path)
			check(profile.record_run("process-run-one",[],[],true,1) and FileAccess.get_file_as_string(profile.path)==before,"receipt replay across process is exact no-op")
			check(profile.record_run("process-run-two",run.inventory,[],false,100),"write later defeat without duplicating starters")
		else:
			check(profile.state.revision==5 and profile.state.items.size()==3 and profile.state.completed_runs==1,"third process retains defeat receipt and nonduplicated gear")
			check("process-run-two"in profile.state.receipts,"defeat receipt survived process exit")
	var result := {"phase":phase,"checks":checks,"failures":failures,"namespace":qa_user_dir,"state":profile.state,"scope":"Actual independent Godot process/default user path using exact14 core files, isolated QA namespace; backend restart/import only, not native stash UI, concurrent CAS race or power-loss approval"}
	print("PROFILE_PROCESS14 ",JSON.stringify(result))
	var path := "res://"+phase+"-result.json";var file := FileAccess.open(path,FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close()
	quit(0 if failures.is_empty()else 1)
