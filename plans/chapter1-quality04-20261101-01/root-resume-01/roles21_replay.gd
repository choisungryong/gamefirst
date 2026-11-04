extends "res://chapter1/chapter_one_view.gd"
var age := 0.0
var shots: Dictionary={}
var roles: Dictionary={}
var armed := false
func _ready() -> void:
	super._ready()
	while run.tick<6500:run.step(full_pilot.decide())
	actors.reset();effects.reset();hud.reset();run.events.clear()
	world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);hud.sync(run,0);armed=true
func _process(delta: float) -> void:
	super._process(delta)
	if not armed:return
	age+=delta
	for at in [1.0,3.0,6.0]:
		if age>=at and not shots.has(str(at)):shots[str(at)]=true;_roles21_shot("field-%.1f"%at)
	for actor in actors.actors.values():
		if not actor.has_meta("role21"):continue
		var e: Dictionary=actors._entity(actor)
		if e.is_empty() or e.hp_raw<=0:continue
		var key: String=e.kind+"-"+e.state
		if e.state not in ["windup","dash","recover"] or roles.has(key):continue
		roles[key]={"tick":run.tick,"id":e.id,"state":e.state,"direction":e.attack_direction,"pose":actor.get_meta("minion19_pose",{}),"dash":actor.get_meta("role21_dash",{})}
		if e.kind=="ranged":
			var staff: Node3D=actor.find_child("CasterStaff21",true,false)
			var camera := get_viewport().get_camera_3d()
			roles[key].staff_projected_span=camera.unproject_position(staff.to_global(Vector3(0,2.4,0))).distance_to(camera.unproject_position(staff.to_global(Vector3(0,-1.05,0))))
		_roles21_shot(key)
func _roles21_shot(label: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://roles21-shots")
	get_viewport().get_texture().get_image().save_png("res://roles21-shots/"+label+".png")
func _print_result() -> void:
	super._print_result()
	if not armed:return
	var reference=ChapterRun.new();var policy=ChapterPilot.new();policy.run=reference
	var started: bool=reference.start(seed_,primary);assert(started)
	while reference.tick<run.tick:reference.step(policy.decide())
	var same: bool=reference.snapshot()==run.snapshot()
	var f := FileAccess.open("res://roles21-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"same_complete_core_as_normal_reference":same,"tick":run.tick,"roles":roles,"scope":"Normal earned build/policy resimulated6500ticks then20s fixed60GPU role presentation study; not manual/fullrun/performance or final art."},"\t"));f.close();assert(same)
