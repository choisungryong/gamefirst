extends SceneTree
var view: Node
var first_victory: Dictionary={}
var observer: Node
var victory_wall := -1.0
var shots: Dictionary={}
class ColdObserver extends Node:
	var view: Node
	var epoch := -1
	var seq := -1
	var shatters := 0
	var cold_deaths := 0
	var counts: Dictionary={}
	func _physics_process(_delta: float) -> void:
		var actual_epoch: int=view.run._epoch
		if actual_epoch!=epoch:epoch=actual_epoch;seq=-1;shatters=0;cold_deaths=0
		for event in view.run.events:
			if int(event.seq)<=seq:continue
			seq=int(event.seq)
			if event.type=="shatter":
				shatters+=1
				if event.get("cause","")=="cold_death":cold_deaths+=1
		counts={"epoch":epoch,"shatters":shatters,"cold_death_cause":cold_deaths,"tick":view.run.tick,"mode":view.run.mode}
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	observer=ColdObserver.new();observer.view=view;observer.process_physics_priority=100;root.add_child(observer)
	view.tree_exiting.connect(_save)
	print("OBSERVER17_BOOT ",JSON.stringify({"epoch":view.run._epoch,"source":"External read-only event observer; packaged17 presentation/core resources"}))
func _process(_delta: float) -> bool:
	if not is_instance_valid(view):return false
	if view.run.mode=="victory" and first_victory.is_empty():
		first_victory=view.run.snapshot();victory_wall=view._wall_age;view._quit_after=view._wall_age+2.1
	if victory_wall>=0:
		for at in [.35,.9,1.6]:
			if view._wall_age-victory_wall>=at and not shots.has(str(at)):
				shots[str(at)]=true
				if not view._capture_dir.is_empty():view._capture_file("victory-after-%.2f.png"%at)
	return false
func _save() -> void:
	print("PACKAGED17_GPU_OBSERVER ",JSON.stringify({"first_victory":first_victory,"counts":observer.counts,"scope":"Actual packed17 resources; external observer only adjusts wall quit after first victory. No HP/rank/item grants. Not manual/audio/performance/final art approval."}))
