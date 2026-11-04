extends SceneTree
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
	DirAccess.make_dir_recursive_absolute("res://space29-shots")
	var view=load("res://chapter1/ChapterOne.tscn").instantiate();view.world=load("res://chapter1/view/chapter_world_quality29.gd").new();root.add_child(view)
	view.set_process(false);view.set_physics_process(false)
	var records: Array[Dictionary]=[];var same_all := true
	for tick in [2800,16000]:
		while view.run.tick<tick:view.run.step(view.full_pilot.decide())
		view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
		view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
		var frozen: Dictionary=view.run.snapshot().duplicate(true)
		for mode in ["before","quiet","strong"]:
			view.world.configure29(mode!="before",mode=="strong")
			for frame in 8:await RenderingServer.frame_post_draw
			var img := root.get_texture().get_image();img.save_png("res://space29-shots/%d-%s.png"%[tick,mode])
			var same: bool=frozen==view.run.snapshot();same_all=same_all and same
			var environment_: Environment=view.world.environment29
			records.append({"tick":tick,"mode":mode,"same_complete_core":same,"image":[img.get_width(),img.get_height()],"ssao":environment_.ssao_enabled,"radius":environment_.ssao_radius,"intensity":environment_.ssao_intensity,"light_affect":environment_.ssao_light_affect})
	view.audio.reset()
	var f := FileAccess.open("res://space29-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"records":records,"all_same":same_all,"scope":"Source28 components/World29 unconnected lighting study. Same normal earned frozen checkpoints; SSAO off/quiet/strong, no light energy or geometry change. Actual GPU screens, not performance/package29/manual/quality approval."},"\t"));f.close()
	for frame in 4:await process_frame
	quit(0 if same_all else 1)
