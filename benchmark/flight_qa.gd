extends "res://baseline_view.gd"
## GPU functional case: real sustained skill authority with no targets, not perf.
func _ready() -> void:
	initial_enemies = 0
	super._ready()
	set_process(false)
	set_physics_process(false)
	var output := "user://phase3-flight-qa"
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--flight-output="): output = argument.trim_prefix("--flight-output=")
	if DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output)) != OK:
		get_tree().quit(1)
		return
	var maximum_bolts := 0
	var maximum_sprites := 0
	var atlas_frames: Dictionary = {}
	var paused_ok := false
	var saved := false
	var image_size := Vector2i.ZERO
	var snapshot_tick := 0
	var shots_before := 0
	var flight_aim: Vector2 = sim.player+Vector2(0,-50)
	for step_index in range(180):
		sim.mana_raw = sim.mana_max_raw
		sim.step(true,flight_aim)
		for event in sim.events: handle_event(event)
		super._process(sim.STEP)
		maximum_bolts = maxi(maximum_bolts,sim.bolts.size())
		maximum_sprites = maxi(maximum_sprites,projectile_nodes.size())
		for sprite in projectile_nodes.values(): atlas_frames[str(sprite.frame_coords)] = true
		await RenderingServer.frame_post_draw
		if maximum_bolts == 4 and not saved:
			var result: Dictionary = await QAOutput.capture(get_viewport(),output+"/four-flight-bolts.png")
			saved = result.saved
			image_size = result.size
			snapshot_tick = sim.tick
			shots_before = sim.shots
			var frozen: Array = [sim.tick,sim.bolts.duplicate(true),particles.map(func(p): return [p.life,p.node.position]),projectile_nodes.values().map(func(sprite): return [sprite.position,sprite.frame_coords])]
			toggle_pause()
			for pause_index in range(20):
				sim.step(true,flight_aim)
				super._process(.05)
				await RenderingServer.frame_post_draw
			paused_ok = frozen == [sim.tick,sim.bolts,particles.map(func(p): return [p.life,p.node.position]),projectile_nodes.values().map(func(sprite): return [sprite.position,sprite.frame_coords])]
			toggle_pause()
	var shot_count: int = sim.shots
	var actual_ticks: int = sim.tick
	restart()
	var clean: bool = sim.bolts.is_empty() and projectile_nodes.is_empty() and particles.is_empty()
	for sprite in effect_presenter.projectile_pool: clean = clean and not sprite.visible
	for particle in effect_presenter.particle_pool: clean = clean and not particle.visible
	var pass_: bool = maximum_bolts == 4 and maximum_sprites == 4 and atlas_frames.size() >= 4 and paused_ok and clean and saved
	var report: Dictionary = {"scope":"actual sustained cast/flight/atlas/pause/reset GPU functional QA; no performance claim","success":pass_,"engine":Engine.get_version_info(),"rendering_method":RenderingServer.get_current_rendering_method(),"maximum_bolts":maximum_bolts,"maximum_sprites":maximum_sprites,"atlas_frames":atlas_frames.keys(),"paused_bolts_atlas_particles_unchanged":paused_ok,"reset_clears_bindings_hides_pools":clean,"snapshot_tick":snapshot_tick,"snapshot_shots":shots_before,"simulated_ticks":actual_ticks,"shots":shot_count,"cycle_ticks":sim.cycle_ticks,"projectile_life_ticks":roundi(float(sim.params.projectile_life_seconds)*60),"capture_saved":saved,"framebuffer_width":image_size.x,"framebuffer_height":image_size.y,"fixture":"zero targets; real cast every33ticks,180simulated60Hzticks; mana refreshed for functional coverage"}
	var file := FileAccess.open(output+"/flight-qa.json",FileAccess.WRITE)
	if not file:
		get_tree().quit(1)
		return
	file.store_string(JSON.stringify(report,"  "))
	file.flush()
	print("ACTUAL_SKILL_FLIGHT_QA ",JSON.stringify(report))
	get_tree().quit(0 if pass_ and file.get_error() == OK else 1)
