extends SceneTree
## Menu presentation and input only. Profiles are disabled; no victory claim.
var view: Node3D
var output := ""
var checks: Array[Dictionary]=[]
var start_requests: Array[String]=[]
var muted_requests := 0
var motion_requests: Array[bool]=[]
func _initialize() -> void:call_deferred("_probe")
func _probe() -> void:
	if not "--chapter1-profile-off" in OS.get_cmdline_user_args():quit(2);return
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--ui41-output="):output=arg.trim_prefix("--ui41-output=")
	if output.is_empty():quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	root.content_scale_size=Vector2i(1600,900);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view.set_process(false);view.set_physics_process(false);view.audio.set_muted(true)
	for connection in view.hud.start.get_connections():view.hud.start.disconnect(connection.callable)
	view.hud.start.connect(func(id_: String):start_requests.append(id_))
	view.hud.mute_toggle.connect(func():muted_requests+=1)
	view.hud.motion_toggle.connect(func(value: bool):motion_requests.append(value))
	view.hud.profile_note="검사 실행 · 저장 비활성"
	for dimensions in [Vector2i(1280,720),Vector2i(1920,1080)]:
		root.size=dimensions
		view.run.mode="menu";view.hud.stash_open=false;view.hud.invalidate();await _sync()
		var menu: Node=view.hud.modal.get_node_or_null("OathMenu41")
		_check("portrait menu built "+str(dimensions),menu!=null)
		if menu==null:continue
		var texture: TextureRect=menu.find_child("PortraitTexture41",true,false)
		_check("portrait texture loaded "+str(dimensions),texture!=null and texture.texture!=null and texture.texture.get_width()==1024)
		var choices: VBoxContainer=menu.find_child("PrimarySkillChoices41",true,false)
		_check("three unique inherited starts "+str(dimensions),choices!=null and choices.get_child_count()==3)
		_check("first start owns initial focus "+str(dimensions),root.gui_get_focus_owner()==choices.get_child(0))
		var previous := root.gui_get_focus_owner();await _key(KEY_TAB)
		_check("Tab moves within menu "+str(dimensions),root.gui_get_focus_owner()!=previous and view.hud.modal.is_ancestor_of(root.gui_get_focus_owner()))
		start_requests.clear()
		for button in choices.get_children():button.pressed.emit()
		_check("exact inherited skill ids "+str(dimensions),start_requests==["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"])
		var mute := _button_named(menu,"음소거 전환 [M]")
		var before_mute := muted_requests
		if mute!=null:mute.pressed.emit()
		_check("mute uses inherited signal "+str(dimensions),muted_requests==before_mute+1)
		var motion: CheckButton=_check_button(menu)
		var before_motion := motion_requests.size()
		if motion!=null:motion.button_pressed=not motion.button_pressed
		_check("motion toggle signal preserved "+str(dimensions),motion_requests.size()==before_motion+1 and view.hud.motion_enabled==motion.button_pressed)
		_check("portrait keeps source aspect "+str(dimensions),texture.stretch_mode==TextureRect.STRETCH_KEEP_ASPECT_CENTERED)
		await _capture("menu",dimensions)
		var stash: Button=_button_prefix(menu,"장비 보관함")
		if stash!=null:stash.pressed.emit()
		await _sync()
		_check("stash opens from existing callback "+str(dimensions),view.hud.stash_open and view.hud.modal.get_node_or_null("OathMenu41")==null)
		await _key(KEY_ESCAPE);await _sync()
		_check("stash closes to portrait menu "+str(dimensions),not view.hud.stash_open and view.hud.modal.get_node_or_null("OathMenu41")!=null)
		_check("single menu after return "+str(dimensions),view.hud.modal.get_child_count()==1)
	var success := checks.all(func(item):return item.passed)
	var file := FileAccess.open(output.path_join("RESULT.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"success":success,"checks":checks,"scope":"Actual menu input/callback presentation; profile-off, no gameplay or 3D approval"},"  "));file.close()
	view.audio.reset();quit(0 if success else 1)
func _sync() -> void:
	for i in 8:
		view.hud.sync(view.run,.016)
		await process_frame
func _key(code: Key) -> void:
	var event := InputEventKey.new();event.keycode=code;event.pressed=true
	Input.parse_input_event(event);await process_frame
	event=InputEventKey.new();event.keycode=code;event.pressed=false
	Input.parse_input_event(event);await _sync()
func _button_named(node: Node,text_: String) -> Button:
	if node is Button and node.text==text_:return node
	for child in node.get_children():
		var result := _button_named(child,text_)
		if result!=null:return result
	return null
func _button_prefix(node: Node,text_: String) -> Button:
	if node is Button and node.text.begins_with(text_):return node
	for child in node.get_children():
		var result := _button_prefix(child,text_)
		if result!=null:return result
	return null
func _check_button(node: Node) -> CheckButton:
	if node is CheckButton:return node
	for child in node.get_children():
		var result := _check_button(child)
		if result!=null:return result
	return null
func _capture(label: String,dimensions: Vector2i) -> void:
	await RenderingServer.frame_post_draw
	var error := root.get_texture().get_image().save_png(output.path_join("%s-%dx%d.png"%[label,dimensions.x,dimensions.y]))
	_check("capture "+label+str(dimensions),error==OK)
func _check(label: String,passed: bool) -> void:
	checks.append({"name":label,"passed":passed});print("UI41 ",label," = ",passed)
