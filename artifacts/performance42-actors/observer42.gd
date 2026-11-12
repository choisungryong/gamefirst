extends SceneTree
const Probe41=preload("C:/Project/d2r-combat-baseline/artifacts/performance42-actors/frame_probe_render42.gd")
var view: Node3D
var probe: RefCounted
var folder := ""
var ending := false
var component_rows: Array[PackedInt64Array]=[]
var previous42: PackedInt64Array=PackedInt64Array()
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	view=load("res://diagnostic42/view.gd").new();root.add_child(view)
	DisplayServer.window_set_title("진단42 구성요소 · 서리 · MENU 대기")
	view._capture_dir=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--performance42-dir="):folder=arg.trim_prefix("--performance42-dir=")
	if folder.is_empty() or DirAccess.dir_exists_absolute(folder):_reject("Fresh performance directory required");return
	if DirAccess.make_dir_recursive_absolute(folder)!=OK:_reject("Cannot create performance folder");return
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var texture := root.get_texture()
	var image_ := texture.get_image()
	var actual := image_.get_size()
	if actual!=Vector2i(1920,1080) or root.size!=Vector2i(1920,1080):_reject("Actual render/window preflight mismatch");return
	if image_.save_png(folder.path_join("preflight.png"))!=OK:_reject("Preflight PNG write failed");return
	var invariant := {"window":str(root.size),"visible":str(root.get_visible_rect().size),"content_scale":root.content_scale_factor,"scale3d":root.scaling_3d_scale,"scale3d_mode":root.scaling_3d_mode,"msaa":root.msaa_3d}
	probe=Probe41.new()
	var context := {"profile_disabled":view._profile_off,"captures_enabled":false,"input_log_enabled":false,"wall_quit_enabled":false,"qa_ignore_focus":view._qa_ignore_focus,"pilot":view._pilot,"render_invariant":invariant,"reported_texture_size":[int(texture.get_width()),int(texture.get_height())],"actual_readback_before":[actual.x,actual.y],"size_contract":"Before/after live image readback1920x1080 + every-frame invariant window/visible/scale3d/MSAA + raw reported texture dimensions kept separately. No image readback or capture during warmup/sample."}
	if not probe.configure(folder.path_join("probe"),view,context):_reject("Performance probe rejected");return
	image_=null;texture=null
	print("PERFORMANCE42_READY ",JSON.stringify({"waiting_for_native_start":true,"folder":folder,"actual":actual,"reported":context.reported_texture_size}))
func _process(_delta: float) -> bool:
	if probe==null or ending:return false
	var vals42:=PackedInt64Array([Time.get_ticks_usec(),Engine.get_process_frames(),Engine.get_physics_frames(),view.run.tick,view.run.enemies.size(),view.actors.actors.size(),int(Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME)),int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)),int(Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)),int(Performance.get_monitor(Performance.MEMORY_STATIC)),int(Performance.get_monitor(Performance.TIME_PROCESS)*1000000),int(Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS)*1000000)])
	for object42 in [view.run,view.world,view.actors,view.effects,view.hud]:
		vals42.append(object42.diag42_us);vals42.append(object42.diag42_calls)
	var count_start42:=Time.get_ticks_usec()
	var offscreen42: int=0
	for enemy42 in view.run.enemies.values():
		var pos42: Vector2=enemy42.position
		if not view.world.camera.is_position_in_frustum(Vector3(pos42.x,0.5,pos42.y)):offscreen42+=1
	vals42.append_array(PackedInt64Array([offscreen42,Time.get_ticks_usec()-count_start42]))
	vals42.append_array(PackedInt64Array([view.diag42_process_us,view.diag42_process_calls,view.diag42_physics_us,view.diag42_physics_calls,view.diag42_consume_us,view.diag42_consume_calls]))
	if view.run.mode in ["playing","choice"]:component_rows.append(vals42)
	probe.observe(view,view.run)
	if probe.done:
		ending=true;view.set_process(false);view.set_physics_process(false);call_deferred("_finish")
	return false
func _finish() -> void:
	var component_file42:=FileAccess.open(folder.path_join("components.csv"),FileAccess.WRITE)
	component_file42.store_line("wall_us,process_frame,physics_frame,tick,retained_enemies,actor_nodes,render_objects,draw_calls,primitives,static_memory,time_process_us,time_physics_us,core_us,core_calls,world_us,world_calls,actors_us,actors_calls,fx_us,fx_calls,hud_us,hud_calls,offscreen_enemy_points,count_observer_us,view_process_us,view_process_calls,view_physics_us,view_physics_calls,consume_us,consume_calls")
	for row42 in component_rows:
		var cells42:=PackedStringArray()
		for value42 in row42:cells42.append(str(value42))
		component_file42.store_csv_line(cells42)
	component_file42.close()
	await RenderingServer.frame_post_draw
	var texture := root.get_texture()
	var image_ := texture.get_image()
	var actual := image_.get_size()
	if image_.save_png(folder.path_join("postflight.png"))!=OK:_reject("Postflight PNG write failed");return
	var report := {"actual_after":[actual.x,actual.y],"window_after":root.size,"reported_after":texture.get_size(),"hud_script":view.hud.get_script().resource_path,"core_script":view.run.get_script().resource_path,"world_script":view.world.get_script().resource_path,"actor_script":view.actors.get_script().resource_path,"fx_script":view.effects.get_script().resource_path,"visible_ground_names":view.effects.layout26_records.size(),"pool_created":view.actors.pool25_created,"pool_hits":view.actors.pool25_hits,"pool_size":view.actors._pool25_size(),"static_memory_bytes":OS.get_static_memory_usage(),"shared_skins":view.actors._shared_skin24.size(),"skin_builds":view.actors.skin24_builds,"skin_hits":view.actors.skin24_hits,"transient_aliases":view.actors._batch19_cache.size(),"tick":view.run.tick,"mode":view.run.mode,"summary":probe.summary,"scope":"Actual41 EXE normal pilot, native menu start. Only before/after PNG/readback, no captures inside the10s+60s measurement."}
	var file := FileAccess.open(folder.path_join("postflight.json"),FileAccess.WRITE)
	if file==null:_reject("Postflight JSON open failed");return
	file.store_string(JSON.stringify(report,"\t"));file.flush()
	var written: bool=file.get_error()==OK
	file.close();file=null
	if not written:_reject("Postflight JSON write failed");return
	texture=null;image_=null
	var code: int=0 if actual==Vector2i(1920,1080) and not probe.io_failed else 1
	await _cleanup(code)

func _reject(message: String) -> void:
	push_error(message)
	ending=true
	call_deferred("_cleanup",1)
func _cleanup(code: int) -> void:
	ending=true
	if view!=null:
		view.set_process(false);view.set_physics_process(false)
	if probe!=null:
		probe.finish("observer_cleanup")
		probe._restore_smoothing()
		if probe.io_failed:code=1
	if view!=null:
		view.audio.reset();view.queue_free()
	for index in 4:await process_frame
	view=null;probe=null
	quit(code)

