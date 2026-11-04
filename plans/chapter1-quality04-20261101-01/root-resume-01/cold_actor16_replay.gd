extends "res://chapter1/chapter_one_view.gd"
var groups := 0
var next_group := 0
var pending: Array[Dictionary]=[]
var seq := -1
var armed := false
var checks: Dictionary={}
func _ready() -> void:
	super._ready()
	while run.tick<3240:run.step(full_pilot.decide())
	actors.reset();effects.reset();run.events.clear()
	world.update_camera(run.hero.position,10);actors.sync(run,0);world.sync(run,0);hud.invalidate();hud.sync(run,54)
	_save_json("start",run.snapshot());armed=true
func _save_json(name_: String,value: Variant) -> void:
	var f := FileAccess.open("res://"+name_+".json",FileAccess.WRITE);f.store_string(JSON.stringify(value,"\t"));f.close()
func _consume_events() -> void:
	super._consume_events()
	if not armed:return
	for event in run.events:
		if int(event.seq)<=seq:continue
		seq=int(event.seq)
		if event.type=="shatter" and groups<4 and run.tick>=next_group:
			groups+=1;next_group=run.tick+90
			for offset in [0,6,15,30]:pending.append({"group":groups,"tick":run.tick+offset,"offset":offset})
func _process(delta: float) -> void:
	super._process(delta)
	if not armed:return
	var keep: Array[Dictionary]=[]
	for shot in pending:
		if run.tick<int(shot.tick):keep.append(shot)
		else:_shot(shot)
	pending=keep
func _shot(shot: Dictionary) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://shots")
	get_viewport().get_texture().get_image().save_png("res://shots/shatter-%02d-after%02d.png"%[shot.group,shot.offset])
func _print_result() -> void:
	super._print_result()
	_save_json("end",run.snapshot())
	if actors.get("_cold_corpses")!=null:_verify_actor()
	_save_json("checks",checks)
func _verify_actor() -> void:
	var before: Dictionary=run.snapshot()
	var bodies: Dictionary=actors.get("_cold_corpses")
	checks["tracked_normal_cold_deaths"]=not bodies.is_empty()
	var original_mode: String=run.mode
	# Inspect real corpses from this ordinary replay, then exercise modal time
	# without advancing the core. This is separate from the saved end snapshot.
	if not bodies.is_empty():
		var key: String=bodies.keys()[0]
		var sprite: AnimatedSprite3D=actors.actors[key].get_meta("sprite")
		bodies[key].age=.06
		for mode_ in ["paused","choice","inventory"]:
			run.mode=mode_;actors.sync(run,0)
			var tint: Color=sprite.modulate
			for i in 12:actors.sync(run,.04)
			checks[mode_+"_holds_age_and_color"]=is_equal_approx(bodies[key].age,.06) and sprite.modulate.is_equal_approx(tint)
		run.mode="victory";actors.sync(run,.23)
		checks["terminal_fades"]=is_zero_approx(sprite.modulate.a)
		var count_: int=bodies.size();actors.consume(run.events)
		checks["event_replay_deduped"]=bodies.size()==count_
	run.mode=original_mode
	checks["core_unchanged_by_visual_checks"]=before==run.snapshot()
	actors.reset()
	checks["reset_clears_records_and_seq"]=actors.get("_cold_corpses").is_empty() and actors.get("_cold_event")==-1
