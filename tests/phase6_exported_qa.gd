extends SceneTree
## External harness for the exported PCK. Product code is never imported from
## the mutable workspace. Direct GUI signals are distinct from OS input.
class IsolatedSim extends "res://baseline_sim.gd":
	var isolated_path := ""
	func save_progress(_path: String = "") -> bool:
		return super.save_progress(isolated_path)
	func load_progress(_path: String = "") -> bool:
		return super.load_progress(isolated_path)
var normal_progress_before := ""
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
		printerr("EXPORTED PROGRESS QA FAILED: "+message)

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
	return {"progress":view.sim.progress_document(),"equipment":view.sim.equipment_snapshot(),"stats":view.sim.player_stats_snapshot(),"skill":view.sim.skill_display(),"life":view.sim.life,"life_max_raw":view.sim.life_max_raw,"mana_raw":view.sim.mana_raw,"hud":view.cast_status.text,"modal":view.is_equipment_open(),"paused":view.sim.paused}

func run() -> void:
	if output.is_empty() or expected_metadata.is_empty() or not output.replace("\\","/").contains("/evidence/phase6/") or DirAccess.dir_exists_absolute(output):
		printerr("Use a new bounded phase6 output directory")
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
	check(executable.contains("/builds/phase6/phase6-candidate-20261030-01/"),"running executable belongs to accepted candidate directory")
	check(not FileAccess.file_exists("res://baseline_sim.gd") and ResourceLoader.exists("res://baseline_sim.gd"),"exported script exists through resource remap without original source text")
	var metadata_hash: String = FileAccess.get_sha256("res://game_data/build_info.json")
	check(metadata_hash == expected_metadata,"PCK embedded metadata matches accepted export")
	var metadata: Variant = JSON.parse_string(FileAccess.get_file_as_string("res://game_data/build_info.json"))
	check(metadata is Dictionary and metadata.get("build_id","") == "phase6-candidate-20261030-01","PCK build identifier")
	normal_progress_before = FileAccess.get_sha256("user://progress-v1.json") if FileAccess.file_exists("user://progress-v1.json") else "absent"
	normal_before = FileAccess.get_sha256("user://equipment-v1.json") if FileAccess.file_exists("user://equipment-v1.json") else "absent"
	var packed: PackedScene = load("res://Baseline.tscn")
	if packed == null:
		check(false,"exported Baseline scene loads")
		finish({},metadata_hash,res_root,{},"")
		return
	view = packed.instantiate()
	view.sim = IsolatedSim.new()
	view.sim.isolated_path = "res://evidence/phase6/exported-qa/"+output.get_base_dir().get_file()+"/"+output.get_file()+"/progress.json"
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
	view.toggle_equipment()
	# Explicit low-HP fixture; cast and death still run through fixed tick combat.
	for kill_index in range(2):
		var state: Dictionary = view.sim.entity(view.sim.spawn_enemy(view.sim.player+Vector2(6,0)))
		state.life_raw = 1
		for step_index in range(240):
			view.sim.step(true,state.p)
			if state.state == "dead": break
		check(state.state == "dead","actual cast creates death reward %d" % kill_index)
	view.sync_actors()
	check(view.sim.progression_snapshot().xp == 6 and view.sim.equipment_context().level == 2,"two real deaths grant six XP and requirement level2")
	check(not view.sim.ground_loot_snapshot().is_empty(),"seeded real deaths produce ground loot")
	check(view.loot_presenter.markers.size() == view.sim.ground_loot_snapshot().size(),"ground visuals project bounded simulation entries")
	view.actor_registry.advance(1.0,view.camera,view.sim.player)
	await capture("frame-loot-level2")
	view.toggle_equipment()
	check(not p.item_buttons[2].disabled and p.context_label.text.contains("경험치 6"),"level2 charm requirement unlocks and XP displays")
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
	var test_save: String = view.sim.isolated_path
	var working_directory: String = DirAccess.open(".").get_current_dir().replace("\\","/")
	var resolved_save: String = working_directory.path_join(ProjectSettings.globalize_path(test_save)).simplify_path()
	check(resolved_save.begins_with(executable.get_base_dir()+"/evidence/phase6/"),"isolated save resolves under candidate phase6 evidence directory")
	check(not FileAccess.file_exists(test_save),"isolated profile save starts absent")
	p.save_button.pressed.emit()
	check(FileAccess.file_exists(test_save),"real save button writes isolated profile")
	var save_sha: String = FileAccess.get_sha256(test_save)
	var saved_progress: Dictionary = view.sim.progress_document()
	var old_handle: Dictionary = view.sim.loot_handle(int(view.sim.ground_loot_snapshot()[0].uid)) if not view.sim.ground_loot_snapshot().is_empty() else {}
	p.slot_buttons.focus.pressed.emit()
	p.slot_buttons.body.pressed.emit()
	check(view.sim.equipment_snapshot().equipped.is_empty() and view.sim.life == 17.0,"unequip without recovery")
	p.load_button.pressed.emit()
	check(view.sim.equipment_snapshot() == equipped.equipment and view.sim.life == 17.0 and view.sim.mana_raw == 1234,"real load button restores exact gear without recovery")
	check(view.sim.progression_snapshot().xp == 6 and view.is_equipment_open() and view.sim.paused,"profile load preserves XP and modal pause")
	check(FileAccess.get_sha256(test_save) == save_sha,"load leaves saved bytes unchanged")
	check(old_handle.is_empty() or not view.sim.pickup_loot(old_handle),"old pre-load ground handle rejected")
	await capture("frame-profile-loaded")
	var loot: Array = view.sim.ground_loot_snapshot()
	if not loot.is_empty():
		var before_items: int = view.sim.equipment_items().size()
		view.sim.player = Vector2(loot[0].p[0],loot[0].p[1])
		view.sim.move_target = view.sim.player
		view.sim.paused = false
		view.sim.step()
		view.sim.paused = true
		check(view.sim.equipment_items().size() > before_items,"fixed tick automatically picks up nearby ground loot")
		view.sync_actors()
		p.refresh()
		await capture("frame-loot-picked-up")
	var before_restart: Dictionary = view.sim.equipment_snapshot()
	view.restart()
	check(view.is_equipment_open() and view.sim.paused and view.sim.equipment_snapshot() == before_restart,"R preserves equipment/UID/RNG and open modal")
	check(view.sim.progression_snapshot().xp == 6 and view.sim.ground_loot_snapshot().is_empty(),"R preserves XP and clears ground rewards")
	check(view.sim.life == 50.0 and view.sim.mana_raw == 8960,"explicit combat reset heals modified maxima")
	await capture("frame-equipment-loaded-reset")
	p.close_button.pressed.emit()
	check(not view.is_equipment_open() and not view.sim.paused,"close restores preceding play state")
	await capture("frame-equipped-play")
	view.toggle_pause()
	view.toggle_equipment()
	view._unhandled_input(key(KEY_ESCAPE))
	check(not view.is_equipment_open() and view.sim.paused and view.pause_cover.visible,"equipment closes back to preceding ordinary pause")
	# Separate synthetic marker-cap fixture, distinct from the two real cast kills.
	view.sim.reset(0)
	view.sync_actors()
	await settled()
	var nodes_before_ground: int = get_node_count()
	for fixture_index in range(192):
		if view.sim.ground_loot_snapshot().size() == 32: break
		var fixture_position: Vector2 = view.sim.player+Vector2(-4+fixture_index%8,-4-int(fixture_index/8)%4)
		var fixture_state: Dictionary = view.sim.entity(view.sim.spawn_enemy(fixture_position))
		fixture_state.state = "dead"
		fixture_state.life_raw = 0
		view.sim.claim_death_reward(view.sim.handle(fixture_state))
		view.sim.despawn_enemy(view.sim.handle(fixture_state))
	view.sim.paused = true
	view.sync_actors()
	check(view.sim.ground_loot_snapshot().size() == 32 and view.loot_presenter.markers.size() == 32,"synthetic full ground32 projects exactly32 markers")
	view.pause_cover.hide()
	await capture("frame-synthetic-ground32")
	check(get_node_count() <= nodes_before_ground+96,"ground32 adds at most three nodes per marker")
	view.sim.tick += 1800
	view.sim.paused = false
	view.sim.step()
	view.sim.paused = true
	view.sync_actors()
	await settled()
	check(view.sim.ground_loot_snapshot().is_empty() and view.loot_presenter.markers.is_empty(),"ground32 expires after TTL and removes markers")
	check(get_node_count() <= nodes_before_ground,"expired ground marker nodes are reclaimed after frame")
	view.sim.reset(0)
	view.sync_actors()
	check(view.loot_presenter.markers.is_empty(),"reset retires all old loot marker handles")
	var final_snapshot: Dictionary = snapshot()
	view.free()
	finish(final_snapshot,metadata_hash,res_root,metadata,test_save)

