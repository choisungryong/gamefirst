extends SceneTree
var view: Node
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	while view.run.mode!="victory":view.run.step(view.full_pilot.decide())
	view._pilot=false;view.actors.reset();view.effects.reset();view.run.events.clear()
	view.world.update_camera(view.run.hero.position,10);view.actors.sync(view.run,0);view.world.sync(view.run,0)
	view.hud.sync(view.run,2);view.open_equipment();view.hud._selected_item=view.run._elite_reward_uid;view.hud.invalidate();view.hud.sync(view.run,0)
	print("NATIVE_GEAR17_SCOPE ",JSON.stringify({"tick":view.run.tick,"kills":view.run.kills,"inventory":view.run.inventory.size(),"scope":"Normal earned build core resimulated to victory, then native inventory input QA only; not full manual play"}))
	view.tree_exiting.connect(func():print("NATIVE_GEAR17_FINAL ",JSON.stringify({"mode":view.run.mode,"selected":view.hud._selected_item,"scroll":view.hud._scroll_position,"equipped":view.run.equipped})))
