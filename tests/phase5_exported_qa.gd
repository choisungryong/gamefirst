extends SceneTree
## External harness for the exported PCK. Product code is never imported from
## the mutable workspace. Direct GUI signals are distinct from OS input.
var checks := 0
var failures: Array[String] = []
var output := ""
var expected_metadata := ""
var dimensions := Vector2i(1440,810)
var captures: Array = []
var normal_before := ""
var view: Node

func _initialize() -> void:
	for argument in OS.get_cmdline_user_args():
		if argument.begins_with("--qa-output="): output = argument.trim_prefix("--qa-output=")
		elif argument.begins_with("--expected-metadata="): expected_metadata = argument.trim_prefix("--expected-metadata=")
		elif argument.begins_with("--qa-width="): dimensions.x = argument.trim_prefix("--qa-width=").to_int()
		elif argument.begins_with("--qa-height="): dimensions.y = argument.trim_prefix("--qa-height=").to_int()
	call_deferred("run")

func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("EXPORTED EQUIPMENT QA FAILED: "+message)

func settled() -> void:
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw

func capture(name_: String) -> void:
	await settled()
	var image_: Image = root.get_texture().get_image()
	var path: String = output.path_join(name_+".png")
	var size_: Vector2i = image_.get_size()
	var saved: bool = image_.save_png(path) == OK
	check(saved and size_ == dimensions,"actual GPU PNG "+name_+" "+str(dimensions))
	captures.append({"path":path,"dimensions":[size_.x,size_.y],"sha256":FileAccess.get_sha256(path) if saved else ""})

func key(code: int) -> InputEventKey:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	return event

func snapshot() -> Dictionary:
	return {"equipment":view.sim.equipment_snapshot(),"stats":view.sim.player_stats_snapshot(),"skill":view.sim.skill_display(),"life":view.sim.life,"life_max_raw":view.sim.life_max_raw,"mana_raw":view.sim.mana_raw,"hud":view.cast_status.text,"modal":view.is_equipment_open(),"paused":view.sim.paused}

