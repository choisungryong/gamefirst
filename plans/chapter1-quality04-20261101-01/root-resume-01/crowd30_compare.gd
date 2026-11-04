extends SceneTree
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
	DirAccess.make_dir_recursive_absolute("res://crowd30-shots")
	var view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view);view.set_process(false);view.set_physics_process(false)
	var records: Array[Dictionary]=[];var all_same := true
	for tick in [2800,12600,19800]:
		while view.run.tick<tick:view.run.step(view.full_pilot.decide())
		view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
		view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0)
		var frozen: Dictionary=view.run.snapshot().duplicate(true)
		for enabled in [false,true]:
			view.actors.variants30_enabled=enabled
			view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
			for frame in 8:await RenderingServer.frame_post_draw
			var label := "after" if enabled else "before"
			var img := root.get_texture().get_image();img.save_png("res://crowd30-shots/%d-%s.png"%[tick,label])
			var same: bool=frozen==view.run.snapshot();all_same=all_same and same
			var counts: Dictionary={}
			for actor in view.actors.actors.values():
				if actor.has_meta("variant30_index"):
					var key: String=str(actor.get_meta("kind"))+":"+str(actor.get_meta("variant30_index"));counts[key]=int(counts.get(key,0))+1
			records.append({"tick":tick,"variants_enabled":enabled,"same_complete_core":same,"image":[img.get_width(),img.get_height()],"variant_counts":counts,"created":view.actors.pool25_created,"shared_skins":view.actors.skin24_builds})
	view.audio.reset()
	var f := FileAccess.open("res://crowd30-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"records":records,"all_same":all_same,"scope":"Same frozen normal-earned core/camera/light/pose. Toggle only role-preserving model proportions. Unconnected source study, no new geometry or RNG. Not native/manual/performance/package30 approval."},"\t"));f.close()
	for frame in 4:await process_frame
	quit(0 if all_same else 1)
