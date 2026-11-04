extends SceneTree
var view: Node
var age := 0.0
var shots: Dictionary={}
var capture := ""
var finished := false
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	capture=OS.get_executable_path().get_base_dir().path_join("qa-captures/visual22-01")
	DirAccess.make_dir_recursive_absolute(capture)
	view._capture_dir=""
	while view.run.tick<16000:view.run.step(view.full_pilot.decide())
	view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
	view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,0)
func _process(delta: float) -> bool:
	if not is_instance_valid(view) or finished:return false
	age+=delta
	for at in [1.0,3.0,5.0]:
		if age>=at and not shots.has(str(at)):
			shots[str(at)]={"tick":view.run.tick,"hero":view.run.hero.position,"zone":view.run.zone};_shot(str(at))
	if age>=6:
		finished=true;view.set_physics_process(false);call_deferred("_finish")
	return false
func _shot(label: String) -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(capture.path_join("live-"+label+".png"))
func _finish() -> void:
	var reference=load("res://chapter1/core/chapter_run_quality16.gd").new()
	var policy=load("res://chapter1/core/chapter_pilot.gd").new();policy.run=reference
	reference.start(view.seed_,view.primary)
	while reference.tick<view.run.tick:reference.step(policy.decide())
	var same: bool=reference.snapshot()==view.run.snapshot()
	print("PACKAGED22_VISUAL ",JSON.stringify({"same_complete_core":same,"tick":view.run.tick,"shots":shots,"world_script":view.world.get_script().resource_path,"fx_script":view.effects.get_script().resource_path,"scope":"Actual22 EXE/PCK. Normal earned build/policy16000 checkpoint then6simsec GPU. Partial replay, not native manual/fullrun/performance."}))
	quit(0 if same else 1)
