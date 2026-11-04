extends "res://baseline_view.gd"
## Synthetic fixed-count immortal stress; never normal gameplay or art acceptance.
## APIs: https://docs.godotengine.org/en/4.5/classes/class_renderingserver.html
var bench_mode := "rig"
var warmup_seconds := 10.0
var sample_seconds := 60.0
var output_dir := "user://phase3"
var bench_phase := "development"
var fixture_bolts := 300
var workload := "projectile_stress"
var event_counts: Dictionary = {}
var skill_event_counts: Dictionary = {}
var bench_skill_ids: Array[String] = []
var bench_skill_index := 0
var skill_event_file: FileAccess
var cast_proxy_count := 0
var require_target := false
var bench_equipment := false
var start_usec := 0
var sample_start_usec := 0
var previous_usec := 0
var rows: Array = []
var tick_rows: Array = []
var finished := false
var capture_busy := false
var bench_image_size := Vector2i.ZERO
var bench_capture_ok := false
var capture_elapsed := -1.0
var frame_sim_ms := 0.0
var frame_sync_ms := 0.0
var frame_physics_ticks := 0
var static_actors: Dictionary = {}
var static_template: Array = []
var total_physics_ticks := 0
var sample_start_tick := 0
var bad_arguments: Array[String] = []
var source_hashes: Dictionary = {}
var source_hashes_basis := "live development source files"
var embedded_manifest_hash := ""
var raw_file: FileAccess
var tick_file: FileAccess
var peak_sample_buffer_bytes := 0
var visual_event_queue: Array = []
var sample_end_usec := 0
var animation_probe_windows: Array = []
var probe_window_start := 0.0
var probe_clock_count := 0
var previous_probe_pose: Array = []
var probe_skeleton: Skeleton3D

func _input(_event: InputEvent) -> void:
	pass

func _unhandled_input(_event: InputEvent) -> void:
	pass

func numeric(argument: String, prefix: String, minimum: float, maximum: float) -> float:
	var token: String = argument.trim_prefix(prefix)
	if not token.is_valid_float():
		bad_arguments.append("Invalid number "+prefix)
		return minimum
	var value: float = float(token)
	if not is_finite(value) or value < minimum or value > maximum:
		bad_arguments.append("Out of range "+prefix)
		return minimum
	return value

