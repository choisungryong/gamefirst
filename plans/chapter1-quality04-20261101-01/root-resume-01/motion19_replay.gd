extends "res://chapter1/chapter_one_view.gd"
var age := 0.0
var shots: Dictionary={}
var armed := false
func _ready() -> void:
	super._ready()
	while run.tick<6500:run.step(full_pilot.decide())
	actors.reset();effects.reset();run.events.clear()
	world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);hud.invalidate();hud.sync(run,6500.0/60.0)
	_save("start",run.snapshot());armed=true
func _save(name_: String,data: Variant) -> void:
	var f := FileAccess.open("res://motion19-"+name_+".json",FileAccess.WRITE);f.store_string(JSON.stringify(data,"\t"));f.close()
func _process(delta: float) -> void:
	super._process(delta)
	if not armed:return
	age+=delta
	for at in [1.0,2.0,3.0,4.0,6.0,7.5]:
		if age>=at and not shots.has(str(at)):shots[str(at)]=true;_shot(at)
func _shot(at: float) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://motion19-shots")
	get_viewport().get_texture().get_image().save_png("res://motion19-shots/at-%04.1f.png"%at)
func _print_result() -> void:
	super._print_result()
	if not armed:return
	_save("end",run.snapshot())
	var rigs := 0;var poses: Dictionary={}
	for actor in actors.actors.values():
		if actor.has_meta("minion19"):
			rigs+=1
			var pose: Dictionary=actor.get_meta("minion19_pose",{})
			poses[String(pose.get("clip","none"))]=int(poses.get(String(pose.get("clip","none")),0))+1
	_save("visual",{"rigs":rigs,"poses":poses,"samples":actors.get("motion19_samples"),"scope":"Normal earned build/policy core resimulated6500ticks then8s fixed60 GPU replay; motion comparison only, not final art/manual/performance."})
