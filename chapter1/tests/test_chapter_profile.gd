extends SceneTree
const Profile=preload("res://chapter1/core/chapter_profile.gd")
const Items=preload("res://chapter1/core/chapter_items.gd")
const Chapter=preload("res://chapter1/core/chapter_run.gd")
var checks := 0
var failures: Array[String]=[]
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:failures.append(message);push_error(message)
func _initialize() -> void:call_deferred("execute")
func execute() -> void:
	var directory := "res://plans/chapter1-quality04-20261101-01/root-resume-01/profile-fixtures-01"
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--fixture-dir="):directory=arg.trim_prefix("--fixture-dir=")
	check(not DirAccess.dir_exists_absolute(directory),"Fresh isolated fixture directory")
	if DirAccess.dir_exists_absolute(directory):quit(1);return
	DirAccess.make_dir_recursive_absolute(directory)
	var profile=Profile.new()
	check(not profile.configure(),"Baseline default profile refuses old application directory")
	check(profile.configure(directory+"/profile.json",true),"New QA profile configured")
	var rng := RandomNumberGenerator.new();rng.seed=44
	var item: Dictionary=Items.roll(rng,8,"rare","weapon");item.uid=3
	check(profile.record_run("run-one",[item],[],true,21000),"Atomic reward save")
	check(profile.state.items.size()==1 and profile.state.completed_runs==1,"Owned loot and completion saved")
	var first_text := FileAccess.get_file_as_string(profile.path)
	check(profile.record_run("run-one",[item],[],true,21000) and FileAccess.get_file_as_string(profile.path)==first_text,"Receipt repeat is exact no-op")
	var reopened=Profile.new();check(reopened.configure(profile.path,true),"JSON numeric canonicalization reload")
	check(reopened.state==profile.state,"Roundtrip state equality")
	var id_: int=reopened.state.items[0].storage_id
	check(reopened.select_item(id_),"Select persistent gear")
	var gear: Array[Dictionary]=reopened.starting_gear();check(gear.size()==1 and gear[0].storage_id==id_,"Selected gear carries persistent identity")
	var run=Chapter.new();run.start(4)
	check(run.import_starting_gear(gear) and run.inventory.size()==1,"Fresh run imports selected gear")
	check(run.hero.hp_raw==run.hero.max_hp_raw and run.tick==0,"Fresh-boundary full health")
	run.tick=1;check(not run.import_starting_gear(gear),"Mid-run gear import forbidden")
	check(reopened.record_run("run-two",run.inventory,[],false,100),"Defeat saves without duplicating existing gear")
	check(reopened.state.items.size()==1 and reopened.state.completed_runs==1,"Starter gear not duplicated and defeat not completed")
	check(not profile.select_item(id_) and profile.error.contains("다른 실행"),"Stale writer refused and external save preserved")
	check(reopened.salvage(id_) and reopened.state.items.is_empty() and reopened.state.equipped.is_empty() and reopened.state.essence==8,"Explicit salvage clears equipped reference and records reward")
	var broken := Profile.fresh();broken.items=[{"storage_id":1,"item":Items.unique(0,5)}];broken.next_id=2;broken.equipped={"body":1}
	check(Profile.normalize(broken).is_empty(),"Wrong-slot equipped reference rejected")
	broken.equipped={};broken.items[0].item.stats.damage_bps=999999
	check(Profile.normalize(broken).is_empty(),"Forged stat range rejected")
	broken.items[0].item=Items.unique(0,5);broken.items[0].item.stats.damage_bps=1200
	check(Profile.normalize(broken).is_empty(),"Forged valid-range unique identity rejected")
	var corrupt_path := directory+"/corrupt.json";var f := FileAccess.open(corrupt_path,FileAccess.WRITE);f.store_string("{bad profile");f.close()
	var bad=Profile.new();check(not bad.configure(corrupt_path,true),"Corrupt profile refused")
	check(not bad.record_run("attempt",[item],[],true,1) and FileAccess.get_file_as_string(corrupt_path)=="{bad profile","Corrupt bytes not overwritten")
	# Capacity fixture exercises bounded recovery, not normal loot generation.
	var full=Profile.new();full.configure(directory+"/full.json",true)
	var candidate := Profile.fresh()
	for i in 256:candidate.items.append({"storage_id":i+1,"item":Items.unique(i%3,5)})
	candidate.next_id=257
	check(full._persist(candidate),"Nominal256 stash persists")
	var inventory: Array=[];var pending: Array=[]
	for i in 65:inventory.append(Items.unique(i%3,5))
	for i in 4:pending.append(Items.unique(i%3,5))
	check(full.record_run("full-recovery",inventory,pending,true,22000) and full.state.items.size()==325,"All69 final rewards preserved at full stash")
	check(full.state.items.size()>256,"Recovery requires sorting before next run")
	var recovered=Profile.new();check(recovered.configure(full.path,true) and recovered.state.items.size()==325,"Full recovery roundtrip")
	var revision_count := 0;var dir := DirAccess.open(directory)
	for name in dir.get_files():
		if name.contains(".revision-"):revision_count+=1
	check(revision_count>=6,"Prior immutable revisions remain")
	if "--negative" in OS.get_cmdline_user_args():check(false,"Intentional checker failure")
	print("CHAPTER_PROFILE_TEST ",JSON.stringify({"checks":checks,"failures":failures,"fixtures":directory,"scope":"New isolated profile fixture files only; old equipment/progress not read or written"}))
	quit(0 if failures.is_empty() else 1)
