extends SceneTree
var casters: Array[MeshInstance3D]=[]
func _initialize() -> void:call_deferred("_study")
func _collect(node: Node) -> void:
	if node is MeshInstance3D:casters.append(node)
	for child in node.get_children():_collect(child)
func _study() -> void:
	DirAccess.make_dir_recursive_absolute("res://space29-shots")
	var view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view);view.set_process(false);view.set_physics_process(false)
	var records: Array[Dictionary]=[];var all_same := true
	for tick in [2800,16000]:
		while view.run.tick<tick:view.run.step(view.full_pilot.decide())
		view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
		view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
		casters.clear()
		for actor in view.actors.actors.values():
			if actor.has_meta("minion19"):_collect(actor.get_meta("minion19").model)
		var frozen: Dictionary=view.run.snapshot().duplicate(true)
		for enabled in [false,true]:
			for mesh in casters:mesh.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON if enabled else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			for frame in 8:await RenderingServer.frame_post_draw
			var label := "after" if enabled else "before"
			var img := root.get_texture().get_image();img.save_png("res://space29-shots/%d-%s.png"%[tick,label])
			var same: bool=frozen==view.run.snapshot();all_same=all_same and same
			records.append({"tick":tick,"shadows_enabled":enabled,"casters":casters.size(),"same_complete_core":same,"image":[img.get_width(),img.get_height()]})
	view.audio.reset()
	var f := FileAccess.open("res://space29-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"records":records,"all_same":all_same,"scope":"Same source28 checkpoint/camera/material/light energies. Toggle only actual ordinary/middle-elite model mesh shadow casting. SSAO remains original off. Frozen GPU study; not performance/package29/manual/full quality approval."},"\t"));f.close()
	for frame in 4:await process_frame
	quit(0 if all_same else 1)
