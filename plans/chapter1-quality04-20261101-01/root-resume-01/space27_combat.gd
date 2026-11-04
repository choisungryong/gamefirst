extends SceneTree
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
	DirAccess.make_dir_recursive_absolute("res://space27-shots")
	var view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view.set_process(false);view.set_physics_process(false)
	var initial: Dictionary=view.run.snapshot().duplicate(true)
	var records: Array[Dictionary]=[]
	var all_same := true
	for tick in [16000,23000]:
		while view.run.tick<tick:view.run.step(view.full_pilot.decide())
		view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
		view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0)
		view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,0)
		var frozen: Dictionary=view.run.snapshot().duplicate(true)
		var floor_mesh: MeshInstance3D=view.world.root.get_child(0)
		var material_: ShaderMaterial=floor_mesh.material_override
		if material_==null:material_=floor_mesh.mesh.surface_get_material(0)
		var old_shader: Shader=material_.shader
		for revision in [22,27]:
			material_.shader=old_shader if revision==22 else load("res://chapter1/view/chapter_ground_quality27.gdshader")
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			var img := root.get_texture().get_image()
			img.save_png("res://space27-shots/%d-tick%d.png"%[revision,tick])
			var same: bool=frozen==view.run.snapshot();all_same=all_same and same
			records.append({"revision":revision,"tick":tick,"zone":view.run.zone,"mode":view.run.mode,"same_complete_core":same,"size":[img.get_width(),img.get_height()]})
		material_.shader=old_shader
	view.audio.reset()
	var f := FileAccess.open("res://space27-result.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"records":records,"all_same":all_same,"scope":"Same candidate26 source components and normal earned frost checkpoints, only floor shader switched. Frozen presentation comparison with actual actors/core projectiles, not live motion/manual/packaged27/performance approval."},"\t"));f.close()
	for i in 4:await process_frame
	quit(0 if all_same else 1)
