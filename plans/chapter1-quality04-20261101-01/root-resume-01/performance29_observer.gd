extends SceneTree
const Probe23=preload("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/root-resume-01/frame_probe_render23.gd")
var view: Node3D
var probe: RefCounted
var folder := ""
var ending := false
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view._capture_dir=""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--performance29-dir="):folder=arg.trim_prefix("--performance29-dir=")
	if folder.is_empty() or DirAccess.dir_exists_absolute(folder):push_error("Fresh performance directory required");quit(1);return
	DirAccess.make_dir_recursive_absolute(folder)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var texture := root.get_texture()
	var image_ := texture.get_image()
	var actual := image_.get_size()
	if actual!=Vector2i(1920,1080) or root.size!=Vector2i(1920,1080):push_error("Actual render/window preflight mismatch");quit(1);return
	image_.save_png(folder.path_join("preflight.png"))
	var invariant := {"window":str(root.size),"visible":str(root.get_visible_rect().size),"content_scale":root.content_scale_factor,"scale3d":root.scaling_3d_scale,"scale3d_mode":root.scaling_3d_mode,"msaa":root.msaa_3d}
	probe=Probe23.new()
	var context := {"captures_enabled":false,"input_log_enabled":false,"wall_quit_enabled":false,"qa_ignore_focus":view._qa_ignore_focus,"pilot":view._pilot,"render_invariant":invariant,"reported_texture_size":[int(texture.get_width()),int(texture.get_height())],"actual_readback_before":[actual.x,actual.y],"size_contract":"Before/after live image readback1920x1080 + every-frame invariant window/visible/scale3d/MSAA + raw reported texture dimensions kept separately. No image readback or capture during warmup/sample."}
	if not probe.configure(folder.path_join("probe"),view,context):push_error("Performance probe rejected");quit(1);return
	print("PERFORMANCE29_READY ",JSON.stringify({"waiting_for_native_start":true,"folder":folder,"actual":actual,"reported":texture.get_size()}))
func _process(_delta: float) -> bool:
	if probe==null or ending:return false
	probe.observe(view,view.run)
	if probe.done:
		ending=true;view.set_physics_process(false);call_deferred("_finish")
	return false
func _finish() -> void:
	await RenderingServer.frame_post_draw
	var texture := root.get_texture()
	var image_ := texture.get_image()
	var actual := image_.get_size()
	image_.save_png(folder.path_join("postflight.png"))
	var report := {"actual_after":[actual.x,actual.y],"window_after":root.size,"reported_after":texture.get_size(),"actor_script":view.actors.get_script().resource_path,"fx_script":view.effects.get_script().resource_path,"visible_ground_names":view.effects.layout26_records.size(),"pool_created":view.actors.pool25_created,"pool_hits":view.actors.pool25_hits,"pool_size":view.actors._pool25_size(),"static_memory_bytes":OS.get_static_memory_usage(),"shared_skins":view.actors._shared_skin24.size(),"skin_builds":view.actors.skin24_builds,"skin_hits":view.actors.skin24_hits,"transient_aliases":view.actors._batch19_cache.size(),"tick":view.run.tick,"mode":view.run.mode,"summary":probe.summary,"scope":"Actual29 EXE normal pilot, native menu start. Only before/after PNG/readback, no captures inside the10s+60s measurement."}
	var file := FileAccess.open(folder.path_join("postflight.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	view.audio.reset()
	await create_timer(.15).timeout
	quit(0 if actual==Vector2i(1920,1080) else 1)
