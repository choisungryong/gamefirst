extends "res://chapter1/chapter_one_input21.gd"
var age := 0.0
var shots: Dictionary={}
var ready22 := false
var max_hostile := 0
func _init() -> void:
	super._init()
	effects=preload("res://chapter1/view/chapter_elements_quality22.gd").new()
func _ready() -> void:
	super._ready()
	while run.tick<900:run.step(full_pilot.decide())
	actors.reset();effects.reset();hud.reset();run.events.clear()
	world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);effects.sync(run,0);hud.sync(run,0)
	ready22=true
func _process(delta: float) -> void:
	super._process(delta)
	if not ready22:return
	age+=delta
	var count := 0
	for p in run.projectiles:
		if p.hostile:count+=1
	max_hostile=maxi(max_hostile,count)
	for at in [2.0,5.0,8.0]:
		if age>=at and not shots.has(str(at)):
			shots[str(at)]={"tick":run.tick,"hostile":count};_shot22(str(at))
func _shot22(label: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://hostile22-shots")
	get_viewport().get_texture().get_image().save_png("res://hostile22-shots/live-"+label+".png")
func _print_result() -> void:
	super._print_result()
	if not ready22:return
	var reference=ChapterRun.new();var policy=ChapterPilot.new();policy.run=reference
	var started: bool=reference.start(seed_,primary);assert(started)
	while reference.tick<run.tick:reference.step(policy.decide())
	var same: bool=reference.snapshot()==run.snapshot()
	var f := FileAccess.open("res://hostile22-result.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"same_complete_core":same,"tick":run.tick,"max_hostile":max_hostile,"shots":shots,"scope":"Normal earned policy900ticks then10simsec fixed60 GPU. Single original projectile batch/new hostile shader only, not native manual/fullrun/performance."},"\t"));f.close()
	assert(same)