func _ready() -> void:
	initial_enemies = 300
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--bench-mode="): bench_mode = argument.trim_prefix("--bench-mode=")
		elif argument.begins_with("--bench-warmup="): warmup_seconds = numeric(argument,"--bench-warmup=",0,600)
		elif argument.begins_with("--bench-seconds="): sample_seconds = numeric(argument,"--bench-seconds=",.05,3600)
		elif argument.begins_with("--bench-output="): output_dir = argument.trim_prefix("--bench-output=")
		elif argument.begins_with("--bench-phase="): bench_phase = argument.trim_prefix("--bench-phase=")
		elif argument.begins_with("--bench-workload="): workload = argument.trim_prefix("--bench-workload=")
		elif argument.begins_with("--bench-bolts="):
			var token: String = argument.trim_prefix("--bench-bolts=")
			if not token.is_valid_int() or int(token) < 0 or int(token) > 1000: bad_arguments.append("Invalid bolt count")
			else: fixture_bolts = int(token)
		elif argument == "--bench-require-target": require_target = true
		elif argument == "--bench-equipment": bench_equipment = true
	if not bench_mode in ["sim","static","rig","fx"]: bad_arguments.append("Invalid mode")
	if not workload in ["skill","multi_skill","projectile_stress"]: bad_arguments.append("Invalid workload")
	if workload == "multi_skill" and bench_mode != "fx": bad_arguments.append("Multi-skill workload requires fx mode")
	if not bad_arguments.is_empty():
		printerr(JSON.stringify({"benchmark_arguments_valid":false,"errors":bad_arguments}))
		get_tree().quit(1)
		return
	if DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(output_dir)) != OK:
		printerr("Cannot create benchmark output")
		get_tree().quit(1)
		return
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	DisplayServer.window_set_size(Vector2i(1920,1080))
	super._ready()
	if bench_equipment:
		if not sim.equipment_valid or not sim.replace_equipment_context({"actor_tag":"caster","level":2}):
			printerr("Synthetic equipment context rejected")
			get_tree().quit(1)
			return
		for item in sim.equipment_items():
			if not sim.equip_item(int(item.uid)):
				printerr("Synthetic equipment transaction rejected: ",sim.equipment_errors)
				get_tree().quit(1)
				return
	sim.profiling_enabled = true
	actor_registry.animation_lod_enabled = not OS.get_cmdline_user_args().has("--no-animation-lod")
	sim.life = 1000000000.0
	if workload == "multi_skill":
		var player_definition: Dictionary = sim.catalog.snapshot().player
		if not sim.replace_player_modifiers([{"source_id":"benchmark.fixture","id":"high_hp","stat_id":player_definition.health_stat_id,"operation":"add","value":1000000000-sim.life_max_raw}]):
			printerr("Synthetic player HP modifier rejected: ",sim.stat_errors)
			get_tree().quit(1)
			return
		sim.life = 1000000000.0/256.0
		bench_skill_ids = sim.available_skill_ids()
		for id_ in bench_skill_ids: skill_event_counts[id_] = {}
	sim.mana_raw = sim.mana_max_raw
	var columns: int = ceili(sqrt(float(initial_enemies)*1.4))
	var index := 0
	for state in sim.enemies.values():
		state.life_raw = 1000000000
		state.max_raw = 1000000000
		state.p = Vector2((index%columns-float(columns-1)*.5)*.65,(floori(float(index)/columns)-float(ceili(float(initial_enemies)/columns)-1)*.5)*.65)
		index += 1
	sync_actors()
	if bench_mode in ["sim","static"]:
		for actor in actor_registry.actors.values():
			var animation: AnimationPlayer = actor.get_meta("player")
			animation.active = false
		var hero_animation: AnimationPlayer = hero.get_meta("player")
		hero_animation.active = false
	if bench_mode == "sim":
		world.hide()
		hero.hide()
		for actor in actor_registry.actors.values(): actor.hide()
		for child in get_children():
			if child is CanvasLayer: child.hide()
	elif bench_mode == "static":
		# Bake only one template at setup, never during measured frames.
		# The API stalls GPU readback and does not copy materials.
		# https://docs.godotengine.org/en/4.5/classes/class_meshinstance3d.html
		await RenderingServer.frame_post_draw
		if not actor_registry.actors.is_empty():
			var first: Node3D = actor_registry.actors.values()[0]
			collect_static(first,first)
		for identity in actor_registry.actors:
			var actor: Node3D = actor_registry.actors[identity]
			var replacement := Node3D.new()
			add_child(replacement)
			replacement.transform = actor.transform
			for part in static_template:
				var instance := MeshInstance3D.new()
				instance.mesh = part.mesh
				instance.transform = part.transform
				replacement.add_child(instance)
			static_actors[identity] = replacement
			actor.hide()
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(),true)
	var metadata_path := "res://game_data/build_info.json"
	if FileAccess.file_exists(metadata_path):
		var metadata: Variant = JSON.parse_string(FileAccess.get_file_as_string(metadata_path))
		if metadata is Dictionary and metadata.get("source_hashes") is Dictionary:
			source_hashes = metadata.source_hashes.duplicate()
			embedded_manifest_hash = FileAccess.get_sha256(metadata_path)
	var paths: Array = source_hashes.keys()
	if paths.is_empty(): paths = ["baseline_sim.gd","baseline_view.gd","presentation/actor_registry.gd","presentation/effect_presenter.gd","presentation/hud_presenter.gd","presentation/qa_output.gd","presentation/static_batch.gd","presentation/skinned_mesh_batch.gd","benchmark/crowd_benchmark.gd","benchmark/crowd_benchmark.tscn","benchmark/flight_qa.gd","benchmark/flight_qa.tscn","game_data/catalog.json","data/game_catalog.gd","project.godot","Baseline.tscn","export_presets.cfg"]
	for path in ["combat/stat_block.gd","combat/combat_resolver.gd","presentation/input_controller.gd","presentation/skill_effect_presenter.gd"]:
		if not paths.has(path): paths.append(path)
	for path in paths:
		var live_hash: String = FileAccess.get_sha256("res://"+path)
		if not live_hash.is_empty(): source_hashes[path] = live_hash
		else: source_hashes_basis = "embedded pre-export source manifest; exported scripts/config are remapped, not runtime source bytes"
	raw_file = FileAccess.open(output_dir+"/frames.csv",FileAccess.WRITE)
	tick_file = FileAccess.open(output_dir+"/physics.csv",FileAccess.WRITE)
	if not raw_file or not tick_file:
		get_tree().quit(1)
		return
	if workload == "multi_skill":
		skill_event_file = FileAccess.open(output_dir+"/skill-events.jsonl",FileAccess.WRITE)
		if not skill_event_file:
			get_tree().quit(1)
			return
	raw_file.store_csv_line(PackedStringArray(headers()))
	tick_file.store_csv_line(PackedStringArray(["elapsed_seconds","tick","sim_tick_ms","sync_tick_ms","ai_ms","grid_ms","query_ms","narrowphase_ms","bolts_ms"]))
	start_usec = Time.get_ticks_usec()
	if not actor_registry.actors.is_empty(): probe_skeleton = skinned_mesh_batch.find_skeleton(actor_registry.actors.values()[0])
	previous_usec = start_usec
	print("CROWD_BENCH_READY ",bench_mode," ",initial_enemies)

