extends "res://chapter1/chapter_one_view.gd"
var observed := {"frozen_hit_events":0,"shatter_events":0,"normal_frozen_hit_events":0,"normal_frozen_alive_tick_samples":0,"elite_frozen_alive_tick_samples":0,"max_frozen_alive":0,"peak_ice_instances":0}
var observer_seq := -1
func _consume_events() -> void:
	for event in run.events:
		if int(event.seq)<=observer_seq:continue
		observer_seq=int(event.seq)
		if event.type=="shatter":observed.shatter_events+=1
		elif event.type=="hit" and event.get("frozen",false):
			observed.frozen_hit_events+=1
			var e: Dictionary=run.enemies.get(event.target_id,{})
			if not e.is_empty() and not e.elite:observed.normal_frozen_hit_events+=1
	super._consume_events()
func _physics_process(delta: float) -> void:
	super._physics_process(delta)
	if run.mode!="playing":return
	var count_ := 0
	for e in run.enemies.values():
		if e.hp_raw<=0 or run.tick>=int(e.frozen_until):continue
		count_+=1
		if e.elite:observed.elite_frozen_alive_tick_samples+=1
		else:observed.normal_frozen_alive_tick_samples+=1
	observed.max_frozen_alive=maxi(observed.max_frozen_alive,count_)
func _process(delta: float) -> void:
	super._process(delta)
	observed.peak_ice_instances=maxi(observed.peak_ice_instances,effects.ice_batch.multimesh.visible_instance_count)
func _print_result() -> void:
	super._print_result()
	print("COLD_NORMAL_OBSERVER14 ",JSON.stringify({"mode":run.mode,"tick":run.tick,"observed":observed,"scope":"Passive external observer on actual packaged14/default core+pilot, headlessfixed60seed90131; no gameplay changes, not GPU/manual/performance"}))
