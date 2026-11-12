extends RefCounted
## Optional QA observer. No gameplay writes and no file I/O inside the sample window.
## Time is monotonic, unlike the adjustable system clock:
## https://docs.godotengine.org/en/4.5/classes/class_time.html#class-time-method-get-ticks-usec
## Focus/render/movie APIs: Window.has_focus, Texture2D.get_size,
## RenderingServer.get_current_rendering_method and Engine.get_write_movie_path.
const MAX_ROWS := 180000
const STRIDE := 18
const WARMUP_US := 10000000
const SAMPLE_US := 60000000
const MODES := {"menu":0,"playing":1,"choice":2,"inventory":3,"paused":4,"victory":5,"defeat":6}
const HEADER := "sequence,elapsed_us,interval_us,phase,focused,mode_code,sim_tick,retained_enemies,projectiles,orbs,ground_items,window_width,window_height,texture_reported_width,texture_reported_height,process_frame,physics_frame,frames_drawn\n"
var enabled := false
var done := false
var rows := PackedInt64Array()
var row_count := 0
var output_dir := ""
var metadata: Dictionary = {}
var summary: Dictionary = {}
var _started_us := -1
var _previous_us := -1
var _previous_elapsed := -1
var _overflow := false
var _previous_delta_smoothing := true
var _changed_delta_smoothing := false
var invariant_errors: Array[Dictionary]=[]
var scenario_errors: Array[Dictionary]=[]
var io_failed := false

func configure(path: String, view: Node3D, context: Dictionary) -> bool:
	if enabled or done:return false
	var normalized := path.replace("\\","/").simplify_path()
	var source_base := ProjectSettings.globalize_path("res://plans/chapter1-quality04-20261101-01/").replace("\\","/")
	var export_base := OS.get_executable_path().get_base_dir().replace("\\","/")+"/qa-probe/"
	if not normalized.is_absolute_path() or (not normalized.begins_with(source_base) and not normalized.begins_with(export_base)):
		push_error("Frame probe requires a new quality04 evidence or executable qa-probe subdirectory")
		return false
	if DirAccess.dir_exists_absolute(normalized) or FileAccess.file_exists(normalized):
		push_error("Frame probe refuses an existing output directory: "+normalized)
		return false
	var engine_args := Array(OS.get_cmdline_args())
	if DirAccess.make_dir_recursive_absolute(normalized)!=OK:
		push_error("Frame probe could not create its new output directory")
		return false
	output_dir=normalized
	metadata=context.duplicate(true)
	# Exported release builds can consume engine CLI flags before this API runs.
	# Read the actual property instead of demanding that a CLI token survives.
	# https://docs.godotengine.org/en/4.5/classes/class_os.html#class-os-property-delta-smoothing
	_previous_delta_smoothing=OS.delta_smoothing
	# The observed release export did not apply the supplied CLI smoothing flag.
	# Apply this process-local QA condition explicitly; raw timings still come
	# from Time.get_ticks_usec, and normal runs never enable this observer.
	OS.delta_smoothing=false
	_changed_delta_smoothing=true
	metadata["delta_smoothing_before_probe"]=_previous_delta_smoothing
	metadata["delta_smoothing"]=OS.delta_smoothing
	metadata["delta_smoothing_set_by_probe"]=true
	metadata.merge({"clock":"Time.get_ticks_usec monotonic callback-start intervals","scope":"Frame-loop wall intervals including pacing and CPU/render-loop work, not hardware GPU duration or fixed-60FPS guarantee","warmup_us":WARMUP_US,"sample_us":SAMPLE_US,"max_rows":MAX_ROWS,"stride":STRIDE,"mode_codes":MODES,"engine_args":engine_args,"user_args":Array(OS.get_cmdline_user_args()),"engine_version":Engine.get_version_info(),"display_server":DisplayServer.get_name(),"rendering_method":RenderingServer.get_current_rendering_method(),"rendering_driver":RenderingServer.get_current_rendering_driver_name(),"gpu":RenderingServer.get_video_adapter_name(),"movie_path":Engine.get_write_movie_path(),"max_fps":Engine.max_fps,"time_scale":Engine.time_scale,"vsync_mode":DisplayServer.window_get_vsync_mode(view.get_window().get_window_id()),"io_during_sample":false,"arm_condition":"first playing callback; menu wait excluded","first_interval_discarded":true,"end_boundary":"retain final whole interval crossing sample end; no clipping"},true)
	if not _write_json("metadata.json",metadata):
		io_failed=true;_restore_smoothing();return false
	# Allocation occurs before the warmup clock starts. Overflow invalidates the
	# run explicitly; later frames are never silently substituted or discarded.
	rows.resize(MAX_ROWS*STRIDE)
	enabled=true
	if not _configuration_errors().is_empty():
		finish("configuration_rejected")
		return false
	return true

