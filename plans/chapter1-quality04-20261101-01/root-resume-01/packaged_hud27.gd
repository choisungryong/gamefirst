extends SceneTree
var folder := ""
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--hud27-dir="):folder=arg.trim_prefix("--hud27-dir=")
	if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
	DirAccess.make_dir_recursive_absolute(folder)
	var view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view.set_process(false);view.set_physics_process(false)
	var found := false
	while view.run.tick<24000 and not found:
		view.run.events.clear();view.run.step(view.full_pilot.decide())
		for event in view.run.events:
			if event.type=="boss_phase":found=true
	view.actors.reset();view.effects.reset();view.hud.reset();view.hud.sync(view.run,3.0)
	view._consume_events()
	view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,0)
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	var img := root.get_texture().get_image();img.save_png(folder.path_join("actual-boss-phase.png"))
	var toast_rect: Rect2=view.hud.toast.get_global_rect();var boss_rect: Rect2=view.hud.boss_bar.get_global_rect()
	var expected := "파수왕의 격노 · 재의 낙인을 피하세요"
	var text_ok: bool=view.hud.toast.text==expected and view.hud.toast.visible
	var separated: bool=not toast_rect.intersects(boss_rect) and view.hud.boss_bar.visible
	var reference=load("res://chapter1/core/chapter_run_quality16.gd").new();var policy=load("res://chapter1/core/chapter_pilot.gd").new();policy.run=reference
	var started: bool=reference.start(view.seed_,view.primary)
	while reference.tick<view.run.tick:reference.step(policy.decide())
	var same: bool=started and reference.snapshot()==view.run.snapshot()
	var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"found_actual_boss_phase":found,"tick":view.run.tick,"text":view.hud.toast.text,"message_ok":text_ok,"separated":separated,"same_complete_core":same,"hud_script":view.hud.get_script().resource_path,"image":[img.get_width(),img.get_height()],"toast":str(toast_rect),"boss":str(boss_rect),"scope":"Actual27 EXE/PCK components, normal earned policy resim to first actual boss_phase; original event consumer produces message. Frozen actual GPU capture. Not manual/full live chapter or formal performance."},"\t"));f.close()
	view.audio.reset()
	for i in 4:await process_frame
	quit(0 if found and text_ok and separated and same else 1)
