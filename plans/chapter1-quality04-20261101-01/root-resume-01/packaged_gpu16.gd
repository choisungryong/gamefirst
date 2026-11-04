extends SceneTree
var view: Node
var first_victory: Dictionary={}
var observer: Node

class ColdObserver extends Node:
	var view: Node
	var epoch := -1
	var seq := -1
	var shatters := 0
	var cold_deaths := 0
	var counts: Dictionary={}
	func _physics_process(_delta: float) -> void:
		if view.run.epoch!=epoch:
			epoch=view.run.epoch;seq=-1;shatters=0;cold_deaths=0
		for event in view.run.events:
			if int(event.seq)<=seq:continue
			seq=int(event.seq)
			if event.type=="shatter":
				shatters+=1
				if event.get("cause","")=="cold_death":cold_deaths+=1
		counts={"epoch":epoch,"shatters":shatters,"cold_death_cause":cold_deaths,"tick":view.run.tick,"mode":view.run.mode}

func _initialize() -> void:
	call_deferred("_boot")
func _boot() -> void:
	view=load("res://chapter1/ChapterOne.tscn").instantiate()
	root.add_child(view)
	observer=ColdObserver.new();observer.view=view;observer.process_physics_priority=100
	root.add_child(observer)
	view.tree_exiting.connect(_save)
func _process(_delta: float) -> bool:
	if is_instance_valid(view) and view.run.mode=="victory" and first_victory.is_empty():
		first_victory=view.run.snapshot()
		# Keep terminal death animation, then use the view's normal audio shutdown.
		view._quit_after=view._wall_age+1.6
	return false
func _save() -> void:
	print("PACKAGED16_GPU_OBSERVER ",JSON.stringify({"first_victory":first_victory,"counts":observer.counts,"scope":"Actual packed resources, normal earned-growth policy; external observer only shortens wall quit after first victory. Not manual/audio/formal performance approval."}))
