extends "res://chapter1/chapter_one_view.gd"
var checks: Dictionary={}
func _ready() -> void:
	super._ready()
	set_process(false);set_physics_process(false)
	var baseline: Dictionary=run.snapshot()
	var entity: Dictionary=run.enemies.values()[0]
	var saved: Dictionary=entity.duplicate(true)
	var n := 1000000
	for fixture in [
		{"name":"cold_normal","skill":"chapter1.skill.frost","elite":false,"kind":"walker","hp":0,"expected":true},
		{"name":"fire_normal","skill":"chapter1.skill.ember","elite":false,"kind":"walker","hp":0,"expected":false},
		{"name":"arc_normal","skill":"chapter1.skill.arc","elite":false,"kind":"walker","hp":0,"expected":false},
		{"name":"cold_elite_flag","skill":"chapter1.skill.frost","elite":true,"kind":"walker","hp":0,"expected":false},
		{"name":"cold_boss_kind","skill":"chapter1.skill.frost","elite":false,"kind":"elite","hp":0,"expected":false},
		{"name":"living_target","skill":"chapter1.skill.frost","elite":false,"kind":"walker","hp":1,"expected":false}]:
		actors.reset();entity.hp_raw=fixture.hp;entity.elite=fixture.elite;entity.kind=fixture.kind;entity.dead_tick=run.tick
		n+=1
		actors.consume([{"type":"death","seq":n,"tick":run.tick,"position":entity.position,"target_id":entity.id,"skill_id":fixture.skill,"kind":entity.kind,"elite":entity.elite}])
		checks[fixture.name]=(not actors.get("_cold_corpses").is_empty())==fixture.expected
	entity.clear();entity.merge(saved,true);actors.reset()
	checks["core_restored_after_fixtures"]=baseline==run.snapshot()
	checks["hero_never_tracked"]=actors.get("_cold_corpses").is_empty()
	var f := FileAccess.open("res://exclusions-result.json",FileAccess.WRITE);f.store_string(JSON.stringify(checks,"\t"));f.close()
	var failed := false
	for value in checks.values():if not value:failed=true
	audio.reset()
	for i in 4:await get_tree().process_frame
	get_tree().quit(1 if failed else 0)