func collect_static(node: Node, actor: Node3D) -> void:
	if node is MeshInstance3D:
		var baked: ArrayMesh = node.bake_mesh_from_current_skeleton_pose()
		for surface in range(baked.get_surface_count()): baked.surface_set_material(surface,node.get_active_material(surface))
		static_template.append({"mesh":baked,"transform":actor.global_transform.affine_inverse()*node.global_transform})
	for child in node.get_children(): collect_static(child,actor)

func _physics_process(_delta: float) -> void:
	if finished or start_usec == 0: return
	var begin: int = Time.get_ticks_usec()
	var seconds: float = float(sim.tick)/60.0
	sim.set_destination(Vector2(cos(seconds*.3)*5.0,sin(seconds*.3)*3.0))
	sim.mana_raw = sim.mana_max_raw
	if bench_mode == "fx" and workload == "projectile_stress":
		while sim.bolts.size() < fixture_bolts:
			var index: int = sim.bolts.size()
			var angle: float = float(index)*2.39996322972865+seconds*.1
			sim.bolts.append({"p":Vector2(cos(angle),sin(angle))*12.0,"direction":-Vector2(cos(angle),sin(angle)),"age":0,"life":132,"id":sim.shots+index+1000+sim.tick*10000})
	var aim_point := Vector2.ZERO
	if workload in ["skill","multi_skill"] and bench_mode == "fx":
		var target: Dictionary = sim.nearest_enemy(sim.player)
		if not target.is_empty(): aim_point = target.p
	var requested_skill: String = bench_skill_ids[bench_skill_index] if workload == "multi_skill" else ""
	if workload == "multi_skill" and sim.pending.is_empty() and sim.tick+1 >= sim.next_cast_tick: sim.select_skill(requested_skill)
	sim.step(workload in ["skill","multi_skill"] and bench_mode == "fx",aim_point,requested_skill)
	var sim_ms: float = float(Time.get_ticks_usec()-begin)/1000.0
	begin = Time.get_ticks_usec()
	if bench_mode == "fx":
		hero_hurt_ticks = maxi(0,hero_hurt_ticks-1)
		for event in sim.events:
			handle_event(event)
			if workload == "multi_skill" and event.kind == "cast_start": bench_skill_index = (bench_skill_index+1)%bench_skill_ids.size()
			if sample_start_usec > 0:
				event_counts[event.kind] = int(event_counts.get(event.kind,0))+1
				if event.kind == "cast_start": cast_proxy_count += 1
				if workload == "multi_skill":
					var skill_id: String = String(event.get("skill_id",sim.default_skill_id))
					if event.kind in ["cast_start","release","hit","skill_effect","status_applied"]:
						var counters: Dictionary = skill_event_counts.get(skill_id,{})
						counters[event.kind] = int(counters.get(event.kind,0))+1
						skill_event_counts[skill_id] = counters
					skill_event_file.store_line(JSON.stringify({"elapsed_seconds":float(Time.get_ticks_usec()-start_usec)/1000000.0,"event":event}))
	var sync_ms: float = float(Time.get_ticks_usec()-begin)/1000.0
	frame_sim_ms += sim_ms
	frame_sync_ms += sync_ms
	frame_physics_ticks += 1
	total_physics_ticks += 1
	if sample_start_usec > 0:
		var row: Array = [float(Time.get_ticks_usec()-start_usec)/1000000.0,sim.tick,sim_ms,sync_ms,float(sim.profile_us.ai)/1000.0,float(sim.profile_us.grid)/1000.0,float(sim.profile_us.query)/1000.0,float(sim.profile_us.narrowphase)/1000.0,float(sim.profile_us.bolts)/1000.0]
		store_csv(tick_file,row)
		# Retain only numeric timing columns for summary, not entity snapshots.
		tick_rows.append(row)

