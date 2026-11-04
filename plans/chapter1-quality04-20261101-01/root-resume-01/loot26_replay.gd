extends "res://chapter1/chapter_one_input21.gd"
var ready22 := false
var age := 0.0
var shots: Dictionary={}
var pickup_uids: Array=[]
var event_seq26 := -1
var ownership_errors: Array=[]
var peak_names26 := 0
func _init() -> void:
	super._init()
	effects=preload("res://chapter1/view/chapter_elements_quality26.gd").new()
func _ready() -> void:
	super._ready()
	while run.tick<16000:run.step(full_pilot.decide())
	actors.reset();effects.reset();hud.reset();run.events.clear()
	world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);effects.sync(run,0);hud.sync(run,0)
	ready22=true
func _physics_process(delta: float) -> void:
 super._physics_process(delta)
 if not ready22:return
 for event in run.events:
  if int(event.seq)<=event_seq26:continue
  event_seq26=int(event.seq)
  if event.type=="item_pickup":pickup_uids.append(event.item.uid)
func _process(delta: float) -> void:
	super._process(delta)
	if not ready22:return
	age+=delta
 peak_names26=maxi(peak_names26,effects.layout26_records.size())
 var expected: Array=[]
 for item in run.items:expected.append(item.uid)
 expected.sort()
 var actual: Array=effects.item_nodes.keys();actual.sort()
 if expected!=actual and ownership_errors.size()<4:ownership_errors.append({"tick":run.tick,"reason":"drop_node_ownership"})
 for uid in pickup_uids:
  if effects.item_nodes.has(uid) and ownership_errors.size()<4:ownership_errors.append({"tick":run.tick,"reason":"collected_name_retained","uid":uid})
	for at in [1.0,3.0,6.0,9.0]:
		if age>=at and not shots.has(str(at)):
			shots[str(at)]={"tick":run.tick,"zone":run.zone,"hero":run.hero.position};_shot22(str(at))
func _shot22(label: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute("res://skin24-shots")
	get_viewport().get_texture().get_image().save_png("res://skin24-shots/live-"+label+".png")
func _print_result() -> void:
	super._print_result()
	if not ready22:return
	var reference=ChapterRun.new();var policy=ChapterPilot.new();policy.run=reference
	var started: bool=reference.start(seed_,primary);assert(started)
	while reference.tick<run.tick:reference.step(policy.decide())
	var same: bool=reference.snapshot()==run.snapshot()
	var f := FileAccess.open("res://skin24-result.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"same_complete_core":same,"tick":run.tick,"shots":shots,"pickup_uids":pickup_uids,"peak_visible_names":peak_names26,"ownership_errors":ownership_errors,"pool_hits":actors.pool25_hits,"pool_created":actors.pool25_created,"pool_size":actors._pool25_size(),"static_memory_bytes":OS.get_static_memory_usage(),"nodes":Performance.get_monitor(Performance.OBJECT_NODE_COUNT),"shared_skins":actors._shared_skin24.size(),"builds":actors.skin24_builds,"hits":actors.skin24_hits,"scope":"Normal earned build/policy16000ticks then14simsec fixed60GPU, Unconnected loot26/World22/Actor25b/HUD23. Partial later-zone replay; not manual/fullrun/performance."},"\t"));f.close()
	assert(same)
