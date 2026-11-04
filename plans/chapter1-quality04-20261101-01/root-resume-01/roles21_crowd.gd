extends "res://chapter1/chapter_one_view.gd"
var frame := 0
var frame_ms: Array[float]=[]
var actor_ms: Array[float]=[]
var last_us := 0
var armed := false
var originals: Dictionary={}
var baseline: Dictionary={}
var start_tick := 0
var image_size := Vector2i.ZERO
func _ready() -> void:
	super._ready();set_physics_process(false)
	Engine.max_fps=0;DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED);get_window().size=Vector2i(1920,1080)
	baseline=run.snapshot().duplicate(true);originals=run.enemies;start_tick=run.tick
	var source: Dictionary=originals.values()[0]
	run.enemies={}
	for i in 180:
		var e: Dictionary=source.duplicate(true)
		e.id=10000+i;e.kind="walker" if i<129 else ("ranged" if i<162 else "charger");e.elite=false;e.state="move";e.frozen_until=0;e.direction=Vector2.RIGHT
		e.position=run.hero.position+Vector2((i%18-8.5)*.65,(i/18-4.5)*.65);run.enemies[e.id]=e
	actors.reset();actors.sync(run,.016);last_us=Time.get_ticks_usec();armed=true
func _process(delta: float) -> void:
	if not armed:return
	var now := Time.get_ticks_usec();var interval := float(now-last_us)/1000.0;last_us=now
	frame+=1;run.tick+=1
	for e in run.enemies.values():e.position.x+=.003
	var before := Time.get_ticks_usec();actors.sync(run,delta);var cost := float(Time.get_ticks_usec()-before)/1000.0
	world.sync(run,delta)
	if frame==100:_warm_capture21()
	if frame>120:frame_ms.append(interval);actor_ms.append(cost)
	if frame>=480:
		armed=false;set_process(false)
		var report := {"roles":{"walker":129,"ranged":33,"charger":18},"image_size":image_size,"frames":frame_ms.size(),"frame_wall":_stats21(frame_ms),"actor_callback_wall":_stats21(actor_ms),"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),"scope":"Synthetic180 mixed roles, native1920x1080/MSAA2/vsync off/uncapped,120warmup+360frames. OS monotonic intervals; actor callback wall cost separately measured, no GPU hardware/normal-gameplay/final3run claim."}
		var raw := FileAccess.open("res://crowd21-samples.json",FileAccess.WRITE);raw.store_string(JSON.stringify({"frame_ms":frame_ms,"actor_ms":actor_ms}));raw.close()
		run.enemies=originals;run.tick=start_tick;actors.reset();actors.sync(run,0);report.core_restored=baseline==run.snapshot()
		var f := FileAccess.open("res://crowd21-result.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close()
		audio.reset()
		for i in 4:await get_tree().process_frame
		get_tree().quit(0 if report.core_restored else 1)
func _warm_capture21() -> void:
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image();image_size=image.get_size();image.save_png("res://crowd21.png")
func _stats21(values: Array[float]) -> Dictionary:
	var sorted := values.duplicate();sorted.sort();var sum_ := 0.0;var over33 := 0
	for value in values:
		sum_+=value
		if value>33.334:over33+=1
	return {"mean_ms":sum_/values.size(),"p50_ms":sorted[values.size()/2],"p95_ms":sorted[int(values.size()*.95)],"p99_ms":sorted[int(values.size()*.99)],"max_ms":sorted[-1],"over33ms":over33}
