extends SceneTree
const New=preload("C:/Project/d2r-combat-baseline/chapter1/core/chapter_run_quality16.gd")
const HUD=preload("C:/Project/d2r-combat-baseline/chapter1/view/chapter_hud_quality16.gd")
var checks := 0
var failures: Array[String]=[]
func _initialize() -> void:call_deferred("execute")
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok:failures.append(message);push_error("COLD16_SEMANTIC_FAILED "+message)
func fixture() -> RefCounted:
	var run=New.new();run.start(90131,"chapter1.skill.frost");run.enemies.clear();run.events.clear();run._enemy_sequence=0
	for row in [["walker",Vector2.ZERO,12],["walker",Vector2(1,0),20],["walker",Vector2(2,0),12],["elite",Vector2(2.5,0),1000]]:
		run._spawn(row[0],row[1]);var e: Dictionary=run.enemies[run._enemy_sequence];e.hp_raw=row[2]*256;e.max_hp_raw=e.hp_raw
	run._rebuild_grid();return run
func paid(run: RefCounted,evolved: bool,budget: int=64) -> Dictionary:
	var skill: Dictionary=run.growth._skills["chapter1.skill.frost"]
	var effect: Dictionary=(skill.evolution if evolved else skill.ranks[3]).duplicate(true)
	return {"uid":1,"skill_id":"chapter1.skill.frost","effects":effect,"remaining_hits":budget,"hit_ids":[],"evolved":evolved}
func execute() -> void:
	var run=fixture();var context := paid(run,false,32);run.enemies[1].frozen_until=75;run._damage_enemy(1,context,0)
	check(run.enemies[2].hp_raw==2*256 and run.enemies[4].hp_raw==982*256,"legacy rank4 frozen shatter retains full18HP secondary damage")
	var count_ := 0
	for event in run.events:
		if event.type=="shatter":count_+=1;check(event.cause=="frozen"and event.normal_damage_divisor==1,"legacy cause/scale remain explicit")
	check(count_==1 and context.remaining_hits==28,"legacy shared budget and no recursive shatter")
	run=fixture();context=paid(run,true,2);run._damage_enemy(1,context,0)
	check(context.remaining_hits==0 and run.enemies[2].hp_raw==6*256 and run.enemies[3].hp_raw==12*256,"secondary stops at original remaining2 budget")
	check(run.metrics.hits["chapter1.skill.frost"]==2 and run.metrics.damage_raw==42*256,"metrics preserve raw attack28 plus secondary14 including existing overkill semantics")
	var before: Dictionary=run.snapshot();run._damage_enemy(1,context,0);check(run.snapshot()==before,"dead target/exhausted cast cannot replay")
	run=fixture();context=paid(run,true);context.effects.proc_depth=0;run._damage_enemy(1,context,0)
	check(run.enemies[2].hp_raw==20*256,"no proc depth means no new evolved death proc")
	run=fixture();context=paid(run,true);run.enemies[1].hp_raw=100*256;run._damage_enemy(1,context,0)
	check(run.enemies[1].hp_raw==72*256 and run.enemies[2].hp_raw==20*256,"surviving hit cannot emit death damage")
	var hud=HUD.new();var after: Dictionary=run.growth._skills["chapter1.skill.frost"].evolution
	var text: String=hud._card_description({"kind":"evolve","skill_id":"chapter1.skill.frost","after":after},run)
	check(text.contains("파쇄3.5m")and text.contains("50%")and text.contains("25%"),"evolution description states real radius/scales")
	check(not text.contains("범위 2.8m")and not text.contains("빙결된 적 처치 시 파쇄"),"obsolete radius/kill prerequisite absent for evolved cold")
	var legacy: String=hud._card_description({"kind":"rank","rank":4,"skill_id":"chapter1.skill.frost","after":run.growth._skills["chapter1.skill.frost"].ranks[3]},run)
	check(legacy.contains("빙결된 적 처치 시 파쇄"),"rank4 description retains frozen prerequisite")
	var result := {"checks":checks,"failures":failures,"description":text,"legacy_description":legacy,"scope":"Focused new-rule legacy compatibility, paid budgets/conditions/metrics and pure description strings; no GPU text bounds/manual/art/performance approval."}
	var file := FileAccess.open("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/cold16/semantic05/result.json",FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close();print("COLD16_SEMANTIC ",JSON.stringify(result));quit(0 if failures.is_empty()else 1)