func observe(view: Node3D, run: RefCounted) -> void:
	if not enabled or done:return
	# A menu can wait indefinitely for root to focus the window and click Start.
	# No warmup time is consumed until the first actual playing callback.
	if _started_us<0 and run.mode!="playing":return
	# Native menu selection can override the CLI primary: verify the actual
	# started scenario rather than treating the launch arguments as proof.
	var scenario := {"seed":int(view.seed_),"primary":String(view.primary)}
	if _started_us<0:
		metadata["actual_scenario_at_start"]=scenario.duplicate()
		metadata["actual_core_primary_at_start"]=String(run.growth.snapshot().primary)
		if metadata.actual_core_primary_at_start!="chapter1.skill.frost":scenario_errors.append({"tick":run.tick,"core_primary":metadata.actual_core_primary_at_start})
	if scenario!={"seed":90131,"primary":"chapter1.skill.frost"}:scenario_errors.append({"tick":run.tick,"scenario":scenario})
	var now := Time.get_ticks_usec()
	var window := view.get_window()
	var window_size := window.size
	var texture := view.get_viewport().get_texture()
	var render_size: Vector2i=Vector2i(texture.get_size()) if texture!=null else Vector2i.ZERO
	var invariant := {"window":str(window.size),"visible":str(view.get_viewport().get_visible_rect().size),"content_scale":window.content_scale_factor,"scale3d":view.get_viewport().scaling_3d_scale,"scale3d_mode":view.get_viewport().scaling_3d_mode,"msaa":view.get_viewport().msaa_3d}
	if invariant!=metadata.get("render_invariant",{}):invariant_errors.append({"at_us":now,"state":invariant})
	_record_at(now,window.has_focus(),MODES.get(run.mode,-1),run.tick,run.enemies.size(),run.projectiles.size(),run.orbs.size(),run.items.size(),window_size,render_size,Engine.get_process_frames(),Engine.get_physics_frames(),Engine.get_frames_drawn())
	if _overflow:finish("sample_capacity_exceeded")
	elif _started_us>=0 and now-_started_us>=WARMUP_US+SAMPLE_US:
		metadata["actual_scenario_at_end"]=scenario.duplicate()
		metadata["actual_core_primary_at_end"]=String(run.growth.snapshot().primary)
		if metadata.actual_core_primary_at_end!="chapter1.skill.frost":scenario_errors.append({"tick":run.tick,"core_primary":metadata.actual_core_primary_at_end})
		metadata["final_game_state"]={"mode":run.mode,"tick":run.tick,"elapsed":run.elapsed(),"kills":run.kills,"hp_raw":run.hero.get("hp_raw",0),"metrics":run.metrics.duplicate(true),"growth":run.growth.snapshot(),"equipped":run.equipped.duplicate(true)}
		finish("complete")

func _record_at(now_us: int, focused: bool, mode_code: int, tick: int, retained: int, projectile_count: int, orb_count: int, item_count: int, window_size: Vector2i, render_size: Vector2i, process_frame: int, physics_frame: int, frames_drawn: int) -> void:
	if _started_us<0:_started_us=now_us
	var elapsed_us := now_us-_started_us
	var interval_us := now_us-_previous_us if _previous_us>=0 else 0
	# 0=warmup,1=measured whole interval (including final crossing),3=warmup boundary.
	var phase := 0
	if _previous_elapsed>=WARMUP_US:phase=1
	elif elapsed_us>=WARMUP_US:phase=3
	if row_count>=MAX_ROWS:
		_overflow=true
		return
	var at := row_count*STRIDE
	rows[at]=row_count;rows[at+1]=elapsed_us;rows[at+2]=interval_us;rows[at+3]=phase
	rows[at+4]=1 if focused else 0;rows[at+5]=mode_code;rows[at+6]=tick;rows[at+7]=retained
	rows[at+8]=projectile_count;rows[at+9]=orb_count;rows[at+10]=item_count
	rows[at+11]=window_size.x;rows[at+12]=window_size.y;rows[at+13]=render_size.x;rows[at+14]=render_size.y
	rows[at+15]=process_frame;rows[at+16]=physics_frame;rows[at+17]=frames_drawn
	row_count+=1;_previous_us=now_us;_previous_elapsed=elapsed_us