func _process(delta: float) -> void:
	if finished or start_usec == 0: return
	var now: int = Time.get_ticks_usec()
	var elapsed: float = float(now-start_usec)/1000000.0
	var frame_ms: float = float(now-previous_usec)/1000.0
	previous_usec = now
	var begin: int = Time.get_ticks_usec()
	age += delta
	fx_time += delta
	cast_glow.light_energy = maxf(0,cast_glow.light_energy-delta*2.5)
	if status_until > 0 and age > status_until: status_label.text = ""
	if bench_mode != "sim":
		sync_actors()
		if bench_mode == "static":
			for identity in static_actors: static_actors[identity].transform = actor_registry.actors[identity].transform
		for event in visual_event_queue: burst(Vector3(event.p[0],.8,event.p[1]),Color("ffbe68"),8,.3)
		visual_event_queue.clear()
	frame_sync_ms += float(Time.get_ticks_usec()-begin)/1000.0
	begin = Time.get_ticks_usec()
	if bench_mode in ["rig","fx"]: actor_registry.advance(delta,camera,sim.player)
	var animation_ms: float = float(Time.get_ticks_usec()-begin)/1000.0
	begin = Time.get_ticks_usec()
	if bench_mode == "fx": effect_presenter.advance(delta)
	var fx_ms: float = float(Time.get_ticks_usec()-begin)/1000.0
	if not capture_busy and not bench_capture_ok and elapsed >= minf(2.0,warmup_seconds*.5):
		capture_busy = true
		capture_benchmark()
	if sample_start_usec == 0 and elapsed >= warmup_seconds:
		sample_start_usec = now
		sample_start_tick = sim.tick
		probe_window_start = elapsed
		previous_probe_pose = read_probe_pose()
	elif sample_start_usec > 0:
		if bench_mode in ["rig","fx"]:
			probe_clock_count += actor_registry.animation_clock_progress
			if elapsed-probe_window_start >= 1.0:
				var current_pose: Array = read_probe_pose()
				animation_probe_windows.append({"window_start_elapsed":probe_window_start,"window_end_elapsed":elapsed,"advanced_clock_count":probe_clock_count,"bone_pose_changed":current_pose != previous_probe_pose})
				probe_window_start = elapsed
				probe_clock_count = 0
				previous_probe_pose = current_pose
		var visible := 0
		if bench_mode != "sim":
			var render_nodes: Array = static_actors.values() if bench_mode == "static" else actor_registry.actors.values()
			for actor in render_nodes:
				if actor.visible and camera.is_position_in_frustum(actor.global_position+Vector3.UP): visible += 1
		var viewport_rid: RID = get_viewport().get_viewport_rid()
		var skinned: int = actor_registry.actors.size() if bench_mode in ["rig","fx"] else 0
		var row: Array = [elapsed,frame_ms,sim.tick,sim.enemies.size(),sim.alive_count(),0 if bench_mode == "sim" else actor_registry.actors.size(),visible,skinned,sim.bolts.size(),effect_presenter.particles.size(),frame_sim_ms,frame_sync_ms,fx_ms,RenderingServer.viewport_get_measured_render_time_cpu(viewport_rid),RenderingServer.viewport_get_measured_render_time_gpu(viewport_rid),RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_DRAW_CALLS_IN_FRAME),RenderingServer.get_rendering_info(RenderingServer.RENDERING_INFO_TOTAL_PRIMITIVES_IN_FRAME),Performance.get_monitor(Performance.MEMORY_STATIC),Performance.get_monitor(Performance.OBJECT_NODE_COUNT),sim.history_count(),frame_physics_ticks,animation_ms,actor_registry.pose_updates if bench_mode in ["rig","fx"] else 0,actor_registry.pool.size(),effect_presenter.projectile_pool.size(),effect_presenter.particle_pool.size(),actor_registry.animation_clock_progress if bench_mode in ["rig","fx"] else 0,actor_registry.animation_playing if bench_mode in ["rig","fx"] else 0]
		row.append_array([effect_presenter.skill_effects.active.size(),effect_presenter.skill_effects.statuses.size(),effect_presenter.skill_effects.created,sim.statuses.size()])
		rows.append(row)
		store_csv(raw_file,row)
		if float(now-sample_start_usec)/1000000.0 >= sample_seconds:
			sample_end_usec = now
			finished = true
			write_benchmark(elapsed)
	frame_sim_ms = 0.0
	frame_sync_ms = 0.0
	frame_physics_ticks = 0

