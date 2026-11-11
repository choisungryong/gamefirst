extends SceneTree
const HUD38=preload("res://chapter1/view/ui38/chapter_hud_quality38.gd")
## Actual ChapterOne world, deterministic presentation fixture, no win claim.
var view: Node3D
var output := ""
var failed := false
func _initialize() -> void:call_deferred("_preview")
func _preview() -> void:
	if not "--chapter1-profile-off" in OS.get_cmdline_user_args():quit(2);return
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--ui38-output="):output=arg.trim_prefix("--ui38-output=")
	if output.is_empty():quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	root.content_scale_size=Vector2i(1600,900);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view.set_process(false);view.set_physics_process(false);view.audio.set_muted(true)
	view.start_run("chapter1.skill.frost");view.audio.set_muted(true)
	# Real simulation at fixed ticks, then stop while reviewing layout/contrast.
	for i in 240:view.run.step(Vector2.ZERO)
	view.run.hero.hp_raw=int(view.run.hero.max_hp_raw*.64)
	for dimensions in [Vector2i(1280,720),Vector2i(1920,1080)]:
		root.size=dimensions
		view.run.mode="playing";view.hud.invalidate()
		await _sync()
		await _capture("combat",dimensions)
		var growth: Dictionary=view.run.growth.snapshot()
		var thresholds: Array=view.run.growth.xp_thresholds()
		view.run.growth.award_xp(int(thresholds[int(growth.level)])-int(growth.xp));view.run._refresh_mode();view.hud.invalidate()
		await _sync();await _capture("growth",dimensions)
		while view.run.mode=="choice":
			var offer: Dictionary=view.run.get_offer();view.run.choose(offer.token,offer.cards[0].id)
		var items=load("res://chapter1/core/chapter_items.gd")
		var rng := RandomNumberGenerator.new();rng.seed=38
		view.run.inventory.clear();view.run.equipped.clear();view.hud._selected_item=3800
		for i in 8:
			var item: Dictionary=items.roll(rng,4,"rare",["weapon","body","charm","ring"][i%4]);item.uid=3800+i;view.run.inventory.append(item)
		view.run.open_inventory();view.hud.invalidate();await _sync()
		await _capture("equipment-empty",dimensions)
		view.run.equip(3804);view.hud._selected_item=3800;view.hud.invalidate();await _sync()
		await _capture("equipment-equipped",dimensions)
		view.run.close_inventory();view.hud.invalidate()
	view.audio.reset();quit(1 if failed else 0)
func _sync() -> void:
	for i in 8:
		view.world.update_camera(view.run.hero.position,.016)
		view.actors.sync(view.run,.016);view.effects.sync(view.run,.016);view.hud.sync(view.run,.016)
		await process_frame
func _capture(label: String,dimensions: Vector2i) -> void:
	await RenderingServer.frame_post_draw
	var error := root.get_texture().get_image().save_png(output.path_join("%s-%dx%d.png"%[label,dimensions.x,dimensions.y]))
	if error!=OK:failed=true
