extends SceneTree
## Bounded synthetic ground32 diagnostic; separate from formal crowd regression.
var output := ""
var expected := ""
var rows: Array = []
var failures: Array[String] = []
var view: Node
func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--probe-output="): output = arg.trim_prefix("--probe-output=")
		elif arg.begins_with("--expected-metadata="): expected = arg.trim_prefix("--expected-metadata=")
	call_deferred("run")
func advance_sim() -> void:
	if is_instance_valid(view): view.sim.step()
func run() -> void:
	if output.is_empty() or not output.replace("\\","/").contains("/evidence/phase6/") or DirAccess.dir_exists_absolute(output):
		quit(1)
		return
	DirAccess.make_dir_recursive_absolute(output)
	if DisplayServer.get_name() == "headless" or FileAccess.get_sha256("res://game_data/build_info.json") != expected:
		quit(1)
		return
	DisplayServer.window_set_size(Vector2i(1920,1080))
	root.size = Vector2i(1920,1080)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	view = load("res://Baseline.tscn").instantiate()
	view.initial_enemies = 0
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	await process_frame
	for index in range(192):
		if view.sim.ground_loot_snapshot().size() == 32: break
		var state: Dictionary = view.sim.entity(view.sim.spawn_enemy(view.sim.player+Vector2(-4+index%8,-4-int(index/8)%4)))
		state.state = "dead"
		state.life_raw = 0
		view.sim.claim_death_reward(view.sim.handle(state))
		view.sim.despawn_enemy(view.sim.handle(state))
	view.sync_actors()
	physics_frame.connect(advance_sim)
	var started: int = Time.get_ticks_usec()
	var previous := started
	while float(Time.get_ticks_usec()-started)/1000000.0 < 10.0:
		await process_frame
		view.sync_actors()
		var now: int = Time.get_ticks_usec()
		var elapsed: float = float(now-started)/1000000.0
		if elapsed >= 2.0:
			rows.append([elapsed,float(now-previous)/1000.0,view.loot_presenter.markers.size(),view.sim.ground_loot_snapshot().size(),get_node_count()])
		previous = now
	await RenderingServer.frame_post_draw
	var image_: Image = root.get_texture().get_image()
	var saved: bool = image_.save_png(output.path_join("frame-ground32.png")) == OK
	if not saved or image_.get_size() != Vector2i(1920,1080): failures.append("Actual framebuffer capture failed")
	var csv := FileAccess.open(output.path_join("frames.csv"),FileAccess.WRITE)
	csv.store_line("elapsed_seconds,frame_ms,marker_count,ground_count,node_count")
	var values: Array[float] = []
	var node_min := 2147483647
	var node_max := 0
	for row in rows:
		csv.store_line("%f,%f,%d,%d,%d" % row)
		values.append(float(row[1]))
		node_min = mini(node_min,int(row[4]))
		node_max = maxi(node_max,int(row[4]))
		if row[2] != 32 or row[3] != 32: failures.append("Ground/marker fixture changed")
	csv.close()
	values.sort()
	var sampled: float = float(rows[-1][0])-float(rows[0][0]) if rows.size() > 1 else 0.0
	if sampled < 7.9 or values.size() < 2: failures.append("Insufficient sample")
	var report := {"scope":"Synthetic stationary ground32 marker diagnostic, 2s warmup + 8s sample; fixed 60Hz core steps and presentation sync, no enemies or deaths during timed sample; distinct from formal crowd regression and normal gameplay", "success":failures.is_empty(),"failures":failures,"sample_count":rows.size(),"sample_seconds":sampled,"frame_ms":{"p95":values[clampi(ceili(values.size()*.95)-1,0,values.size()-1)],"worst":values[-1]},"node_min":node_min,"node_max":node_max,"ground":32,"markers":32,"framebuffer":[image_.get_width(),image_.get_height()],"renderer":RenderingServer.get_current_rendering_method(),"metadata_sha256":expected,"executable":OS.get_executable_path(),"external_script_sha256":FileAccess.get_sha256(get_script().resource_path)}
	var file := FileAccess.open(output.path_join("summary.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"\t"))
	file.close()
	print(JSON.stringify(report))
	physics_frame.disconnect(advance_sim)
	view.free()
	quit(0 if failures.is_empty() else 1)
