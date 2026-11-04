extends SceneTree
func _initialize() -> void:call_deferred("_test")
func _same(a: Node3D,b: Node3D) -> bool:
	if a.get_meta("minion19").model.scale!=b.get_meta("minion19").model.scale:return false
	var sa: Dictionary=a.get_meta("minion19");var sb: Dictionary=b.get_meta("minion19")
	for i in sa.skeleton.get_bone_count():
		if not sa.skeleton.get_bone_pose(i).is_equal_approx(sb.skeleton.get_bone_pose(i)):return false
	if sa.has("staff21") and not sa.staff21.position.is_equal_approx(sb.staff21.position):return false
	return true
func _test() -> void:
	var view=load("res://chapter1/ChapterOne.tscn").instantiate();view.actors=load("res://chapter1/view/chapter_actors_quality30c.gd").new();root.add_child(view);view.set_process(false);view.set_physics_process(false)
	var control=load("res://chapter1/view/chapter_actors_quality30b.gd").new();control.setup(view)
	while view.run.tick<2800:view.run.step(view.full_pilot.decide())
	view.run.events.clear();view.actors.reset();control.reset()
	var same := true;var comparisons := 0;var original: Dictionary=view.run.snapshot().duplicate(true)
	for frame in 60:
		view.run.events.clear();view.run.step(view.full_pilot.decide());view.actors.consume(view.run.events);control.consume(view.run.events)
		var frozen: Dictionary=view.run.snapshot().duplicate(true)
		view.actors.sync(view.run,1.0/60);control.sync(view.run,1.0/60)
		for key in view.actors.actors:
			var a: Node3D=view.actors.actors[key];var b: Node3D=control.actors[key]
			if a.has_meta("minion19"):same=same and _same(a,b);comparisons+=1
		same=same and frozen==view.run.snapshot()
	var held := true
	var frozen: Dictionary=view.run.snapshot().duplicate(true)
	view.run.mode="choice";view.actors.sync(view.run,0);control.sync(view.run,0)
	for key in view.actors.actors:
		if view.actors.actors[key].has_meta("minion19"):held=held and _same(view.actors.actors[key],control.actors[key])
	view.run.mode=frozen.mode
	var reset_same := true
	view.actors.reset();control.reset();view.actors.sync(view.run,0);control.sync(view.run,0)
	for key in view.actors.actors:
		if view.actors.actors[key].has_meta("minion19"):reset_same=reset_same and _same(view.actors.actors[key],control.actors[key])
	var checks := {"normal_per_bone_model_staff_equal":same,"freeze_equal":held,"pool_recheckout_equal":reset_same,"core_unchanged_by_presenters":frozen==view.run.snapshot(),"compared_more_than_4000_actors":comparisons>4000,"pool224_both":view.actors.pool25_created==224 and control.pool25_created==224}
	var ok := true
	for value in checks.values():ok=ok and value
	var f := FileAccess.open("res://crowd30-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"passed":ok,"comparisons":comparisons,"start_tick":original.tick,"end_tick":view.run.tick,"scope":"Exact per-bone/model/staff equivalence of original30b and allocation-reduced30c on60 normal-policy steps, modal and pool recheckout. Same core reference. Not performance/manual/visual approval."},"\t"));f.close()
	view.audio.reset()
	for i in 4:await process_frame
	quit(0 if ok else 1)
