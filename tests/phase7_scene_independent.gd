extends SceneTree
## Actual expedition scene signals/input; storage is isolated before tree entry.
const Run = preload("res://run/expedition_controller.gd")
class IsolatedSim:
	extends "res://baseline_sim.gd"
	var test_path := ""
	func save_progress(_path: String = "user://progress-v1.json") -> bool: return super.save_progress(test_path)
	func load_progress(_path: String = "user://progress-v1.json") -> bool: return super.load_progress(test_path)
var checks := 0
var failures: Array[String] = []
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("PHASE7 SCENE FAILED: "+message)
func key(code: int) -> InputEventKey:
	var e := InputEventKey.new()
	e.keycode = code
	e.pressed = true
	return e
func settled() -> void:
	await process_frame
	await process_frame
func snap(view: Node) -> Dictionary:
	return {"run":view.controller.snapshot(),"profile":view.sim.progress_document(),"life":view.sim.life,"mana":view.sim.mana_raw,"tick":view.sim.tick,"damage_rng":str(view.sim.rng.state),"spawn_rng":str(view.controller.spawn_rng.state)}
func kill(view: Node) -> void:
	var id_: Dictionary = view.sim.spawn_enemy(Vector2(6,-5))
	view.sim.entity(id_).life_raw = 1
	var context: Dictionary = view.sim._make_context("skill.ember_bolt")
	context["shot"] = 1
	view.sim._apply_damage(view.sim.entity(id_),context,Vector2(6,-5))
