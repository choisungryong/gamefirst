extends SceneTree
## UI-only deterministic fixture. Real37 core + HUD38, no profile or game window.
const HUD38=preload("res://chapter1/view/ui38/chapter_hud_quality38.gd")
const Core37=preload("res://chapter1/core/chapter_run_quality37.gd")
const Items=preload("res://chapter1/core/chapter_items.gd")
var hud=HUD38.new()
var run=Core37.new()
var result: Dictionary={"scope":"UI38 actual native UI, deterministic core fixture, no profile I/O","checks":[]}
var output := ""
var selected := 0
func _initialize() -> void:
	call_deferred("_probe")
func _probe() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--ui38-output="):output=arg.trim_prefix("--ui38-output=")
	if output.is_empty():quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	var view := Node3D.new();root.add_child(view)
	hud.setup(view)
	hud.start.connect(func(id_: String):run.start(3807,id_))
	hud.choice.connect(func(token: String,id_: String):
		if run.choose(token,id_):selected+=1
	)
	hud.close_equipment.connect(func():run.close_inventory())
	hud.equip_item.connect(func(uid: int):run.equip(uid))
	# Same logical1600x900 canvas as the product, at both physical sizes.
	root.content_scale_size=Vector2i(1600,900)
	root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	for dimensions in [Vector2i(1280,720),Vector2i(1920,1080)]:
		root.size=dimensions
		run.mode="menu";hud.reset();hud.sync(run,0)
		await _settle()
		var owner := root.gui_get_focus_owner()
		_check("menu initial focus "+str(dimensions),owner is Button)
		await _capture("menu",dimensions)
		# Keyboard accept activates the real focused start button.
		await _key(KEY_ENTER)
		hud.sync(run,0);await _settle()
		_check("keyboard start "+str(dimensions),run.mode=="playing")
		_check("HP matches core "+str(dimensions),int(hud.hp.value)==int(run.hero.hp_raw))
		await _capture("combat",dimensions)
		run.growth.award_xp(12);run._refresh_mode();hud.invalidate();hud.sync(run,0)
		await _settle();await _capture("growth",dimensions)
		var before := root.gui_get_focus_owner()
		await _key(KEY_TAB)
		_check("Tab advances modal focus "+str(dimensions),root.gui_get_focus_owner()!=before and hud.modal.is_ancestor_of(root.gui_get_focus_owner()))
		var count_before := selected
		await _key(KEY_ENTER);hud.sync(run,0);await _settle()
		_check("growth single choice "+str(dimensions),selected==count_before+1 and run.mode=="playing")
		# Deterministic generated items are test fixtures, never granted by HUD.
		var rng := RandomNumberGenerator.new();rng.seed=38
		for i in 12:
			var item := Items.roll(rng,4,"rare",["weapon","body","charm","ring"][i%4]);item.uid=3800+i
			run.inventory.append(item)
		run.open_inventory();hud.invalidate();hud.sync(run,0);await _settle()
		await _capture("equipment",dimensions)
		_check("inventory scrollbar retained "+str(dimensions),is_instance_valid(hud._gear_scroll))
		run.close_inventory();hud.sync(run,0);await _settle()
		_check("inventory closes "+str(dimensions),run.mode=="playing" and not hud.overlay.visible)
	var file := FileAccess.open(output.path_join("result.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"  "));file.close()
	var failed := false
	for check in result.checks:
		if not check.passed:failed=true
	quit(1 if failed else 0)
func _settle() -> void:
	for i in 4:await process_frame
func _key(code: Key) -> void:
	var event := InputEventKey.new();event.keycode=code;event.pressed=true
	Input.parse_input_event(event);await process_frame
	event=InputEventKey.new();event.keycode=code;event.pressed=false
	Input.parse_input_event(event);await _settle()
func _capture(label: String,dimensions: Vector2i) -> void:
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(output.path_join("%s-%dx%d.png"%[label,dimensions.x,dimensions.y]))
func _check(label: String,passed: bool) -> void:
	result.checks.append({"name":label,"passed":passed})
	print("UI38 ",label," = ",passed)
