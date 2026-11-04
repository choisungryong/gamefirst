extends SceneTree
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
	DirAccess.make_dir_recursive_absolute("res://space31-shots")
	var view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view);view.set_process(false);view.set_physics_process(false)
	var clearance_ok := true;var moved := 0
	for node in view.world._solid_columns31:
		clearance_ok=clearance_ok and node.cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
	var rows: Array=[];var same_all := true
	for tick in [2800,12600,19800]:
		while view.run.tick<tick:view.run.step(view.full_pilot.decide())
		view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear();view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
		var frozen: Dictionary=view.run.snapshot().duplicate(true)
		for enabled in [false,true]:
			view.world.set_columns31(enabled)
			for i in 8:await RenderingServer.frame_post_draw
			var label := "after" if enabled else "before"
			var image := root.get_texture().get_image();image.save_png("res://space31-shots/%d-%s.png"%[tick,label])
			var same: bool=frozen==view.run.snapshot();same_all=same_all and same
			rows.append({"tick":tick,"solid_columns":enabled,"same_complete_core":same,"image":[image.get_width(),image.get_height()],"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)})
	var file := FileAccess.open("res://space31-result.json",FileAccess.WRITE);file.store_string(JSON.stringify({"rows":rows,"same_complete_core_all":same_all,"shadow_only_modes":clearance_ok,"columns":view.world.columns31.size(),"moved_out_of_walkable":moved,"clearance_records":view.world.clearance31,"batches":view.world._solid_columns31.size(),"scope":"Same source30 normal cold checkpoints, camera/actor poses/core/lights fixed. Authored column impostors/contact remain visible unchanged. Toggle hidden3D shadow-only proxies in two batches at original prop origins. Proxies are not visible meshes or colliders. Original props split into batches; not bitwise original22 rendering. Shadow proxy radii.78x and heights1.144x original billboard-derived dimensions. Not product31/manual/performance approval."},"\t"));file.close()
	view.audio.reset();view.queue_free();view=null
	for i in 8:await process_frame
	quit(0 if same_all and clearance_ok else 1)