func run() -> void:
	var folder := "res://evidence/phase7/verification/scene-"+str(OS.get_process_id())+"-"+str(Time.get_ticks_usec())
	check(DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(folder)) == OK,"isolated scene save directory")
	var normal_equipment := "user://equipment-v1.json"
	var normal_progress := "user://progress-v1.json"
	var equipment_before := FileAccess.get_sha256(normal_equipment) if FileAccess.file_exists(normal_equipment) else "absent"
	var progress_before := FileAccess.get_sha256(normal_progress) if FileAccess.file_exists(normal_progress) else "absent"
	var packed: PackedScene = load("res://Expedition.tscn")
	check(packed != null,"expedition scene imports")
	if packed == null:
		print(JSON.stringify({"checks":checks,"failures":failures,"success":false}))
		quit(1)
		return
	var view = packed.instantiate()
	var isolated = IsolatedSim.new()
	isolated.test_path = folder+"/progress.json"
	view.sim = isolated
	view.controller = Run.new(isolated)
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	await settled()
	check(view.controller.state == "ready" and view.sim.paused and view.hud.overlay.visible,"actual scene starts at frozen menu")
	check(view.hud.start_button.visible and view.hud.load_button.visible and not view.hud.retry_button.visible,"menu exposes start/load actions")
	var before: Dictionary = snap(view)
	view._physics_process(1.0/60.0)
	check(snap(view) == before,"menu input loop does not run combat")
	view.hud.start_button.pressed.emit()
	check(view.controller.state == "active" and not view.sim.paused and not view.hud.overlay.visible,"real start signal begins active expedition")
	check(view.sim.alive_count() == 1 and view.hud.timer.text == "00:00","start HUD and initial enemy agree")
	for index in range(3):
		view.hud.skill_buttons[index].pressed.emit()
		check(view.sim.selected_skill_id == view.sim.available_skill_ids()[index],"actual skill button selects skill "+str(index))
	view.hud.auto_button.pressed.emit()
	check(view.input_controller.auto_cast,"actual automatic policy button toggles")
	view._unhandled_input(key(KEY_I))
	check(view.is_equipment_open() and view.sim.paused and view.controller.paused and not view.input_controller.auto_cast,"I modal freezes run/combat and clears auto input")
	before = snap(view)
	for i in range(20): view._physics_process(1.0/60.0)
	for code in [KEY_F,KEY_1,KEY_2,KEY_3]: view._unhandled_input(key(code))
	check(snap(view) == before,"modal blocks ticking/regen/spawn/combat policy changes")
	view.sim.life = 17
	view.sim.mana_raw = 1234
	var p = view.equipment_presenter
	p.item_buttons[1].pressed.emit()
	check(view.sim.life == 17 and view.sim.life_max_raw == 12800 and view.sim.mana_raw == 1234,"modal robe changes maximum without healing")
	kill(view)
	kill(view)
	p.refresh()
	check(view.sim.progression_snapshot().xp == 6 and not p.item_buttons[2].disabled,"actual modal reflects level2 unlock")
	p.save_button.pressed.emit()
	check(FileAccess.file_exists(isolated.test_path) and JSON.parse_string(FileAccess.get_file_as_string(isolated.test_path)).xp == 6,"actual modal save uses isolated complete profile")
	p.slot_buttons.body.pressed.emit()
	view.controller.elapsed_ticks = 1000
	p.load_button.pressed.emit()
	check(view.controller.elapsed_ticks == 0 and view.controller.state == "active" and view.sim.paused and view.controller.paused and view.is_equipment_open(),"modal profile load resets run clock and preserves modal pause")
	check(view.sim.life == 17 and view.sim.life_max_raw == 12800 and view.sim.mana_raw == 1234 and view.sim.progression_snapshot().xp == 6,"modal full-profile load preserves absolute vitals and XP")
	var good: String = isolated.test_path
	isolated.test_path = folder+"/broken.json"
	var f := FileAccess.open(isolated.test_path,FileAccess.WRITE)
	f.store_string("{broken")
	f.close()
	before = snap(view)
	p.load_button.pressed.emit()
	check(snap(view) == before and p.notice_label.text.contains("현재 상태는 유지"),"failed modal load preserves controller and sim")
	isolated.test_path = good
	view._unhandled_input(key(KEY_ESCAPE))
	check(not view.is_equipment_open() and not view.sim.paused and not view.controller.paused,"closing modal restores active play")
	view._unhandled_input(key(KEY_ESCAPE))
	check(view.controller.paused and view.hud.pause_label.visible,"Esc pauses expedition")
	view._unhandled_input(key(KEY_I))
	view._unhandled_input(key(KEY_ESCAPE))
	check(view.controller.paused and view.sim.paused and view.hud.pause_label.visible,"modal opened from pause restores previous pause")
	view._unhandled_input(key(KEY_ESCAPE))
	view._unhandled_input(key(KEY_I))
	view.focus_lost()
	view._unhandled_input(key(KEY_ESCAPE))
	check(view.controller.paused and view.sim.paused,"focus loss inside modal survives closing")
	view._unhandled_input(key(KEY_ESCAPE))
	view.hud.mute_button.pressed.emit()
	check(view.muted,"mute signal reaches view")
	view.hud.mute_button.pressed.emit()
	check(not view.muted,"mute signal toggles back")
	view.controller.elapsed_ticks = 14399
	view.controller.elite_spawned = true
	view.controller.elite_defeated = true
	view.controller.step()
	view.sync_equipment_hud()
	check(view.controller.state == "victory" and view.hud.overlay.visible and view.hud.retry_button.visible and view.hud.menu_button.visible,"actual terminal overlay exposes retry/menu")
	view.sim.life = 1
	view.sim.mana_raw = 1
	view.hud.retry_button.pressed.emit()
	check(view.controller.state == "active" and view.controller.elapsed_ticks == 0 and view.sim.life == 50 and view.sim.mana_raw == 8960,"actual retry starts fresh explicit recovered combat")
	check(view.sim.progression_snapshot().xp == 6,"retry retains metaXP")
	view.start_menu()
	view.sim.life = 11
	view.sim.mana_raw = 333
	view.hud.load_button.pressed.emit()
	check(view.controller.state == "active" and view.controller.elapsed_ticks == 0 and view.sim.life == 11 and view.sim.mana_raw == 333,"menu load begins fresh run without recovery")
	for size in [Vector2i(1440,810),Vector2i(1920,1080)]:
		root.size = size
		await settled()
		for button in view.hud.skill_buttons:
			check(view.hud.root.get_global_rect().encloses(button.get_global_rect()),"skill action fits actual viewport "+str(size))
		check(view.hud.root.get_global_rect().encloses(view.hud.auto_button.get_global_rect()),"auto action fits viewport "+str(size))
	view.free()
	await settled()
	var equipment_after := FileAccess.get_sha256(normal_equipment) if FileAccess.file_exists(normal_equipment) else "absent"
	var progress_after := FileAccess.get_sha256(normal_progress) if FileAccess.file_exists(normal_progress) else "absent"
	check(equipment_before == equipment_after and progress_before == progress_after,"actual scene tests preserve both user save paths")
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional phase7 scene harness failure proof")
	print(JSON.stringify({"scope":"Actual expedition SceneTree signal/input/profile/modal/layout checks; no OS/GPU/art/fun claim","checks":checks,"failures":failures,"success":failures.is_empty(),"isolated_storage":folder}))
	quit(0 if failures.is_empty() else 1)
