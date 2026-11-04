extends RefCounted
## Output-only QA boundary. Captures and traces never mutate combat state.
## https://docs.godotengine.org/en/4.5/classes/class_renderingserver.html#class-renderingserver-signal-frame-post-draw

static func capture(viewport: Viewport, path: String) -> Dictionary:
	await RenderingServer.frame_post_draw
	var image: Image = viewport.get_texture().get_image()
	var result: Error = image.save_png(path)
	print("FRAMEBUFFER_CAPTURE ",result," ",path)
	return {"error":result,"saved":result == OK,"size":image.get_size()}

static func write_report(view: Node) -> bool:
	var absolute_dir: String = ProjectSettings.globalize_path(view.report_dir)
	var mkdir_result: Error = DirAccess.make_dir_recursive_absolute(absolute_dir)
	if mkdir_result != OK:
		push_error("Cannot create report directory: "+view.report_dir)
		return false
	var file := FileAccess.open(view.report_dir+"/scene-run.json",FileAccess.WRITE)
	if not file:
		push_error("Cannot open scene-run report: "+view.report_dir)
		return false
	var sim: RefCounted = view.sim
	var logical_corpses: int = sim.enemies.size()-sim.alive_count()
	var rendered_corpses := 0
	for state in sim.enemies.values():
		if state.state == "dead" and view.actor_registry.actor_for(state) != null: rendered_corpses += 1
	file.store_string(JSON.stringify({"scope":"independent game experiment; not D2R mechanics or crowd performance validation","engine":Engine.get_version_info().string,"tick":sim.tick,"shots":sim.shots,"hits":sim.hits,"enemy_state":sim.enemy.get("state","none"),"requested_enemies":sim.initial_count,"alive":sim.alive_count(),"entities":sim.enemies.size(),"actor_count":view.actor_registry.actors.size(),"logical_corpses":logical_corpses,"rendered_corpses":rendered_corpses,"culled_corpses":view.actor_registry.culled_corpses,"corpse_ticks":sim.corpse_ticks,"broadphase_candidates":sim.broadphase_candidates,"narrowphase_checks":sim.narrowphase_checks,"mana_raw":sim.mana_raw,"events":sim.history,"capture":view.capture_path,"capture_saved":view.capture_saved,"framebuffer_width":view.capture_size.x,"framebuffer_height":view.capture_size.y},"  "))
	file.flush()
	return file.get_error() == OK

