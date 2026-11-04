extends SceneTree
## External diagnostic only: the shipped benchmark .gdc remains unchanged.
## Absolute --script is supported in release exports:
## https://docs.godotengine.org/en/4.5/tutorials/editor/command_line_tutorial.html
## process_frame runs before every Node._process, so buffer reclamation occurs
## outside the benchmark's gameplay/render/animation callbacks:
## https://docs.godotengine.org/en/4.5/classes/class_scenetree.html
var benchmark
var output := ""
var duration := 300.0
var next_clear := 1.0
var clear_count := 0
var frame_rows_removed := 0
var tick_rows_removed := 0
var maximum_frame_rows := 0
var maximum_tick_rows := 0
var all_clear_states_unchanged := true
var finished_control := false
var observations: Array = []
var control_file: FileAccess
const EXPECTED_METADATA := "1ea1fc0ad4e03042dab4db1c0d6fb343295ad5baaa1f197943ebafef639697dc"

func _initialize() -> void:
	call_deferred("boot")

func boot() -> void:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--control-output="): output = argument.trim_prefix("--control-output=")
		elif argument.begins_with("--control-seconds="):
			var token: String = argument.trim_prefix("--control-seconds=")
			if not token.is_valid_float():
				fail("Invalid control duration")
				return
			duration = float(token)
	if output.is_empty() or not is_finite(duration) or duration < 2.0 or duration > 300.0:
		fail("Control requires an output directory and 2..300 finite seconds")
		return
	if DirAccess.make_dir_recursive_absolute(output) != OK:
		fail("Cannot create control output")
		return
	control_file = FileAccess.open(output+"/control-observations.csv",FileAccess.WRITE)
	if not control_file:
		fail("Cannot create control observations")
		return
	control_file.store_csv_line(PackedStringArray(["bench_elapsed_seconds","sample_elapsed_seconds","tick","removed_frame_rows","removed_tick_rows","alive","rigs","nodes","history","particles_created","particles_reused","clear_state_unchanged"]))
	var packed: PackedScene = load("res://benchmark/crowd_benchmark.tscn")
	if not packed:
		fail("The shipped benchmark PackedScene could not be loaded")
		return
	if current_scene != null:
		fail("Unexpected existing main scene; refusing to duplicate the workload")
		return
	benchmark = packed.instantiate()
	root.add_child(benchmark)
	current_scene = benchmark
	if benchmark.start_usec == 0 or benchmark.bench_mode != "fx" or benchmark.workload != "skill" or benchmark.initial_enemies != 300 or benchmark.sample_seconds <= duration+10.0:
		fail("Shipped benchmark configuration is not the intended control")
		return
	if benchmark.embedded_manifest_hash != EXPECTED_METADATA or Engine.physics_ticks_per_second != 60 or Engine.time_scale != 1.0:
		fail("Build metadata or physics/time configuration differs")
		return
	process_frame.connect(observe_and_reclaim)
	print("MEMORY_CONTROL_READY ",JSON.stringify({"seconds":duration,"base_requested_seconds":benchmark.sample_seconds,"embedded_metadata":benchmark.embedded_manifest_hash,"intervention":"clear numeric rows and tick_rows every1s only; original gameplay/render/AP/FX/CSV callbacks retained"}))

func state_signature() -> Array:
	var sim = benchmark.sim
	var effects = benchmark.effect_presenter
	var registry = benchmark.actor_registry
	return [sim.tick,sim.player,sim.move_target,sim.life,sim.mana_raw,sim.rng.state,sim.enemies.size(),sim.alive_count(),sim.bolts.size(),sim.pending.duplicate(true),sim.shots,sim.hits,sim.kills,sim.history_count(),sim.events.size(),registry.actors.size(),registry.animation_clock_progress,registry.animation_time,effects.particles.size(),effects.projectile_nodes.size(),effects.particle_created,effects.particle_reused,effects.projectile_created,effects.projectile_reused]

