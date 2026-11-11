extends SceneTree
## Actual38 world+HUD40, synthetic read-only stash/terminal fixtures.
## No user profile reads/writes, rewards or manual victory claims.
const Items=preload("res://chapter1/core/chapter_items.gd")
var view: Node3D
var output := ""
var checks: Array[Dictionary]=[]
var equip_request := -1
var salvage_request := -1
func _initialize() -> void:call_deferred("_probe")
func _probe() -> void:
	if not "--chapter1-profile-off" in OS.get_cmdline_user_args():quit(2);return
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--ui40-output="):output=arg.trim_prefix("--ui40-output=")
	if output.is_empty():quit(2);return
	DirAccess.make_dir_recursive_absolute(output)
	root.content_scale_size=Vector2i(1600,900);root.content_scale_mode=Window.CONTENT_SCALE_MODE_CANVAS_ITEMS
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view.set_process(false);view.set_physics_process(false);view.audio.set_muted(true)
	view.start_run("chapter1.skill.frost");view.audio.set_muted(true)
	for i in 180:view.run.step(Vector2.ZERO)
	# Disconnect storage requests from the profile owner: test callbacks only.
	for connection in view.hud.stash_equip.get_connections():view.hud.stash_equip.disconnect(connection.callable)
	for connection in view.hud.stash_salvage.get_connections():view.hud.stash_salvage.disconnect(connection.callable)
	view.hud.stash_equip.connect(func(id_: int):equip_request=id_)
	view.hud.stash_salvage.connect(func(id_: int):salvage_request=id_)
	var rng := RandomNumberGenerator.new();rng.seed=4011
	var records: Array=[]
	for i in 48:
		var item: Dictionary=Items.unique(2,4) if i%4==3 else Items.roll(rng,4,["common","magic","rare"][i%4],["weapon","body","charm"][i%4])
		item.uid=4000+i;records.append({"storage_id":4000+i,"item":item})
	view.hud.profile_state={"items":records,"equipped":{"body":4001},"essence":71,"completed_runs":2}
	view.hud.profile_note="검사 fixture · 저장 비활성"
	var profile_before: String=JSON.stringify(view.hud.profile_state)
	for dimensions in [Vector2i(1280,720),Vector2i(1920,1080)]:
		root.size=dimensions
		view.hud.stash_open=true;view.hud.invalidate();await _sync();await _capture("stash",dimensions)
		_check("recent sort "+str(dimensions),view.hud._stash_records40()[0].storage_id==4047)
		_check("stash keyboard focus "+str(dimensions),view.hud.modal.is_ancestor_of(root.gui_get_focus_owner()))
		var previous_focus := root.gui_get_focus_owner();await _key(KEY_TAB)
		_check("stash Tab remains in modal "+str(dimensions),root.gui_get_focus_owner()!=previous_focus and view.hud.modal.is_ancestor_of(root.gui_get_focus_owner()))
		view.hud._stash_scroll40.scroll_vertical=250;await _sync()
		var saved_scroll: int=view.hud._stash_scroll40.scroll_vertical
		view.hud._storage_selection=4021;view.hud.invalidate();await _sync()
		_check("selection id and scroll retained "+str(dimensions),view.hud._storage_selection==4021 and view.hud._stash_scroll40.scroll_vertical==saved_scroll and saved_scroll>0)
		var equip_button := _button_named(view.hud.modal,"다음 도전에 장착")
		var salvage_button := _button_named(view.hud.modal,"이 장비 해체")
		if equip_button!=null:equip_button.pressed.emit()
		if salvage_button!=null:salvage_button.pressed.emit()
		_check("storage callbacks carry selected id "+str(dimensions),equip_request==4021 and salvage_request==4021)
		view.hud._stash_slot40="body";view.hud._reset_stash_filter40();await _sync()
		var filtered: Array=view.hud._stash_records40()
		_check("slot filter "+str(dimensions),filtered.size()==12 and filtered.all(func(record):return record.item.slot=="body"))
		view.hud._stash_quality40="unique";view.hud._reset_stash_filter40();await _sync()
		_check("empty combined filter "+str(dimensions),view.hud._stash_records40().is_empty())
		await _capture("stash-empty",dimensions)
		view.hud._stash_slot40="";view.hud._stash_quality40="";view.hud._stash_sort40=1;view.hud._reset_stash_filter40();await _sync()
		_check("rarity sort "+str(dimensions),view.hud._stash_records40()[0].item.quality=="unique")
		view.hud._stash_sort40=2;view.hud._reset_stash_filter40();await _sync()
		filtered=view.hud._stash_records40();var ordered := true
		for i in range(1,filtered.size()):
			if String(filtered[i-1].item.name).naturalnocasecmp_to(String(filtered[i].item.name))>0:ordered=false
		_check("name sort "+str(dimensions),ordered)
		view.hud.stash_open=false;view.run.mode="playing"
		for zone in 3:
			view.run.zone=zone;view.run._zone_entered=zone==0
			for i in 3:view.run.seals[i].cleared=i<zone
			view.hud.invalidate();await _sync();await _capture("route-"+str(zone),dimensions)
			_check("actual route zone "+str(zone)+" "+str(dimensions),view.hud._route_labels40[zone].text.begins_with("◆ "))
		view.run.inventory.clear();view.run.equipped.clear()
		for i in 4:view.run.inventory.append(records[i].item.duplicate(true));view.run.equipped[records[i].item.slot]=records[i].item.uid
		for mode_ in ["victory","defeat"]:
			view.run.mode=mode_;view.run._elite_reward_uid=records[3].item.uid if mode_=="victory" else -1
			# Preserve the inherited victory reveal delay, sample after it expires.
			view.hud._previous_mode=mode_;view.hud._victory_age=1.5
			view.hud.profile_note="이번 도전 보상 저장 완료 · fixture" if mode_=="victory" else "검사 fixture · 저장 비활성"
			view.hud.invalidate();await _sync();await _capture(mode_,dimensions)
			var text := _text(view.hud.modal)
			_check("terminal data "+mode_+" "+str(dimensions),text.contains("보유 4개") and text.contains(String(records[0].item.name)) and text.contains(view.hud.profile_note))
			_check("terminal keyboard focus "+mode_+" "+str(dimensions),view.hud.modal.is_ancestor_of(root.gui_get_focus_owner()))
		view.hud._stash_sort40=0
	_check("profile fixture unchanged",JSON.stringify(view.hud.profile_state)==profile_before)
	var success := true
	for check in checks:
		if not check.passed:success=false
	var report: Dictionary={"success":success,"checks":checks,"scope":"Actual38 world HUD40 read-only synthetic stash/routes/results. Not manual victory or real save verification."}
	var file := FileAccess.open(output.path_join("RESULT.json"),FileAccess.WRITE);file.store_string(JSON.stringify(report,"  "));file.close()
	view.audio.reset();print("UI40_RESULT ",JSON.stringify(report));quit(0 if success else 1)
func _sync() -> void:
	for i in 6:
		view.world.update_camera(view.run.hero.position,.016);view.actors.sync(view.run,.016);view.effects.sync(view.run,.016);view.hud.sync(view.run,.016);await process_frame
func _capture(label: String,dimensions: Vector2i) -> void:
	await RenderingServer.frame_post_draw
	_check("capture "+label+" "+str(dimensions),root.get_texture().get_image().save_png(output.path_join("%s-%dx%d.png"%[label,dimensions.x,dimensions.y]))==OK)
func _check(label: String,passed: bool) -> void:checks.append({"name":label,"passed":passed});print("UI40 ",label," = ",passed)
func _key(code: Key) -> void:
	var event := InputEventKey.new();event.keycode=code;event.pressed=true;Input.parse_input_event(event);await process_frame
	event=InputEventKey.new();event.keycode=code;event.pressed=false;Input.parse_input_event(event);await _sync()
func _button_named(node: Node,text: String) -> Button:
	if node is Button and node.text==text:return node
	for child in node.get_children():
		var found := _button_named(child,text)
		if found!=null:return found
	return null
func _text(node: Node) -> String:
	var text := String(node.text) if node is Label else ""
	for child in node.get_children():text+="\n"+_text(child)
	return text
