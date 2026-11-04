extends SceneTree
var view: Node
var observer: Node
var first_victory: Dictionary={}
var victory_wall := -1.0
var shots: Dictionary={}
class Observer19 extends Node:
	var view: Node
	var epoch := -1
	var seq := -1
	var shatters := 0
	var cold_deaths := 0
	var intervals: Array[float]=[]
	var process_ms: Array[float]=[]
	var zones: Dictionary={}
	func _physics_process(_delta: float) -> void:
		if view.run._epoch!=epoch:epoch=view.run._epoch;seq=-1;shatters=0;cold_deaths=0
		for event in view.run.events:
			if int(event.seq)<=seq:continue
			seq=int(event.seq)
			if event.type=="shatter":
				shatters+=1
				if event.get("cause","")=="cold_death":cold_deaths+=1
	func _process(delta: float) -> void:
		if view._wall_age<5:return
		intervals.append(delta*1000);process_ms.append(Performance.get_monitor(Performance.TIME_PROCESS)*1000)
		var zone_: String=str(view.run.zone)
		if not zones.has(zone_):zones[zone_]={"frames":0,"over33ms":0,"peak_actors":0}
		zones[zone_].frames+=1
		if delta>.0333334:zones[zone_].over33ms+=1
		zones[zone_].peak_actors=maxi(zones[zone_].peak_actors,view.actors.actors.size())
	func stats(values: Array[float]) -> Dictionary:
		var ordered := values.duplicate();ordered.sort();var sum_ := 0.0;var over33 := 0;var over50 := 0
		for value in values:
			sum_+=value
			if value>33.334:over33+=1
			if value>50:over50+=1
		if values.is_empty():return {}
		return {"frames":values.size(),"mean_ms":sum_/values.size(),"p50_ms":ordered[values.size()/2],"p95_ms":ordered[int(values.size()*.95)],"p99_ms":ordered[int(values.size()*.99)],"max_ms":ordered[-1],"over33ms":over33,"over50ms":over50}
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view.get_window().size=Vector2i(1920,1080);DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	observer=Observer19.new();observer.view=view;observer.process_physics_priority=100;root.add_child(observer)
	view.tree_exiting.connect(_save)
	print("OBSERVER19_BOOT ",JSON.stringify({"epoch":view.run._epoch,"source":"External read-only event/frame observer on actual package19;1080p vsync off maxfps120; profile off."}))
func _process(_delta: float) -> bool:
	if not is_instance_valid(view):return false
	if view.run.mode=="victory" and first_victory.is_empty():first_victory=view.run.snapshot();victory_wall=view._wall_age;view._quit_after=view._wall_age+2.1
	if victory_wall>=0:
		for at in [.35,.9,1.6]:
			if view._wall_age-victory_wall>=at and not shots.has(str(at)):
				shots[str(at)]=true
				if not view._capture_dir.is_empty():view._capture_file("victory-after-%.2f.png"%at)
	return false
func _save() -> void:
	var report := {"first_victory":first_victory,"counts":{"epoch":observer.epoch,"shatters":observer.shatters,"cold_death_cause":observer.cold_deaths,"tick":view.run.tick,"mode":view.run.mode},"frame_intervals":observer.stats(observer.intervals),"process_time":observer.stats(observer.process_ms),"zones":observer.zones,"render_size":view.get_viewport().get_texture().get_size(),"scope":"Actual package19 normal-policy earned full run; frame intervals include maxfps120 presentation cap,5s warmup excluded. CPU process time separate, no GPU hardware timings/manual/audio/final3run claim."}
	print("PACKAGED19_GPU_OBSERVER ",JSON.stringify(report))
