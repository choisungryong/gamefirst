extends SceneTree
var view: Node3D
var folder := ""
var selection := ""
var ready_ := false
var ending := false
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--slot-dir="):folder=arg.trim_prefix("--slot-dir=")
		if arg.begins_with("--slot-selection="):selection=arg.trim_prefix("--slot-selection=")
	if folder.is_empty() or DirAccess.dir_exists_absolute(folder) or selection not in ["walker","all"]:quit(1);return
	DirAccess.make_dir_recursive_absolute(folder)
	view=load("res://chapter1/ChapterOne.tscn").instantiate();view.actors=load("res://chapter1/presentation/sprite_role_actors_preview.gd").new()
	var registry_ok: bool=view.actors.registry.configure("res://plans/chapter1-quality04-20261101-01/sprite-slots01/registry-"+selection+".json")
	if not registry_ok:push_error(view.actors.registry.error);quit(1);return
	root.add_child(view)
	while view.run.tick<2800:view.run.step(view.full_pilot.decide())
	view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear();view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
	if DisplayServer.get_name()!="headless":
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(folder.path_join("before.png"))
	ready_=true
func _process(_delta: float) -> bool:
	if ready_ and not ending and view.run.tick>=3400:
		ending=true;view.set_process(false);view.set_physics_process(false);call_deferred("_finish")
	return false
func _finish() -> void:
	var reference=load("res://chapter1/core/chapter_run_quality16.gd").new();var policy=load("res://chapter1/core/chapter_pilot.gd").new();policy.run=reference
	var started: bool=reference.start(view.seed_,view.primary)
	while reference.tick<view.run.tick:reference.step(policy.decide())
	var same: bool=started and reference.snapshot()==view.run.snapshot()
	var slots: Dictionary={};var only_selected := true
	for actor in view.actors.actors.values():
		var kind: String=actor.get_meta("kind")
		if actor.has_meta("minion19"):
			var state: Dictionary=actor.get_meta("minion19")
			var bound: bool=state.has("sprite_slot")
			only_selected=only_selected and bound==view.actors.registry.bindings.has(kind)
			if bound:slots[kind]=int(slots.get(kind,0))+1;only_selected=only_selected and not state.model.visible
	var hero_selected: bool=view.actors._hero_slot!=null
	only_selected=only_selected and hero_selected==view.actors.registry.bindings.has("hero")
	var old_zone: int=view.run.zone;view.run.zone=2
	var boss: Node3D=view.actors._create("elite");view.add_child(boss)
	var boss_kept: bool=boss.has_meta("enemy_rig") and view.actors._slot_for(boss)==null
	boss.queue_free();view.run.zone=old_zone
	if DisplayServer.get_name()!="headless":
		await RenderingServer.frame_post_draw
		var img := root.get_texture().get_image();img.save_png(folder.path_join("after.png"))
	var checks := {"same_complete_core":same,"only_selected_roles_replaced":only_selected,"hero_selection_correct":hero_selected==(selection=="all"),"final_boss_keeps3D":boss_kept,"pool224_retained":view.actors.pool25_created==224,"sprite_samples_nonzero":view.actors.slot_samples>0,"original_profile_off":view._profile_off}
	var ok := true
	for value in checks.values():ok=ok and bool(value)
	var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"passed":ok,"selection":selection,"tick":view.run.tick,"visible_slot_counts":slots,"samples":view.actors.slot_samples,"fallbacks":view.actors.slot_fallbacks,"registry_warnings":view.actors.registry.warnings,"scope":"Isolated source30 role-slot combat preview, normal earned2800checkpoint then original live policy/controllers3400. Actor presentation only. Not new package/manual/full chapter/performance/audio approval. Hidden3D rigs retained as compatibility scaffolding."},"\t"));f.close()
	view.audio.reset();view.queue_free();view=null
	for i in 8:await process_frame
	load("res://chapter1/presentation/sprite_asset_presenter_v2.gd").clear_shared_cache()
	for i in 4:await process_frame
	quit(0 if ok else 1)