func observe_and_reclaim() -> void:
	if finished_control or benchmark == null or benchmark.sample_start_usec == 0: return
	var now: int = Time.get_ticks_usec()
	var sample_elapsed: float = float(now-benchmark.sample_start_usec)/1000000.0
	var bench_elapsed: float = float(now-benchmark.start_usec)/1000000.0
	maximum_frame_rows = maxi(maximum_frame_rows,benchmark.rows.size())
	maximum_tick_rows = maxi(maximum_tick_rows,benchmark.tick_rows.size())
	if sample_elapsed >= next_clear:
		var before: Array = state_signature()
		var removed_frames: int = benchmark.rows.size()
		var removed_ticks: int = benchmark.tick_rows.size()
		# The ONLY steady-state mutation of benchmark storage in this diagnostic.
		# End-of-run finished/sample_end fields are set separately at shutdown.
		benchmark.rows.clear()
		benchmark.tick_rows.clear()
		var state_unchanged: bool = before == state_signature()
		all_clear_states_unchanged = all_clear_states_unchanged and state_unchanged
		frame_rows_removed += removed_frames
		tick_rows_removed += removed_ticks
		clear_count += 1
		var observation: Dictionary = {"bench_elapsed_seconds":bench_elapsed,"sample_elapsed_seconds":sample_elapsed,"tick":benchmark.sim.tick,"removed_frame_rows":removed_frames,"removed_tick_rows":removed_ticks,"alive":benchmark.sim.alive_count(),"rigs":benchmark.actor_registry.actors.size(),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"history":benchmark.sim.history_count(),"particles_created":benchmark.effect_presenter.particle_created,"particles_reused":benchmark.effect_presenter.particle_reused,"clear_state_unchanged":state_unchanged}
		observations.append(observation)
		control_file.store_csv_line(PackedStringArray([str(bench_elapsed),str(sample_elapsed),str(observation.tick),str(removed_frames),str(removed_ticks),str(observation.alive),str(observation.rigs),str(observation.nodes),str(observation.history),str(observation.particles_created),str(observation.particles_reused),str(state_unchanged)]))
		next_clear = floorf(sample_elapsed)+1.0
	if sample_elapsed >= duration:
		finish_control(now,sample_elapsed)

func finish_control(now: int, sample_elapsed: float) -> void:
	finished_control = true
	# End before write_benchmark(): its retained-row statistics would describe only
	# the last partial second and MUST NOT be emitted as a formal performance run.
	benchmark.finished = true
	benchmark.sample_end_usec = now
	benchmark.raw_file.flush()
	benchmark.tick_file.flush()
	control_file.flush()
	var physics_seconds: float = float(benchmark.sim.tick-benchmark.sample_start_tick)/60.0
	var windows: Array = benchmark.animation_probe_windows
	var motion_ok := not windows.is_empty()
	for window in windows:
		motion_ok = motion_ok and int(window.advanced_clock_count) > 0 and bool(window.bone_pose_changed)
	var success: bool = all_clear_states_unchanged and motion_ok and benchmark.sim.alive_count() == 300 and benchmark.actor_registry.actors.size() == 300 and absf(physics_seconds-sample_elapsed) < .1 and benchmark.bench_capture_ok and benchmark.bench_image_size == Vector2i(1920,1080)
	var report: Dictionary = {"success":success,"scope":"non-performance memory-attribution control; unchanged embedded benchmark logic/render/AP/FX; only numeric retention rows reclaimed every1s","not_a_formal_performance_summary":true,"script_path":get_script().resource_path,"script_sha256":FileAccess.get_sha256(get_script().resource_path),"embedded_source_manifest_sha256":benchmark.embedded_manifest_hash,"base_requested_sample_seconds":benchmark.sample_seconds,"actual_sample_seconds":sample_elapsed,"warmup_seconds":benchmark.warmup_seconds,"physics_seconds":physics_seconds,"physics_start_tick":benchmark.sample_start_tick,"physics_end_tick":benchmark.sim.tick,"rendering_method":RenderingServer.get_current_rendering_method(),"configuration_basis":"same embedded final benchmark fx/skill300,HP1e9/mana_refill/near64@60Hz/rest15Hz; only retained numeric arrays cleared","framebuffer_width":benchmark.bench_image_size.x,"framebuffer_height":benchmark.bench_image_size.y,"clear_count":clear_count,"frame_rows_removed":frame_rows_removed,"tick_rows_removed":tick_rows_removed,"maximum_retained_frame_rows":maximum_frame_rows,"maximum_retained_tick_rows":maximum_tick_rows,"clear_state_unchanged":all_clear_states_unchanged,"sample_event_counts":benchmark.event_counts,"cast_proxy_count":benchmark.cast_proxy_count,"animation_probe_windows":windows,"observations":observations,"final_nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"final_pool_counters":{"actors_created":benchmark.actor_registry.created_count,"particles_created":benchmark.effect_presenter.particle_created,"particles_reused":benchmark.effect_presenter.particle_reused},"memory_caveat":"Compare process-memory matched60..300s windows; no claim of zero leak or formal FPS from this control"}
	var file := FileAccess.open(output+"/control-report.json",FileAccess.WRITE)
	if not file:
		fail("Cannot write non-performance control report")
		return
	file.store_string(JSON.stringify(report,"  "))
	file.flush()
	print("MEMORY_CONTROL_RESULT ",JSON.stringify({"success":success,"sample_seconds":sample_elapsed,"clear_count":clear_count,"state_unchanged":all_clear_states_unchanged}))
	quit(0 if success and file.get_error() == OK and benchmark.raw_file.get_error() == OK and benchmark.tick_file.get_error() == OK and control_file.get_error() == OK else 1)

func fail(message: String) -> void:
	printerr("MEMORY_CONTROL_FAILED ",message)
	if benchmark != null: benchmark.finished = true
	quit(1)