func run() -> void:
	if output.is_empty() or expected_metadata.is_empty() or not output.replace("\\","/").contains("/evidence/phase5/") or DirAccess.dir_exists_absolute(output):
		printerr("Use a new bounded phase5 output directory")
		quit(1)
		return
	if DirAccess.make_dir_recursive_absolute(output) != OK:
		quit(1)
		return
	DisplayServer.window_set_size(dimensions)
	root.size = dimensions
	check(DisplayServer.get_name() != "headless","actual graphical display server")
	var res_root: String = ProjectSettings.globalize_path("res://").replace("\\","/")
	var executable: String = OS.get_executable_path().replace("\\","/")
	check(executable.contains("/builds/phase5/phase5-candidate-20261029-01/"),"running executable belongs to accepted candidate directory")
	check(not FileAccess.file_exists("res://baseline_sim.gd") and ResourceLoader.exists("res://baseline_sim.gd"),"exported script exists through resource remap without original source text")
	var metadata_hash: String = FileAccess.get_sha256("res://game_data/build_info.json")
	check(metadata_hash == expected_metadata,"PCK embedded metadata matches accepted export")
	var metadata: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://game_data/build_info.json"))
	check(metadata is Dictionary and metadata.get("build_id","") == "phase5-candidate-20261029-01","PCK build identifier")
	normal_before = FileAccess.get_sha256("user://equipment-v1.json") if FileAccess.file_exists("user://equipment-v1.json") else "absent"
	var packed: PackedScene = load("res://Baseline.tscn")
	if packed == null:
		check(false,"exported Baseline scene loads")
		finish({},metadata_hash,res_root,{},"")
		return
	view = packed.instantiate()
	view.initial_enemies = 0
	root.add_child(view)
	await settled()
	view.set_process(false)
	view.set_physics_process(false)
	check(view.sim.equipment_valid and view.sim.equipment_items().size() == 3,"exported equipment definitions and three initial instances")
	check(view.sim.equipment_snapshot().equipped.is_empty() and view.cast_status.text.contains("Lv.1"),"default remains unequipped baseline skill")
	check(view.auto_button.get_global_rect().end.y <= view.skill_mode_label.get_global_rect().position.y,"automatic button and description do not overlap")
	await capture("frame-default")
	view.equipment_button.pressed.emit()
	var p: RefCounted = view.equipment_presenter
	check(view.is_equipment_open() and view.sim.paused and not view.pause_cover.visible,"exported equipment modal opens and pauses")
	check(p.item_buttons[2].disabled and p.context_label.text.contains("레벨 1"),"level2 charm requirement visible and blocked")
	await settled()
	check(p.panel.get_global_rect().encloses(p.card.get_global_rect()),"modal card fits actual viewport")
	check(p.card.get_global_rect().encloses(p.save_button.get_global_rect()) and p.card.get_global_rect().encloses(p.load_button.get_global_rect()),"modal save/load actions remain in card")
	await capture("frame-equipment-default")
	view.sim.life = 17.0
	view.sim.mana_raw = 1234
	p.item_buttons[0].pressed.emit()
	p.item_buttons[1].pressed.emit()
	check(view.sim.equipment_snapshot().equipped == {"focus":1,"body":2},"real item signals equip focus and robe")
	check(view.sim.skill_display().effective_level == 2 and view.cast_status.text.contains("Lv.2"),"equipped level reaches actual HUD")
	check(view.sim.skill_display().damage_min_raw == 1085 and view.sim.skill_display().damage_max_raw == 2170,"equipped raw damage matches frozen-roll oracle")
	check(view.sim.life_max_raw == 12800 and view.sim.life == 17.0 and view.sim.mana_raw == 1234,"equipping does not restore current life/mana")
	var equipped: Dictionary = snapshot()
	await capture("frame-equipment-equipped")
	var test_directory: String = "res://evidence/phase5/exported-qa/"+output.get_base_dir().get_file()+"/"+output.get_file()
	var test_save: String = test_directory+"/equipment.json"
	var working_directory: String = DirAccess.open(".").get_current_dir().replace("\\","/")
	var resolved_save: String = working_directory.path_join(ProjectSettings.globalize_path(test_save)).simplify_path()
	check(resolved_save.begins_with(executable.get_base_dir()+"/evidence/phase5/"),"isolated fallback save remains under candidate executable phase5 directory")
	check(not FileAccess.file_exists(test_save),"isolated exported save starts absent")
	check(view.sim.save_equipment(test_save),"exported public storage saves isolated path")
	var save_sha: String = FileAccess.get_sha256(test_save)
	check(save_sha.length() == 64,"saved file has readable SHA")
	p.slot_buttons.focus.pressed.emit()
	p.slot_buttons.body.pressed.emit()
	check(view.sim.equipment_snapshot().equipped.is_empty() and view.sim.life_max_raw == 10240 and view.sim.life == 17.0,"unequip restores maxima without recovery")
	check(view.sim.load_equipment(test_save),"exported public storage loads isolated file")
	p.refresh()
	view.sync_equipment_hud()
	check(snapshot().equipment == equipped.equipment and view.sim.life == 17.0 and view.sim.mana_raw == 1234,"load restores exact inventory/roll/RNG/gear without recovery")
	check(FileAccess.get_sha256(test_save) == save_sha,"load does not rewrite saved bytes")
	var bad_path: String = test_directory+"/invalid.json"
	var bad_file := FileAccess.open(bad_path,FileAccess.WRITE)
	if bad_file:
		bad_file.store_string("{invalid")
		bad_file.close()
	else: check(false,"create isolated invalid-load fixture")
	var before_bad: Dictionary = snapshot()
	var bad_sha: String = FileAccess.get_sha256(bad_path)
	check(not view.sim.load_equipment(bad_path) and snapshot() == before_bad and FileAccess.get_sha256(bad_path) == bad_sha,"invalid exported load preserves state and original bytes")
	view.restart()
	check(view.is_equipment_open() and view.sim.paused and view.sim.equipment_snapshot() == equipped.equipment,"R preserves equipment/UID/RNG and open modal")
	check(view.sim.life == 50.0 and view.sim.mana_raw == 8960,"explicit combat reset heals modified maxima")
	await capture("frame-equipment-loaded-reset")
	p.close_button.pressed.emit()
	check(not view.is_equipment_open() and not view.sim.paused,"close restores preceding play state")
	await capture("frame-equipped-play")
	view.toggle_pause()
	view.toggle_equipment()
	view._unhandled_input(key(KEY_ESCAPE))
	check(not view.is_equipment_open() and view.sim.paused and view.pause_cover.visible,"equipment closes back to preceding ordinary pause")
	var final_snapshot: Dictionary = snapshot()
	view.free()
	finish(final_snapshot,metadata_hash,res_root,metadata,test_save)

func finish(state: Dictionary, metadata_hash: String, res_root: String, metadata: Variant, test_save: String) -> void:
	var normal_after: String = FileAccess.get_sha256("user://equipment-v1.json") if FileAccess.file_exists("user://equipment-v1.json") else "absent"
	check(normal_after == normal_before,"external QA never changes normal user equipment save")
	var working_directory: String = DirAccess.open(".").get_current_dir().replace("\\","/")
	var save_resolved: String = working_directory.path_join(ProjectSettings.globalize_path(test_save)).simplify_path()
	var report := {"scope":"External SceneTree against exported PCK, direct signals/public methods; distinct from OS input and performance evidence","checks":checks,"failures":failures,"success":failures.is_empty(),"engine":Engine.get_version_info().string,"display_server":DisplayServer.get_name(),"renderer":RenderingServer.get_current_rendering_method(),"metadata_sha256":metadata_hash,"metadata":metadata,"resource_root":res_root,"working_directory":working_directory,"executable":OS.get_executable_path(),"original_source_text_present":FileAccess.file_exists("res://baseline_sim.gd"),"external_script_sha256":FileAccess.get_sha256(get_script().resource_path),"captures":captures,"final":state,"isolated_save_path":save_resolved,"isolated_save_sha256":FileAccess.get_sha256(test_save) if not test_save.is_empty() else "","normal_user_save_before":normal_before,"normal_user_save_after":normal_after,"user_data_dir":OS.get_user_data_dir()}
	var file := FileAccess.open(output.path_join("qa-report.json"),FileAccess.WRITE)
	if not file:
		quit(1)
		return
	file.store_string(JSON.stringify(report,"\t"))
	file.flush()
	var saved: bool = file.get_error() == OK
	print(JSON.stringify({"scope":report.scope,"checks":checks,"failures":failures,"success":failures.is_empty() and saved}))
	quit(0 if failures.is_empty() and saved else 1)
