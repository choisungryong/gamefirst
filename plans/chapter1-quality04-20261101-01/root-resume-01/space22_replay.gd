extends "res://chapter1/chapter_one_input21.gd"
var ready22 := false
var age := 0.0
var shots: Dictionary={}
func _init() -> void:
	super._init()
	world=preload("res://chapter1/view/chapter_world_quality22.gd").new()
	effects=preload("res://chapter1/view/chapter_elements_quality22.gd").new()
func _ready() -> void:
	super._ready()
	while run.tick<16000:run.step(full_pilot.decide())
	actors.reset();effects.reset();hud.reset();run.events.clear()
	world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);effects.sync(run,0);hud.sync(run,0)
	ready22=true
func _process(delta: float) -> void:
	super._process(delta)
	if not ready22:return
	age+=delta
	for at in [1.0,3.0,6.0,9.0]:
		if age>=at and not shots.has(str(at)):
			shots[str(at)]={"tick":run.tick,"zone":run.zone,"hero":run.hero.position};_shot22(str(at))
func _shot22(label: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://space22-shots")
	get_viewport().get_texture().get_image().save_png("res://space22-shots/live-"+label+".png")
func _print_result() -> void:
	super._print_result()
	if not ready22:return
	var reference=ChapterRun.new();var policy=ChapterPilot.new();policy.run=reference
	var started: bool=reference.start(seed_,primary);assert(started)
	while reference.tick<run.tick:reference.step(policy.decide())
	var same: bool=reference.snapshot()==run.snapshot()
	var f := FileAccess.open("res://space22-result.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"same_complete_core":same,"tick":run.tick,"shots":shots,"art":world.art_status,"scope":"Normal earned build/policy16000ticks then10simsec fixed60GPU, World22+FX22. Partial later-zone replay; not manual/fullrun/performance."},"\t"));f.close()
	assert(same)