func capture_benchmark() -> void:
	var result: Dictionary = await QAOutput.capture(get_viewport(),output_dir+"/frame.png")
	bench_image_size = result.size
	bench_capture_ok = result.saved
	capture_elapsed = float(Time.get_ticks_usec()-start_usec)/1000000.0
	capture_busy = false

func sync_actors() -> void:
	super.sync_actors()
	if workload != "multi_skill": return
	# This harness supplies synthetic inputs directly. Label that policy instead
	# of presenting the normal manual-input toggle as the measured workload.
	if auto_button:
		auto_button.text = "성능 측정 · 3스킬 순환"
		auto_button.disabled = true
	if equipment_button: equipment_button.disabled = true
	for skill_button in skill_buttons: skill_button.disabled = true
	if skill_mode_label:
		var casting: String = sim.casting_skill_id()
		var detail: String = "다음 요청 대기" if casting.is_empty() else "시전 중: "+str(sim.skill_definition(casting).get("display_name",casting))
		skill_mode_label.text = "고HP/마나 보정 · 합성 부하\n"+detail
	if hint: hint.text = "성능 측정 · 3스킬 순환 · 고HP/마나 보정"
	if stats_text: stats_text.text = "성능 측정 · 3스킬 순환\n적 최대 체력 1,000,000,000 raw\n플레이어 최대 체력 1,000,000,000 raw\n마나 매틱 보충 · 유한 고HP 합성 부하\n일반 플레이·재미·최종 아트 판정 아님"
	if bench_equipment:
		if skill_mode_label: skill_mode_label.text += "\n장비 3개 · 합성 소유자 레벨 2"
		if stats_text: stats_text.text += "\n장비 3개 활성 · 장비 스탯/화염탄 보너스 포함"

func read_probe_pose() -> Array:
	var pose: Array = []
	if probe_skeleton:
		for index in range(probe_skeleton.get_bone_count()): pose.append(probe_skeleton.get_bone_pose(index))
	return pose

func headers() -> Array:
	return ["elapsed_seconds","frame_ms","tick","sim_active","sim_alive","render_actors","actor_centers_in_frustum","skinned_rigs","bolts","fx_particles","sim_frame_ms","presentation_sync_frame_ms","fx_advance_ms","render_cpu_ms","render_gpu_ms","draw_calls","primitives","debug_static_bytes","nodes","history","physics_ticks_in_frame","animation_frame_ms","pose_updates","actor_pool","projectile_pool","particle_pool","animation_clock_progress","animation_playing","skill_fx_active","skill_fx_status","skill_fx_created","sim_statuses"]

func store_csv(file: FileAccess, row: Array) -> void:
	var strings := PackedStringArray()
	for value in row: strings.append(str(value))
	file.store_csv_line(strings)

func summary(values: Array) -> Dictionary:
	if values.is_empty(): return {}
	var ordered: Array = values.duplicate()
	ordered.sort()
	var n: int = ordered.size()
	return {"min":ordered[0],"max":ordered[-1],"p50":ordered[mini(n-1,ceili(n*.5)-1)],"p95":ordered[mini(n-1,ceili(n*.95)-1)],"p99":ordered[mini(n-1,ceili(n*.99)-1)]}

