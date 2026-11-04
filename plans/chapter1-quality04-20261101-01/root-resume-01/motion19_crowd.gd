extends "res://chapter1/chapter_one_view.gd"
var frame := 0
var samples: Array[float]=[]
var ready_ := false
var originals: Dictionary={}
var baseline: Dictionary={}
var start_tick := 0
func _ready() -> void:
	super._ready();set_physics_process(false)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	get_window().size=Vector2i(1920,1080)
	baseline=run.snapshot().duplicate(true);originals=run.enemies;start_tick=run.tick
	var source: Dictionary=originals.values()[0]
	run.enemies={}
	for i in 180:
		var e: Dictionary=source.duplicate(true)
		e.id=10000+i;e.kind="walker";e.elite=false;e.state="move";e.frozen_until=0;e.direction=Vector2.RIGHT
		e.position=run.hero.position+Vector2((i%18-8.5)*.65,(i/18-4.5)*.65)
		run.enemies[e.id]=e
	actors.reset();actors.sync(run,.016);ready_=true
func _process(delta: float) -> void:
	if not ready_:return
	frame+=1;run.tick+=1
	for e in run.enemies.values():e.position.x+=.003
	actors.sync(run,delta);world.sync(run,delta)
	if frame==120:
		await RenderingServer.frame_post_draw
		get_viewport().get_texture().get_image().save_png("res://crowd.png")
	if frame>120:samples.append(delta*1000)
	if frame>=480:
		ready_=false;set_process(false)
		var sum_ := 0.0
		for value in samples:sum_+=value
		samples.sort()
		var report := {"viewport":get_viewport().get_visible_rect().size,"actors":actors.actors.size(),"frames":samples.size(),"mean_ms":sum_/samples.size(),"p50_ms":samples[samples.size()/2],"p95_ms":samples[int(samples.size()*.95)],"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),"scope":"Uncapped native1080p synthetic180walker crowd;120warmup+360samples, no normal-gameplay/final3run claim."}
		run.enemies=originals;run.tick=start_tick;actors.reset();actors.sync(run,0)
		report.core_restored=baseline==run.snapshot()
		var f := FileAccess.open("res://crowd-result.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close()
		audio.reset()
		for i in 4:await get_tree().process_frame
		get_tree().quit(0 if report.core_restored else 1)