func _restore_smoothing() -> void:
	if _changed_delta_smoothing:
		OS.delta_smoothing=_previous_delta_smoothing
		_changed_delta_smoothing=false

func finish(reason: String="scene_exit") -> void:
	if not enabled or done:return
	done=true
	summary=_summarize(reason)
	_restore_smoothing()
	metadata["delta_smoothing_restored_after_sample"]=OS.delta_smoothing
	var csv_path := output_dir.path_join("frames.csv")
	if FileAccess.file_exists(csv_path):
		io_failed=true;summary.eligible_representative_run=false;summary.target_met_for_this_run=false
		push_error("Frame probe refuses to overwrite its raw CSV")
		return
	var csv := FileAccess.open(csv_path,FileAccess.WRITE)
	if csv==null:
		io_failed=true;summary.eligible_representative_run=false;summary.target_met_for_this_run=false
		push_error("Frame probe could not write its raw CSV")
		return
	csv.store_string(HEADER)
	for row in row_count:
		var values := PackedStringArray()
		for col in STRIDE:values.append(str(rows[row*STRIDE+col]))
		csv.store_csv_line(values)
	csv.flush()
	if csv.get_error()!=OK:io_failed=true
	csv.close();csv=null
	summary["raw_csv_sha256"]=FileAccess.get_sha256(csv_path)
	summary["raw_csv_bytes"]=FileAccess.get_file_as_bytes(csv_path).size()
	if not _write_json("final-context.json",metadata):io_failed=true
	if io_failed:summary.eligible_representative_run=false;summary.target_met_for_this_run=false
	if not _write_json("summary.json",summary):io_failed=true
	print("CHAPTER1_FRAME_PROBE_RESULT ",JSON.stringify(summary))
	rows.clear()

