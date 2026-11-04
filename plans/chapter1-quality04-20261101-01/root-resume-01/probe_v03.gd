extends SceneTree
## PURE INJECTED CLOCK TESTS. None of these synthetic intervals measures FPS.
const Probe=preload("res://chapter1/presentation/frame_probe.gd")
var checks := 0
var failures: Array[String]=[]
class MenuRun extends RefCounted:
	var mode := "menu"

func check(ok: bool,label: String) -> void:
	checks+=1
	if not ok:failures.append(label)

func fixture():
	var p=Probe.new()
	p.rows.resize(Probe.MAX_ROWS*Probe.STRIDE)
	p.metadata={"engine_args":[],"delta_smoothing":false,"display_server":"windows","rendering_method":"forward_plus","max_fps":0,"time_scale":1.0,"vsync_mode":DisplayServer.VSYNC_DISABLED,"qa_ignore_focus":false,"pilot":true}
	return p

func row(p,t: int,focus: bool=true,mode: int=1,size: Vector2i=Vector2i(1920,1080)) -> void:
	p._record_at(t,focus,mode,42,11,7,3,2,size,size,12,13,14)

func _initialize() -> void:
	var previous_delta:bool=OS.delta_smoothing
	OS.delta_smoothing=false
	check(not OS.delta_smoothing,"actual OS smoothing setter honored")
	OS.delta_smoothing=previous_delta
	check(OS.delta_smoothing==previous_delta,"actual OS smoothing state restored")
	var p=fixture()
	p.enabled=true
	var node=Node3D.new()
	p.observe(node,MenuRun.new())
	check(p._started_us==-1 and p.row_count==0,"menu never consumes warmup")
	node.free()
	row(p,1234)
	row(p,10001234)
	check(p.rows[Probe.STRIDE+3]==3,"warmup crossing interval explicitly separated")
	for second in range(11,71):row(p,second*1000000+1234)
	var s=p._summarize("complete")
	check(s.measured_samples==60 and s.measured_interval_sum_us==60000000,"complete whole interval sample duration")
	check(s.first_interval_start_us==10000000 and s.last_interval_end_us==70000000,"exact warm/sample boundary positions")
	check(s.eligible_representative_run,"synthetic configuration eligibility mechanics only")
	check(p.rows[7]==11 and p.rows[8]==7 and p.rows[9]==3 and p.rows[10]==2,"raw counts preserved")
	var q=fixture()
	row(q,0);row(q,10000001);row(q,69999999);row(q,70500000)
	s=q._summarize("complete")
	check(s.measured_samples==2 and s.worst_ms>59000,"crossing final interval retained without clipping")
	check(s.last_interval_end_us==70500000,"final overshoot explicit")
	var bad=fixture()
	row(bad,0,false);row(bad,10000000);row(bad,70000000,true,6,Vector2i(1440,810))
	s=bad._summarize("complete")
	check(s.eligibility_errors.has("unfocused_armed_frames"),"warmup focus loss invalid")
	check(s.eligibility_errors.has("window_or_render_texture_not_1920x1080"),"resize invalid")
	check(s.eligibility_errors.has("nonplaying_or_nonchoice_armed_frames"),"terminal invalid")
	bad.metadata.delta_smoothing=true
	bad.metadata.max_fps=120
	bad.metadata.movie_path="test.avi"
	bad.metadata.engine_args=["--fixed-fps","30"]
	bad.metadata.display_server="headless"
	s=bad._summarize("scene_exit")
	for reason in ["fps_cap_enabled","movie_writer_enabled","fixed_fps_enabled","headless","scene_exit","delta_smoothing_enabled"]:
		check(s.eligibility_errors.has(reason),"reject "+reason)
	var full=fixture()
	full.row_count=Probe.MAX_ROWS
	row(full,0)
	check(full._overflow and full.row_count==Probe.MAX_ROWS,"overflow explicit and retained rows never replaced")
	check(full._summarize("sample_capacity_exceeded").eligibility_errors.has("sample_capacity_exceeded"),"overflow ineligible")
	check(p._quantile(PackedInt64Array([1,2,3,4,5]),.95)==5,"nearest rank quantile")
	check(not p._summarize("scene_exit").eligible_representative_run,"early exit ineligible")
	print("FRAME_PROBE_PURE_TEST ",JSON.stringify({"checks":checks,"failures":failures,"clock":"injected synthetic; no runtime performance measurement"}))
	quit(0 if failures.is_empty() else 1)
