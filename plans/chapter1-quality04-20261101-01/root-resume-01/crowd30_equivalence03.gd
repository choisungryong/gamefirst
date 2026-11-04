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
	var saved_enemies: Dictionary=view.run.enemies;var saved_tick: int=view.run.tick;var saved_mode: String=view.run.mode
	var template: Dictionary=saved_enemies.values()[0];var fixture: Dictionary={}
	var roles := ["walker","ranged","charger"];var directions := [Vector2.RIGHT,Vector2.UP,Vector2.LEFT,Vector2.DOWN]
	for ri in 3:
		for vi in 4:
			for di in 4:
				var e: Dictionary=template.duplicate(true);e.generation=1;e.id=100001+(ri*16+vi*4+di)*4+vi;e.kind=roles[ri];e.elite=false;e.hp_raw=1000;e.frozen_until=0;e.position=Vector2(-10+vi*5,-8+ri*5+float(di)*.4);e.direction=directions[di];e.attack_direction=directions[di];e.attack_kind="fan" if e.kind=="ranged" else "line";e.definition=view.run.ENEMY_DEFS[e.kind].duplicate(true);e.state="windup";e.state_until=100000+int(e.definition.windup);fixture[e.id]=e
	view.run.enemies=fixture;view.run.tick=100000;view.actors.reset();control.reset()
	var attack_same := true;var attack_comparisons := 0;var sequence := 2000000
	for frame in 180:
		view.run.tick=100000+frame;view.run.mode="choice" if frame>=80 and frame<90 else "playing"
		for e in fixture.values():
			if frame==int(e.definition.windup):
				e.state="recover";e.direction=e.attack_direction.orthogonal();e.state_until=view.run.tick+int(e.definition.recover)
				var event := {"seq":sequence,"type":"enemy_attack","kind":e.kind,"target_id":e.id,"tick":view.run.tick,"attack_kind":e.attack_kind,"position":e.position};view.actors.consume([event]);control.consume([event]);sequence+=1
			elif e.state=="recover" and view.run.tick>=int(e.state_until):e.state="idle"
			if frame==120:view.actors._enemy_hit_until[e.id]=view.run.tick+6;control._enemy_hit_until[e.id]=view.run.tick+6
			if frame==150:e.hp_raw=0;e.dead_tick=view.run.tick
		view.actors.sync(view.run,1.0/60);control.sync(view.run,1.0/60)
		for key in view.actors.actors:
			var a: Node3D=view.actors.actors[key];var b: Node3D=control.actors[key]
			attack_same=attack_same and _same(a,b) and is_equal_approx(a.rotation.y,b.rotation.y);attack_comparisons+=1
	view.run.enemies=saved_enemies;view.run.tick=saved_tick;view.run.mode=saved_mode;view.actors.reset();control.reset()
	var checks := {"normal_per_bone_model_staff_equal":same,"roles3_variants4_directions4_attack_hit_death_equal":attack_same,"attack_comparisons8640":attack_comparisons==8640,"freeze_equal":held,"pool_recheckout_equal":reset_same,"core_unchanged_by_presenters":frozen==view.run.snapshot(),"compared_more_than_4000_actors":comparisons>4000,"pool224_both":view.actors.pool25_created==224 and control.pool25_created==224}
	var ok := true
	for value in checks.values():ok=ok and value
	var f := FileAccess.open("res://crowd30-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"passed":ok,"comparisons":comparisons,"attack_comparisons":attack_comparisons,"start_tick":original.tick,"end_tick":view.run.tick,"scope":"Exact per-bone/model/staff equivalence of original30b and allocation-reduced30c on60 normal-policy steps, modal and pool recheckout. Same core reference. Not performance/manual/visual approval."},"\t"));f.close()
	view.audio.reset()
	control=null
	view.queue_free()
	view=null
	for i in 8:await process_frame
	quit(0 if ok else 1)