func _summarize(reason: String) -> Dictionary:
	var values := PackedInt64Array()
	var unfocused := 0
	var wrong_size := 0
	var forbidden_mode := 0
	var nonpositive := 0
	var measured_us := 0
	var modes: Dictionary={}
	var first_start_us := -1
	var last_end_us := -1
	for row in row_count:
		var at := row*STRIDE
		# Eligibility covers the entire armed warmup + sample, including boundaries.
		if rows[at+4]==0:unfocused+=1
		if rows[at+11]!=1920 or rows[at+12]!=1080 or rows[at+13]!=int(metadata.reported_texture_size[0]) or rows[at+14]!=int(metadata.reported_texture_size[1]):wrong_size+=1
		var mode_code := int(rows[at+5]);modes[str(mode_code)]=int(modes.get(str(mode_code),0))+1
		if mode_code not in [1,2]:forbidden_mode+=1
		if rows[at+3]!=1:continue
		var dt := rows[at+2]
		values.append(dt);measured_us+=dt
		if first_start_us<0:first_start_us=rows[at+1]-dt
		last_end_us=rows[at+1]
		if dt<=0:nonpositive+=1
	values.sort()
	var eligibility_errors: Array[String]=_configuration_errors()
	if reason!="complete":eligibility_errors.append(reason)
	if _overflow:eligibility_errors.append("sample_capacity_exceeded")
	if values.is_empty():eligibility_errors.append("no_measured_intervals")
	if measured_us<59000000:eligibility_errors.append("less_than_59_seconds_of_complete_intervals")
	# No interval is removed: a stall that loses >1s at a boundary makes this
	# fixed-window representative scope unproven; its raw long interval remains.
	if values.size()<300:eligibility_errors.append("fewer_than_300_measured_callbacks")
	if first_start_us<10000000 or first_start_us>11000000:eligibility_errors.append("warmup_boundary_loss_exceeds_1s")
	if last_end_us<70000000 or last_end_us>71000000:eligibility_errors.append("sample_end_overshoot_exceeds_1s")
	if unfocused>0:eligibility_errors.append("unfocused_armed_frames")
	if wrong_size>0:eligibility_errors.append("window_or_reported_texture_changed_from_live_readback_preflight")
	if forbidden_mode>0:eligibility_errors.append("nonplaying_or_nonchoice_armed_frames")
	if nonpositive>0:eligibility_errors.append("nonpositive_intervals")
	if not invariant_errors.is_empty():eligibility_errors.append("render_configuration_changed")
	metadata["render_invariant_errors"]=invariant_errors
	metadata["scenario_errors"]=scenario_errors
	if not scenario_errors.is_empty():eligibility_errors.append("actual_seed_or_primary_not_fixed")
	var p95 := _quantile(values,.95)
	return {"reason":reason,"complete":reason=="complete","scope":"Raw monotonic frame-loop wall intervals; not hardware GPU duration, no maximum180-enemy claim, not fixed60FPS guarantee","rows":row_count,"measured_samples":values.size(),"overflow":_overflow,"warmup_us":WARMUP_US,"requested_sample_us":SAMPLE_US,"measured_interval_sum_us":measured_us,"first_interval_start_us":first_start_us,"last_interval_end_us":last_end_us,"unfocused_samples":unfocused,"wrong_size_samples":wrong_size,"forbidden_mode_samples":forbidden_mode,"nonpositive_samples":nonpositive,"mode_counts":modes,"p50_ms":_quantile(values,.5)/1000.0,"p95_ms":p95/1000.0,"p99_ms":_quantile(values,.99)/1000.0,"worst_ms":int(values[-1])/1000.0 if not values.is_empty() else 0.0,"percentile_rule":"nearest-rank ceil(n*p)-1, all measured intervals retained","eligibility_errors":eligibility_errors,"eligible_representative_run":eligibility_errors.is_empty(),"target_p95_ms":16.67,"target_met_for_this_run":eligibility_errors.is_empty() and p95<=16670,"three_run_gate_complete":false}

func _configuration_errors() -> Array[String]:
	var errors: Array[String]=[]
	var args: Array=metadata.get("engine_args",[])
	if not metadata.get("movie_path","").is_empty():errors.append("movie_writer_enabled")
	if args.has("--fixed-fps"):errors.append("fixed_fps_enabled")
	if args.has("--disable-render-loop"):errors.append("render_loop_disabled")
	if metadata.get("captures_enabled",false):errors.append("png_capture_enabled")
	if metadata.get("input_log_enabled",false):errors.append("input_log_io_enabled")
	if metadata.get("wall_quit_enabled",false):errors.append("wall_quit_instead_of_probe_completion")
	if metadata.get("display_server","")=="headless":errors.append("headless")
	if metadata.get("rendering_method","")!="forward_plus":errors.append("not_forward_plus")
	if metadata.get("max_fps",-1)!=0:errors.append("fps_cap_enabled")
	if metadata.get("time_scale",0.0)!=1.0:errors.append("time_scale_not_one")
	if metadata.get("vsync_mode",-1)!=DisplayServer.VSYNC_DISABLED:errors.append("vsync_not_disabled")
	if metadata.get("qa_ignore_focus",true):errors.append("ignore_focus_enabled")
	if not metadata.get("pilot",false):errors.append("normal_pilot_not_enabled")
	if metadata.get("delta_smoothing",true):errors.append("delta_smoothing_enabled")
	return errors

func _quantile(sorted: PackedInt64Array, fraction: float) -> int:
	if sorted.is_empty():return 0
	return sorted[clampi(ceili(float(sorted.size())*fraction)-1,0,sorted.size()-1)]

func _write_json(filename: String,value: Dictionary) -> bool:
	var path := output_dir.path_join(filename)
	if FileAccess.file_exists(path):
		push_error("Frame probe refuses to overwrite "+path)
		return false
	var file := FileAccess.open(path,FileAccess.WRITE)
	if file==null:
		push_error("Frame probe could not write "+path)
		return false
	file.store_string(JSON.stringify(value,"\t")+"\n");file.flush()
	var ok: bool=file.get_error()==OK
	file.close();file=null
	if not ok:push_error("Frame probe write failed: "+path)
	return ok
