extends "res://chapter1/chapter_one_view.gd"
## Declared presentation arena, NOT a normal run/earned build or performance.
## Same authored placement/loadout in before13/after14; real ChapterRun.step
## owns casts, hit positions, frozen_until and shatter/death decisions.
var captured := {}
var counts := {"frozen_hits":0,"shatter":0,"arc_casts":0,"frost_casts":0}
var _fixture_seq := -1
var _finished := false
var _max_frozen := 0
var _variant := "after14"
var _result_path := "res://elements-result.json"
const CAPTURE_TICKS := [18,78,138,198,258,318,378,438,482,488,498,546,606,666,726]
func _ready() -> void:
	super._ready()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--elements-variant="):_variant=arg.get_slice("=",1)
	run.enemies.clear();run.projectiles.clear();run.orbs.clear();run.items.clear();actors.reset();effects.reset()
	run.growth._ranks={"chapter1.skill.frost":4};run.growth._evolved.assign(["chapter1.skill.frost"])
	run.growth._primary="chapter1.skill.frost";run.growth._level=11;run.growth._xp=1180
	run._next_spawn=999999;run._next_cast.clear()
	run.hero.max_hp_raw=5000*256;run.hero.hp_raw=run.hero.max_hp_raw
	for i in 80:
		var angle := float(i)*2.399963;var radius := 5.0+float(i%7)*.78
		run._spawn("charger" if i%5==0 else "walker",Vector2(cos(angle),sin(angle))*radius)
		var e: Dictionary=run.enemies[run._enemy_sequence];e.hp_raw=140*256;e.max_hp_raw=e.hp_raw;e.definition.speed=.75
	run.events.clear();world.update_camera(run.hero.position,10)
	print("ELEMENTS_FIXTURE_SCOPE ",JSON.stringify({"variant":_variant,"setup":"80placed enemies with140HP/.75speed; supplied evolved frost4; arc4 evolved added at8seconds; hero5000HP; automatic growth choices suppressed","normal_run":false,"damage_from":"actual ChapterRun.step"}))
func _physics_process(_delta: float) -> void:
	if _finished:return
	if run.tick==480:run.growth._ranks["chapter1.skill.arc"]=4;run.growth._evolved.append("chapter1.skill.arc")
	run.step(Vector2.ZERO,false)
	# Research loadout remains fixed; do not count this as earned progression.
	run.growth._pending.clear();run.growth._offer.clear()
	if run.mode=="choice":run.mode="playing"
	for e in run.events:
		if int(e.seq)<=_fixture_seq:continue
		_fixture_seq=int(e.seq)
		if e.type=="hit" and e.get("frozen",false):counts.frozen_hits+=1
		elif e.type=="shatter":counts.shatter+=1
		elif e.type=="cast":
			if e.skill_id=="chapter1.skill.arc":counts.arc_casts+=1
			elif e.skill_id=="chapter1.skill.frost":counts.frost_casts+=1
	var frozen := 0
	for e in run.enemies.values():
		if e.hp_raw>0 and run.tick<int(e.frozen_until):frozen+=1
	_max_frozen=maxi(_max_frozen,frozen)
	_consume_events();hud.invalidate()
func _process(delta: float) -> void:
	super._process(delta)
	if _finished:return
	for tick_ in CAPTURE_TICKS:
		if run.tick>=tick_ and not captured.has(tick_):
			captured[tick_]=true
			await RenderingServer.frame_post_draw
			var path := "res://fixture-captures/"+_variant+"-%04d.png"%tick_
			DirAccess.make_dir_recursive_absolute(path.get_base_dir())
			if not FileAccess.file_exists(path):get_viewport().get_texture().get_image().save_png(path)
	if run.tick>=780:
		_finished=true
		var result := {"variant":_variant,"tick":run.tick,"kills":run.kills,"counts":counts,"max_frozen":_max_frozen,"metrics":run.metrics.duplicate(true),"hero":run.hero.duplicate(true),"growth":run.growth.snapshot(),"scope":"Configured arena actual core events, not normal chapter/earned progression/manual/audio/performance"}
		print("ELEMENTS_ARENA_RESULT ",JSON.stringify(result))
		var file := FileAccess.open(_result_path,FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"));file.close()
