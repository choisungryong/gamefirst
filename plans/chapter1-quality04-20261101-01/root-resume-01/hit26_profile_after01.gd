extends "res://chapter1/chapter_one_input21.gd"
class TimedActors extends "res://chapter1/view/chapter_actors_quality26.gd":
	var creations: Array[Dictionary]=[]
	var sources: Array[Dictionary]=[]
	var sync_us := 0
	func _create(kind: String) -> Node3D:
		var begin := Time.get_ticks_usec()
		var actor := super._create(kind)
		creations.append({"tick":view.run.tick,"kind":kind,"us":Time.get_ticks_usec()-begin,"cache":_batch19_cache.size()})
		return actor
	func _demon19_materials(node: Node,materials: Array[StandardMaterial3D],kind: String) -> void:
		for child in node.get_children():
			if child is MeshInstance3D:
				sources.append({"tick":view.run.tick,"id":child.mesh.get_instance_id(),"path":child.mesh.resource_path,"name":child.mesh.resource_name,"node":child.name,"local_to_scene":child.mesh.resource_local_to_scene,"kind":kind})
		super._demon19_materials(node,materials,kind)
	func sync(run: RefCounted,delta: float) -> void:
		var begin := Time.get_ticks_usec();super.sync(run,delta);sync_us=Time.get_ticks_usec()-begin
var armed := false
var rows: Array[Dictionary]=[]
var physics_us := 0
func _init() -> void:
	super._init();actors=TimedActors.new()
func _ready() -> void:
	super._ready()
	while run.tick<2800:run.step(full_pilot.decide())
	actors.reset();effects.reset();hud.reset();run.events.clear()
	world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);effects.sync(run,0);hud.sync(run,0)
	actors.creations.clear();actors.sources.clear();armed=true
func _physics_process(delta: float) -> void:
	var begin := Time.get_ticks_usec();super._physics_process(delta);physics_us+=Time.get_ticks_usec()-begin
func _process(delta: float) -> void:
	var begin := Time.get_ticks_usec();super._process(delta)
	if not armed:return
	rows.append({"tick":run.tick,"process_us":Time.get_ticks_usec()-begin,"actors_us":actors.sync_us,"physics_us":physics_us,"cache":actors._batch19_cache.size()});physics_us=0
func _print_result() -> void:
	super._print_result()
	if not armed:return
	var reference=ChapterRun.new();var policy=ChapterPilot.new();policy.run=reference
	reference.start(seed_,primary)
	while reference.tick<run.tick:reference.step(policy.decide())
	var same: bool=reference.snapshot()==run.snapshot()
	var file := FileAccess.open("res://pool25-result.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"same_complete_core":same,"tick":run.tick,"rows":rows,"creations":actors.creations,"mesh_sources":actors.sources,"pool_hits":actors.pool25_hits,"pool_created":actors.pool25_created,"pool_size":actors._pool25_size(),"hit_blends":actors.get("hit26_blends"),"shared_skins":actors._shared_skin24.size(),"builds":actors.skin24_builds,"hits":actors.skin24_hits,"scope":"Source25b normal ember2800tick checkpoint then10simsec fixed60 instrumentation. CPU callback attribution, not formal frame pacing or native fullrun."},"\t"));file.close();assert(same)
