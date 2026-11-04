extends "res://chapter1/chapter_one_view.gd"
## Core-only replay of the ordinary policy to120s; no HP/rank/item grants.
## Then record18s normally. Cosmetic state starts clear at the boundary;
## discard first1s from the comparison. Never claim real-time/full/manual.
var _variant := "after15"
var _paid: Dictionary={}
var _observer_seq := -1
var _armed := false
var _next_kill_capture := 0
var _kill_groups := 0
var _pending: Array[Dictionary]=[]
var _snapshots: Array=[]
var _paired_deaths := 0

func _ready() -> void:
	super._ready()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--replay-variant="):_variant=arg.get_slice("=",1)
	for i in 7200:
		var movement: Vector2=full_pilot.decide()
		run.step(movement)
	actors.reset();effects.reset();run.events.clear()
	world.update_camera(run.hero.position,10);actors.sync(run,1.0/60.0);world.sync(run,0);hud.invalidate();hud.sync(run,120)
	_armed=true
	var file := FileAccess.open("res://replay-start.json",FileAccess.WRITE);file.store_string(JSON.stringify(run.snapshot(),"\t"));file.close()
	print("COLD_REPLAY_SCOPE ",JSON.stringify({"variant":_variant,"start_tick":run.tick,"start_kills":run.kills,"resimulation":"7200normal policy/core steps; no HP/rank/item grants","boundary":"clear cosmetic state, discard first1s","scope":"Offline short replay, not realtime/full chapter/manual/audio/performance"}))

func _consume_events() -> void:
	if _armed:
		for event in run.events:
			if int(event.seq)<=_observer_seq:continue
			_observer_seq=int(event.seq)
			if event.type=="hit":_paid=event
			elif event.type=="death" and event.skill_id=="chapter1.skill.frost" and not _paid.is_empty():
				if int(event.seq)==int(_paid.seq)+1 and int(event.target_id)==int(_paid.target_id) and _paid.skill_id==event.skill_id and _paid.get("evolved",false) and not _paid.get("shatter",false):
					_paired_deaths+=1
					if run.tick>=_next_kill_capture and _kill_groups<6:
						_next_kill_capture=run.tick+75;_kill_groups+=1
						for offset in [0,6,15]:_pending.append({"group":_kill_groups,"event_seq":event.seq,"death_tick":run.tick,"capture_after":run.tick+offset,"offset":offset,"position":event.position})
	super._consume_events()

func _process(delta: float) -> void:
	super._process(delta)
	if not _armed:return
	var keep: Array[Dictionary]=[]
	for request in _pending:
		if run.tick<int(request.capture_after):keep.append(request);continue
		_snapshots.append({"event_seq":request.event_seq,"death_tick":request.death_tick,"render_tick":run.tick,"offset":request.offset,"at":request.position})
		_save_kill_frame(request)
	_pending=keep

func _save_kill_frame(request: Dictionary) -> void:
	await RenderingServer.frame_post_draw
	var path := "res://replay-captures/%s-kill%02d-after%02d.png"%[_variant,request.group,request.offset]
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	if not FileAccess.file_exists(path):get_viewport().get_texture().get_image().save_png(path)

func _print_result() -> void:
	super._print_result()
	if not _armed:return
	var info := {"variant":_variant,"tick":run.tick,"paired_cold_deaths":_paired_deaths,"event_captures":_snapshots,"core":run.snapshot(),"cosmetic_death_accents":effects.get("cold_death_accents"),"peak_scope":"Snapshots are event-synchronous normal replay, not full run/performance/manual"}
	var file := FileAccess.open("res://replay-result.json",FileAccess.WRITE);file.store_string(JSON.stringify(info,"\t"));file.close()
	print("COLD_REPLAY_RESULT ",JSON.stringify({"variant":_variant,"tick":run.tick,"paired_deaths":_paired_deaths,"snapshots":_snapshots.size()}))
