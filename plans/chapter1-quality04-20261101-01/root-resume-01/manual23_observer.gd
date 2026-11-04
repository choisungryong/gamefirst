extends SceneTree
var view: Node
var previous := ""
var next_report := 0.0
var terminal := false
var started_us := 0
class InputLog extends Node:
	var view: Node
	func _input(event: InputEvent) -> void:
		if event is InputEventMouseButton and event.pressed:
			print("MANUAL23_INPUT ",JSON.stringify({"tick":view.run.tick,"mode":view.run.mode,"mouse":event.button_index,"position":event.position,"wall_us":Time.get_ticks_usec()}))
		elif event is InputEventKey and event.pressed and not event.echo:
			print("MANUAL23_INPUT ",JSON.stringify({"tick":view.run.tick,"mode":view.run.mode,"key":event.keycode,"wall_us":Time.get_ticks_usec()}))
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	started_us=Time.get_ticks_usec()
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	var logger := InputLog.new();logger.view=view;root.add_child(logger)
	view.tree_exiting.connect(_save)
	print("MANUAL23_BOOT ",JSON.stringify({"pilot":view._pilot,"profile_off":view._profile_off,"scope":"Actual package23 from menu. Native UI inputs only; observer records/captures/terminal quit, never steps/resimulates/grants/chooses/equips."}))
func _process(_delta: float) -> bool:
	if not is_instance_valid(view):return false
	var signature := str([view.run.mode,view.run.zone,view.run.growth.snapshot().get("level",0),view.run.inventory.size(),view.run.equipped])
	if signature!=previous or view._wall_age>=next_report:
		previous=signature;next_report=view._wall_age+5
		print("MANUAL23_STATE ",JSON.stringify({"mode":view.run.mode,"tick":view.run.tick,"zone":view.run.zone,"kills":view.run.kills,"hero":view.run.hero,"growth":view.run.growth.snapshot(),"items":view.run.inventory.size(),"equipped":view.run.equipped,"actor_cache":view.actors._batch19_cache.size(),"wall_s":float(Time.get_ticks_usec()-started_us)/1000000}))
	if not terminal and view.run.mode in ["victory","defeat"]:
		terminal=true;view._quit_after=view._wall_age+5
	return false
func _save() -> void:
	print("MANUAL23_FINAL ",JSON.stringify({"snapshot":view.run.snapshot(),"pilot":view._pilot,"profile_off":view._profile_off,"wall_s":float(Time.get_ticks_usec()-started_us)/1000000,"scope":"Actual native-input diagnostic from menu; report outcome honestly, not automated policy or final quality approval."}))
