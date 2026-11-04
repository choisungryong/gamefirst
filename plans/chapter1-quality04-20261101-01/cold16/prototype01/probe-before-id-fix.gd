extends SceneTree
const New=preload("C:/Project/d2r-combat-baseline/chapter1/core/chapter_run_quality16.gd")
const Old=preload("res://chapter1/core/chapter_run.gd")
const Pilot=preload("res://chapter1/core/chapter_pilot.gd")
var checks := 0
var failures: Array[String]=[]
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:failures.append(message);push_error("COLD16_FAILED "+message)
func _initialize() -> void:call_deferred("execute")
func context(run: RefCounted,evolved: bool=true,budget: int=64) -> Dictionary:
	var effects: Dictionary=run.growth._skills["chapter1.skill.frost"].evolution.duplicate(true)
	return {"uid":101,"skill_id":"chapter1.skill.frost","effects":effects,"remaining_hits":budget,"hit_ids":[],"evolved":evolved}
func fixture() -> RefCounted:
	var run=New.new();run.start(90131,"chapter1.skill.frost");run.enemies.clear();run.events.clear()
	for data in [["walker",Vector2.ZERO,12],["walker",Vector2(1,0),20],["walker",Vector2(2,0),12],["elite",Vector2(2.5,0),1000]]:
		run._spawn(data[0],data[1]);var e: Dictionary=run.enemies[run._enemy_sequence];e.hp_raw=data[2]*256;e.max_hp_raw=e.hp_raw
	run._rebuild_grid();return run
func execute() -> void:
	var run=fixture();var paid := context(run);run._damage_enemy(1,paid,0)
	check(run.enemies[1].hp_raw==0,"direct evolved cold kills ordinary12HP")
	check(run.enemies[2].hp_raw==6*256,"normal secondary damage is14HP/50%")
	check(run.enemies[3].hp_raw==0,"secondary kills another12HP target")
	check(run.enemies[4].hp_raw==993*256,"elite secondary damage is7HP/25%")
	var shatters := 0
	for event in run.events:
		if event.type=="shatter":shatters+=1;check(event.cause=="cold_death","new proc identified as actual cold death")
	check(shatters==1,"secondary death cannot recursively create another shatter")
	check(paid.remaining_hits==60,"direct plus3secondaries share original64hit budget")
	run=fixture();paid=context(run,false);run.growth._evolved.assign(["chapter1.skill.frost"]);run._damage_enemy(1,paid,0)
	check(run.enemies[2].hp_raw==20*256 and run.enemies[3].hp_raw==12*256,"old paid non-evolved hit cannot borrow later rank")
	run=fixture();paid=context(run,true,1);run._damage_enemy(1,paid,0)
	check(paid.remaining_hits==0 and run.enemies[2].hp_raw==20*256,"exhausted global cast budget forbids secondary damage")
	run=fixture();paid=context(run,true);paid.effects.shatter_count=0;run._damage_enemy(1,paid,0)
	check(run.enemies[2].hp_raw==20*256,"no paid shatter count means no new proc")
	var pacing: Array=[]
	for id_ in ["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"]:
		var game=New.new();game.start(90131,id_);var pilot=Pilot.new();pilot.run=game;var actual_shatters := 0;var seen := -1
		for i in 40000:
			var move: Vector2=pilot.decide();game.step(move)
			for event in game.events:
				if int(event.seq)<=seen:continue
				seen=int(event.seq)
				if event.type=="shatter":actual_shatters+=1
			if game.mode in ["victory","defeat"]:break
		var result := {"primary":id_,"mode":game.mode,"tick":game.tick,"seconds":float(game.tick)/60,"kills":game.kills,"level":game.growth.snapshot().level,"shatters":actual_shatters,"snapshot":game.snapshot()}
		pacing.append(result);print("COLD16_PACING ",JSON.stringify({"primary":id_,"mode":game.mode,"seconds":result.seconds,"kills":game.kills,"shatters":actual_shatters}))
		check(game.mode=="victory" and game.tick>=300*60 and game.tick<=480*60,"5–8minute normal pacing "+id_)
	var info := {"checks":checks,"failures":failures,"pacing":pacing,"scope":"New independent cold rule prototype on exact14 inherited core, normal policy/seed90131 no HP/rank grants. Headless simulation, not GPU/manual/packaged/performance approval. Root14 preload unchanged."}
	var file := FileAccess.open("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/cold16/prototype01/result.json",FileAccess.WRITE);file.store_string(JSON.stringify(info,"\t"));file.close();print("COLD16_RULE_TEST ",JSON.stringify({"checks":checks,"failures":failures}));quit(0 if failures.is_empty()else 1)
