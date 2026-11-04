extends SceneTree
var folder := ""
var variant := "25b"
var view: Node3D
var stamp: Label
var rows: Array[Dictionary]=[]
func _initialize() -> void:call_deferred("_study")
func _capture(phase: String,index: int) -> void:
	stamp.text="QA %s · %s · frame %03d · tick %d"%[variant,phase,index,view.run.tick]
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image()
	img.save_png(folder.path_join("%s-%03d.png"%[phase,index]))
	var angles: Dictionary={}
	if phase=="attack":
		for actor in view.actors.actors.values():angles[String(actor.get_meta("kind"))]=actor.rotation.y
	rows.append({"phase":phase,"frame":index,"tick":view.run.tick,"core_sha256":JSON.stringify(view.run.snapshot()).sha256_text(),"angles":angles,"image":[img.get_width(),img.get_height()]})
func _study() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--mapped-dir="):folder=arg.trim_prefix("--mapped-dir=")
		if arg.begins_with("--mapped-actor="):variant=arg.trim_prefix("--mapped-actor=")
	if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
	DirAccess.make_dir_recursive_absolute(folder)
	view=load("res://chapter1/ChapterOne.tscn").instantiate();view.actors=load("res://chapter1/view/chapter_actors_quality%s.gd"%variant).new();root.add_child(view)
	view.set_process(false);view.set_physics_process(false)
	var canvas := CanvasLayer.new();root.add_child(canvas);stamp=Label.new();stamp.position=Vector2(16,130);stamp.add_theme_font_size_override("font_size",14);canvas.add_child(stamp)
	while view.run.tick<16000:view.run.step(view.full_pilot.decide())
	view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear();view.hud.sync(view.run,3)
	view.world.update_camera(view.run.hero.position,10)
	for frame in 120:
		view.run.events.clear();view.run.step(view.full_pilot.decide());view._consume_events()
		view.world.update_camera(view.run.hero.position,1.0/60);view.world.sync(view.run,1.0/60);view.actors.sync(view.run,1.0/60);view.effects.sync(view.run,1.0/60);view.hud.sync(view.run,1.0/60)
		await _capture("normal",frame)
	var normal_snapshot: Dictionary=view.run.snapshot().duplicate(true)
	var saved_enemies: Dictionary=view.run.enemies;var saved_tick: int=view.run.tick;var saved_zone: int=view.run.zone;var saved_hero: Dictionary=view.run.hero.duplicate(true)
	var template: Dictionary=saved_enemies.values()[0];var fixture: Dictionary={};var roles := ["walker","ranged","charger","elite"];var directions := [Vector2.RIGHT,Vector2.UP,Vector2.LEFT,Vector2.DOWN]
	for i in 4:
		var e: Dictionary=template.duplicate(true);e.id=900000+i;e.kind=roles[i];e.elite=roles[i]=="elite";e.hp_raw=1000;e.frozen_until=0;e.position=Vector2(-3+i*2,-4);e.direction=directions[i];e.attack_direction=directions[i];e.attack_kind="fan" if roles[i]=="ranged" else "line";e.definition=view.run.ENEMY_DEFS[roles[i]].duplicate(true);e.state="windup";e.state_until=100000+int(e.definition.windup);fixture[e.id]=e
	view.run.zone=0;view.run.enemies=fixture;view.run.hero.position=Vector2.ZERO;view.run.tick=100000
	view.actors.reset();view.effects.reset();view.hud.root.visible=false;view.actors.sync(view.run,0);view.actors.hero.visible=false
	var camera := root.get_camera_3d();camera.position=Vector3(10,15,9);camera.look_at(Vector3(0,.8,-4));camera.size=9
	for actor in view.actors.actors.values():
		var e: Dictionary=view.actors._entity(actor)
		if not e.is_empty():actor.rotation.y=atan2(e.attack_direction.x,e.attack_direction.y)
	var sequence := 1000000
	for frame in 180:
		view.run.tick=100000+frame
		for e in fixture.values():
			if frame==int(e.definition.windup):
				e.state="recover";e.direction=e.attack_direction.orthogonal();e.state_until=view.run.tick+int(e.definition.recover)
				view.actors.consume([{"seq":sequence,"type":"enemy_attack","target_id":e.id,"tick":view.run.tick,"attack_kind":e.attack_kind,"kind":e.kind,"position":e.position}]);sequence+=1
			elif e.state=="recover" and view.run.tick>=int(e.state_until):e.state="idle"
		view.actors.sync(view.run,1.0/60);view.actors.hero.visible=false
		await _capture("attack",frame)
	view.run.enemies=saved_enemies;view.run.tick=saved_tick;view.run.zone=saved_zone;view.run.hero=saved_hero;view.actors.reset()
	var restored: bool=normal_snapshot==view.run.snapshot()
	var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"rows":rows,"normal_end_tick":saved_tick,"normal_core":normal_snapshot,"complete_normal_core_restored":restored,"hit_blends":view.actors.get("hit28_blends"),"scope":"Own PNG per frame,120 consecutive normal-policy steps then180 copied-role attack fixture frames. Explicit frame/tick/hash map. One role per cardinal direction; fixture intentionally gives stale travel direction during recover. Encode60fps without startup/cleanup frames. Source QA, not actual package28/manual/performance."},"\t"));f.close()
	view.audio.reset()
	for i in 4:await process_frame
	quit(0 if restored else 1)
