extends "res://chapter1/chapter_one_view.gd"
var seen_shots: Dictionary={}
var records: Array[Dictionary]=[]
func _process(delta: float) -> void:
	super._process(delta)
	if hud._discovery_left<.5 or hud._discovery_left>2.8:return
	if hud.discovery20_history.is_empty():return
	var record: Dictionary=hud.discovery20_history[-1]
	if seen_shots.has(record.uid):return
	seen_shots[record.uid]=true
	var found := false
	for item in run.inventory:
		if item.uid==record.uid:
			found=item.quality==record.quality and item.slot==record.slot and item.name==record.name
	assert(found)
	var rect: Rect2=hud._discovery.get_global_rect()
	assert(rect.size.y<=140 and rect.end.y<get_viewport().get_visible_rect().size.y*.4)
	records.append({"tick":run.tick,"receipt":record.duplicate(true),"actually_owned":found,"card_rect":rect})
	_capture_discovery20(record.uid)
func _capture_discovery20(uid: int) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://discovery-shots")
	get_viewport().get_texture().get_image().save_png("res://discovery-shots/item-%03d.png"%uid)
func _print_result() -> void:
	super._print_result()
	var reference=ChapterRun.new();var policy=ChapterPilot.new();policy.run=reference
	var started: bool=reference.start(seed_,primary)
	assert(started)
	while reference.tick<run.tick:reference.step(policy.decide())
	var same: bool=reference.snapshot()==run.snapshot()
	var f := FileAccess.open("res://discovery-result.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"receipts":records,"history":hud.discovery20_history,"same_complete_core_as_independent_policy":same,"tick":run.tick,"scope":"Actual normal earned-inventory discovery replay, no item grants; fixed60 source GPU, not full/manual/performance."},"\t"));f.close()
	assert(same)