func finish(state: Dictionary, metadata_hash: String, res_root: String, metadata: Variant, test_save: String) -> void:
	var normal_progress_after: String = FileAccess.get_sha256("user://progress-v1.json") if FileAccess.file_exists("user://progress-v1.json") else "absent"
	check(normal_progress_after == normal_progress_before,"external QA never changes native user progress save")
	var normal_after: String = FileAccess.get_sha256("user://equipment-v1.json") if FileAccess.file_exists("user://equipment-v1.json") else "absent"
	check(normal_after == normal_before,"external QA never changes normal user equipment save")
	var working_directory: String = DirAccess.open(".").get_current_dir().replace("\\","/")
	var save_resolved: String = working_directory.path_join(ProjectSettings.globalize_path(test_save)).simplify_path()
	var report := {"scope":"External SceneTree against exported PCK, direct signals/public methods; distinct from OS input and performance evidence","checks":checks,"failures":failures,"success":failures.is_empty(),"engine":Engine.get_version_info().string,"display_server":DisplayServer.get_name(),"renderer":RenderingServer.get_current_rendering_method(),"metadata_sha256":metadata_hash,"metadata":metadata,"resource_root":res_root,"working_directory":working_directory,"executable":OS.get_executable_path(),"original_source_text_present":FileAccess.file_exists("res://baseline_sim.gd"),"external_script_sha256":FileAccess.get_sha256(get_script().resource_path),"captures":captures,"final":state,"isolated_save_path":save_resolved,"isolated_save_sha256":FileAccess.get_sha256(test_save) if not test_save.is_empty() else "","native_progress_before":normal_progress_before,"native_progress_after":normal_progress_after,"normal_user_save_before":normal_before,"normal_user_save_after":normal_after,"user_data_dir":OS.get_user_data_dir()}
	var file := FileAccess.open(output.path_join("qa-report.json"),FileAccess.WRITE)
	if not file:
		quit(1)
		return
	file.store_string(JSON.stringify(report,"\t"))
	file.flush()
	var saved: bool = file.get_error() == OK
	print(JSON.stringify({"scope":report.scope,"checks":checks,"failures":failures,"success":failures.is_empty() and saved}))
	quit(0 if failures.is_empty() and saved else 1)
