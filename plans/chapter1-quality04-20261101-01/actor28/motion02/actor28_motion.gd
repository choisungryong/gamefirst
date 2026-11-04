extends SceneTree
var output := ""
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--motion-output="):output=arg.trim_prefix("--motion-output=")
	if output.is_empty() or DirAccess.dir_exists_absolute(output):quit(1);return
	DirAccess.make_dir_recursive_absolute(output)
	var records: Array[Dictionary]=[]
	var restored_all := true
	for revision in ["25b","28"]:
		var view=load("res://chapter1/ChapterOne.tscn").instantiate();view.actors=load("res://chapter1/view/chapter_actors_quality%s.gd"%revision).new();root.add_child(view)
		view.set_process(false);view.set_physics_process(false);view.hud.root.visible=false
		var original: Dictionary=view.run.snapshot().duplicate(true)
		var saved_enemies: Dictionary=view.run.enemies;var saved_tick: int=view.run.tick
		var source: Dictionary=saved_enemies.values()[0]
		var fixture: Dictionary={};var roles := ["walker","ranged","charger","elite"]
		for i in roles.size():
			var e: Dictionary=source.duplicate(true);e.id=100000+i;e.kind=roles[i];e.elite=roles[i]=="elite";e.position=Vector2(-3+i*2,-4);e.state="move";e.hp_raw=1000;e.frozen_until=0;e.attack_kind="fan" if roles[i]=="ranged" else "line"
			fixture[e.id]=e
		view.run.enemies=fixture;view.run.tick=100;view.actors.reset();view.actors.sync(view.run,.016);view.actors.hero.visible=false
		var camera := root.get_camera_3d();camera.position=Vector3(10,15,9);camera.look_at(Vector3(0,.8,-4));camera.size=9.0
		var sequence := 1000000
		for pair in [{"name":"north","direction":Vector2.UP},{"name":"east","direction":Vector2.RIGHT},{"name":"south","direction":Vector2.DOWN},{"name":"west","direction":Vector2.LEFT}]:
			view.run.tick=100
			for e in fixture.values():
				e.direction=pair.direction;e.attack_direction=pair.direction
				view.actors.consume([{"seq":sequence,"type":"hit","target_id":e.id,"tick":100,"position":e.position}]);sequence+=1
			for actor in view.actors.actors.values():actor.rotation.y=atan2(pair.direction.x,pair.direction.y)
			for age in [0,2,4,6,8,10,12,18]:
				view.run.tick=100+age
				var before: Dictionary=view.run.snapshot().duplicate(true)
				view.actors.sync(view.run,2.0/60);view.actors.hero.visible=false
				await RenderingServer.frame_post_draw
				await RenderingServer.frame_post_draw
				var img := root.get_texture().get_image();var filename: String="%s-%s-%02d.png"%[revision,pair.name,age];img.save_png(output.path_join(filename))
				records.append({"file":filename,"revision":revision,"direction":pair.name,"hit_age_ticks":age,"same_fixture_core":before==view.run.snapshot(),"image":[img.get_width(),img.get_height()]})
		view.run.enemies=saved_enemies;view.run.tick=saved_tick;view.actors.reset()
		restored_all=restored_all and original==view.run.snapshot();view.audio.reset();view.queue_free()
		await process_frame
	var f := FileAccess.open(output.path_join("RESULT.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"records":records,"complete_original_core_restored":restored_all,"scope":"Source25b vs source28, same copied four-role fixtures/4directions/controlled hit ages. Sampled motion study, not actual whole gameplay, native input or performance."},"\t"));f.close()
	for i in 4:await process_frame
	quit(0 if restored_all else 1)