func write_benchmark(elapsed: float) -> void:
	raw_file.flush()
	tick_file.flush()
	var raw_ok: bool = raw_file.get_error() == OK and tick_file.get_error() == OK
	if skill_event_file:
		skill_event_file.flush()
		raw_ok = raw_ok and skill_event_file.get_error() == OK
	var config: Dictionary = {"camera_transform":str(camera.transform),"camera_projection":camera.projection,"camera_size":camera.size,"world":"baseline fixed seed415, unchanged lighting and shadows","enemy_model":"Skeleton_Minion.glb","hero_model":"Mage.glb","animation_lod":actor_registry.animation_lod_enabled,"near_hz":60,"far_hz":15,"offscreen_hz":2,"merged":not OS.get_cmdline_user_args().has("--unmerged-actors"),"floor_batched":not OS.get_cmdline_user_args().has("--unbatched-floor"),"fixture_policy":"grid.65m; moving target cos/sin; highHP1e9; no RNG reseeding","fx_particles_cap":effect_presenter.MAX_PARTICLES,"projectile_visual_cap":effect_presenter.MAX_PROJECTILES}
	var data: Dictionary = {"scope":"synthetic fixed-count boosted-HP stress; not normal gameplay or SACRATA quality","mode":bench_mode,"phase":bench_phase,"requested":initial_enemies,"fixture_bolts":fixture_bolts if bench_mode == "fx" else 0,"engine":Engine.get_version_info(),"rendering_method":RenderingServer.get_current_rendering_method(),"rendering_driver":RenderingServer.get_current_rendering_driver_name(),"adapter":RenderingServer.get_video_adapter_name(),"adapter_vendor":RenderingServer.get_video_adapter_vendor(),"display_server":DisplayServer.get_name(),"os":OS.get_name(),"processor":OS.get_processor_name(),"warmup_seconds":warmup_seconds,"requested_sample_seconds":sample_seconds,"wall_elapsed_seconds":elapsed,"sample_count":rows.size(),"sample_start_elapsed":float(sample_start_usec-start_usec)/1000000.0,"sample_first_elapsed":rows[0][0] if not rows.is_empty() else 0,"sample_last_elapsed":rows[-1][0] if not rows.is_empty() else 0,"measured_sample_seconds":float(Time.get_ticks_usec()-sample_start_usec)/1000000.0,"sample_start_tick":sample_start_tick,"sample_end_tick":sim.tick,"total_physics_ticks":total_physics_ticks,"physics_sample_count":tick_rows.size(),"time_scale":Engine.time_scale,"max_physics_steps_per_frame":Engine.max_physics_steps_per_frame,"framebuffer_width":bench_image_size.x,"framebuffer_height":bench_image_size.y,"capture_saved":bench_capture_ok,"capture_elapsed":capture_elapsed,"vsync_mode":DisplayServer.window_get_vsync_mode(),"max_fps":Engine.max_fps,"catalog_sha256":FileAccess.get_sha256("res://game_data/catalog.json"),"source_hashes":source_hashes,"configuration":config,"configuration_digest":JSON.stringify(config).sha256_text(),"floor_stats":floor_stats,"memory_note":"Release MEMORY_STATIC zero is unavailable. Benchmark rows/timing vectors are retained intentionally until report, so process-memory growth includes measurement buffers; game pools/history have explicit caps.","monitor_note":"Render times exclude scripts and may overlap CPU/GPU. Frustum center count is not occlusion visibility. CPU frame sums include ALL physics callbacks since previous render; physics.csv gives each individual tick."}
	for index in range(1,headers().size()):
		data[headers()[index]] = summary(rows.map(func(row): return row[index]))
	var tick_headers := ["elapsed_seconds","tick","sim_tick_ms","sync_tick_ms","ai_ms","grid_ms","query_ms","narrowphase_ms","bolts_ms"]
	for index in range(2,tick_headers.size()): data[tick_headers[index]] = summary(tick_rows.map(func(row): return row[index]))
	data["stutter_gt50"] = rows.filter(func(row): return row[1] > 50.0).size()
	data["pool_counters"] = {"actors_created":actor_registry.created_count,"actors_reused":actor_registry.reused_count,"actors_released":actor_registry.released_count,"projectiles_created":effect_presenter.projectile_created,"projectiles_reused":effect_presenter.projectile_reused,"particles_created":effect_presenter.particle_created,"particles_reused":effect_presenter.particle_reused,"particle_requests_dropped":effect_presenter.dropped_particles,"projectile_visual_requests_dropped":effect_presenter.dropped_projectiles,"history_dropped":sim.history_dropped}
	data["workload"] = workload
	data["sample_event_counts"] = event_counts
	data["sample_skill_event_counts"] = skill_event_counts
	data["skill_round_robin_ids"] = bench_skill_ids
	data["skill_fx_pool"] = {"created":effect_presenter.skill_effects.created,"reused":effect_presenter.skill_effects.reused,"dropped":effect_presenter.skill_effects.dropped,"cap":effect_presenter.skill_effects.MAX_NODES}
	data["combat_errors"] = sim.combat_errors.duplicate()
	data["equipment_fixture"] = {"enabled":bench_equipment,"context":sim.equipment_context(),"inventory":sim.equipment_snapshot(),"stats":sim.player_stats_snapshot(),"skills":[]}
	if bench_equipment:
		for id_ in sim.available_skill_ids(): data.equipment_fixture.skills.append(sim.skill_display(id_))
	data["cast_proxy_count"] = cast_proxy_count
	data["skill_budget"] = {"scope":"Default FireBolt budget; multi-skill definitions are separately listed in round-robin ids and source catalog","cycle_ticks":sim.cycle_ticks,"projectile_life_ticks":roundi(float(sim.params.projectile_life_seconds)*60.0),"theoretical_max_simultaneous_bolts":ceili(float(sim.params.projectile_life_seconds)*60.0/float(sim.cycle_ticks)),"startup_ticks":sim.startup_ticks,"mana_cost_raw":sim.mana_cost_raw,"refill_note":"Synthetic finite boosted-HP fixture restores mana every tick so sustained casting does not stop; normal game retains baseline mana rules."}
	data["source_hashes_basis"] = source_hashes_basis
	data["embedded_source_manifest_sha256"] = embedded_manifest_hash
	if workload in ["skill","multi_skill"]: data["fixture_bolts"] = 0
	var valid: bool = raw_ok and bench_capture_ok and bench_image_size == Vector2i(1920,1080) and not rows.is_empty() and data.sim_active.min == initial_enemies and data.sim_alive.min == initial_enemies and DisplayServer.get_name() != "headless"
	var target_eligible: bool = valid and warmup_seconds >= 10 and sample_seconds >= 60 and bench_mode in ["rig","fx"] and capture_elapsed < data.sample_start_elapsed
	var progress_seconds: float = float(sim.tick-sample_start_tick)/60.0
	var measured_seconds: float = float(sample_end_usec-sample_start_usec)/1000000.0
	data["measured_sample_seconds"] = measured_seconds
	var actual_motion: bool = bench_mode not in ["rig","fx"] or (data.pose_updates.max > 0 and data.animation_clock_progress.max > 0)
	for window in animation_probe_windows:
		actual_motion = actual_motion and int(window.advanced_clock_count) > 0 and bool(window.bone_pose_changed)
	data["animation_probe_windows"] = animation_probe_windows
	data["counter_definitions"] = {"skinned_rigs":"retained actor rigs with Skin/Skeleton associated, not direct GPU skinning work","actor_centers_in_frustum":"camera center-point estimate, not occlusion visibility","pose_updates":"manual AnimationPlayer.advance calls","animation_clock_progress":"advance calls whose animation clock actually changed","animation_playing":"players currently playing; non-loop clips can legitimately finish before AI state ends"}
	data.configuration["near_animation_budget"] = actor_registry.NEAR_ANIMATION_BUDGET
	data.configuration["workload"] = workload
	data.configuration["fixture_bolts"] = fixture_bolts if workload == "projectile_stress" else 0
	data.configuration["skill_cycle_ticks"] = sim.cycle_ticks
	data.configuration["player_and_enemy_hp"] = 1000000000
	data.configuration["mana_refilled_every_tick"] = true
	data.configuration["equipment_fixture"] = data.equipment_fixture.duplicate(true)
	data["configuration_digest"] = JSON.stringify(data.configuration).sha256_text()
	var actual_rigs: bool = bench_mode not in ["rig","fx"] or (data.render_actors.min == initial_enemies and data.skinned_rigs.min == initial_enemies)
	var actual_skill: bool = true
	if workload == "skill" and bench_mode == "fx":
		var expected_casts: float = sample_seconds*60.0/float(sim.cycle_ticks)
		actual_skill = absf(float(event_counts.get("cast_start",0))-expected_casts) <= 2.0 and int(event_counts.get("release",0)) > 0 and int(event_counts.get("hit",0)) > 0 and data.fx_particles.max > 0 and cast_proxy_count == int(event_counts.get("cast_start",0))
	if workload == "multi_skill":
		actual_skill = bench_skill_ids.size() == 3 and sim.combat_errors.is_empty() and data.fx_particles.max > 0 and data.skill_fx_active.max > 0 and data.skill_fx_status.max > 0 and data.sim_statuses.max > 0 and cast_proxy_count == int(event_counts.get("cast_start",0))
		for id_ in bench_skill_ids:
			var counters: Dictionary = skill_event_counts.get(id_,{})
			var definition: Dictionary = sim.skill_definition(id_)
			actual_skill = actual_skill and int(counters.get("cast_start",0)) > 0 and int(counters.get("release",0)) > 0 and int(counters.get("hit",0)) > 0
			if definition.get("kind","projectile") != "projectile": actual_skill = actual_skill and int(counters.get("skill_effect",0)) > 0
			if definition.get("effect",{}).has("status"): actual_skill = actual_skill and int(counters.get("status_applied",0)) > 0
		data.configuration["skill_policy"] = "round robin advances only on accepted cast; all three skill definitions and common resolver, real chill/area/chain FX; per-event disk logging included"
		data.configuration["player_hp_raw"] = 1000000000
		data.configuration["player_hp_policy"] = "public modifier benchmark.fixture/high_hp sets maximum and stat snapshot to 1e9 raw; current HP initialized to that maximum"
		data.configuration["enemy_hp_policy"] = "synthetic direct runtime current/max_raw override to 1e9, defense stats unchanged; enemy health modifiers are not supported"
		data["configuration_digest"] = JSON.stringify(data.configuration).sha256_text()
	if bench_equipment:
		actual_skill = actual_skill and sim.equipment_snapshot().equipped.size() == 3 and sim.equipment_context().level == 2 and sim.player_stats.value("stat.skill.ember_level") == 1 and sim.skill_display("skill.ember_bolt").effective_level == 2
	var physics_progress: bool = absf(progress_seconds-measured_seconds) <= .1 and Engine.time_scale == 1.0 and Engine.physics_ticks_per_second == 60
	valid = valid and actual_motion and actual_rigs and actual_skill and physics_progress and measured_seconds >= sample_seconds
	target_eligible = target_eligible and valid
	data["validity_checks"] = {"file_writes":raw_ok,"all_requested_alive":data.sim_active.min == initial_enemies and data.sim_alive.min == initial_enemies,"actual_rigs":actual_rigs,"actual_pose_updates":actual_motion,"physics_progress":physics_progress,"physics_seconds":progress_seconds,"measured_seconds":measured_seconds,"actual_framebuffer":bench_image_size == Vector2i(1920,1080)}
	data.validity_checks["actual_skill_and_fx"] = actual_skill
	var target_pass: bool = target_eligible and data.frame_ms.p95 <= 16.67
	data["valid_run"] = valid
	data["target_eligible"] = target_eligible
	data["target_pass"] = target_pass
	data["target_threshold_ms"] = 16.67
	var report := FileAccess.open(output_dir+"/summary.json",FileAccess.WRITE)
	if not report:
		get_tree().quit(1)
		return
	report.store_string(JSON.stringify(data,"  "))
	report.flush()
	print("CROWD_BENCH_RESULT ",JSON.stringify(data))
	get_tree().quit(0 if valid and report.get_error() == OK and (not require_target or target_pass) else 1)

