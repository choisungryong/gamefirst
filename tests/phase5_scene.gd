extends SceneTree
## Actual Baseline tree with isolated save path injection. This tests GUI signal
## routing/layout state, not OS input injection or GPU appearance.
const Sim = preload("res://baseline_sim.gd")
const Catalog = preload("res://data/game_catalog.gd")
const Storage = preload("res://data/equipment_storage.gd")
class IsolatedSim:
	extends "res://baseline_sim.gd"
	var test_save_path := ""
	func save_equipment(_path: String = "user://equipment-v1.json") -> bool:
		return super.save_equipment(test_save_path)
	func load_equipment(_path: String = "user://equipment-v1.json") -> bool:
		return super.load_equipment(test_save_path)

var checks := 0
var failures: Array[String] = []
var save_directory := ""

func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("PHASE5 SCENE FAILED: "+message)

func key(code: int) -> InputEventKey:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	return event

func pointer(pressed: bool) -> InputEventMouseButton:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_RIGHT
	event.pressed = pressed
	event.position = Vector2(400,400)
	return event

func settled() -> void:
	await process_frame
	await process_frame

func panel_layout(view: Node, label_: String) -> void:
	var p = view.equipment_presenter
	check(p.panel.get_global_rect().encloses(p.card.get_global_rect()),"equipment card fits requested viewport "+label_)
	check(view.auto_button.get_global_rect().end.y <= view.skill_mode_label.get_global_rect().position.y,"automatic policy button and mode label do not overlap "+label_)
	check(p.card.get_global_rect().encloses(p.close_button.get_global_rect()) and p.card.get_global_rect().encloses(p.save_button.get_global_rect()) and p.card.get_global_rect().encloses(p.load_button.get_global_rect()),"modal actions remain within card "+label_)

func unit_labels(packed: PackedScene) -> void:
	var c = Catalog.new()
	check(c.load_file(),"unit label fixture catalog loads")
	var document: Dictionary = c.snapshot()
	var provenance := {"status":"design_choice","method":"project_design","note":"Independent UI unit fixture"}
	document.stats.append({"id":"stat.extra_health","unit":"health","scale":256,"minimum_raw":0,"maximum_raw":2147483647,"default_raw":0,"provenance":provenance})
	document.stats.append({"id":"stat.extra_count","unit":"count","scale":1,"minimum_raw":0,"maximum_raw":20,"default_raw":0,"provenance":provenance})
	check(c.replace_document(document),"valid additional unnamed health/count definitions")
	var v = packed.instantiate()
	v.sim = Sim.new(c)
	v.sim.reset(0)
	v.initial_enemies = 0
	root.add_child(v)
	v.set_process(false)
	v.set_physics_process(false)
	var presenter = v.equipment_presenter
	var health: String = presenter.modifier_text({"stat_id":"stat.extra_health","operation":"add","value":384})
	var count_: String = presenter.modifier_text({"stat_id":"stat.extra_count","operation":"add","value":3})
	check(health.contains("1.5") and not health.contains("%"),"unnamed valid health stat displays scale256 quantity without percent")
	check(count_.ends_with("+3") and not count_.contains("%"),"unnamed count stat displays integral scale1 without percent")
	var percent: String = presenter.modifier_text({"stat_id":"stat.health","operation":"percent_bps","value":1000})
	check(percent.contains("+10%"),"percent operation takes precedence over health raw scale")
	check(presenter.modifier_text({"stat_id":"stat.health","operation":"add","value":-384}).contains("-1.5"),"negative raw health displays correct quantity")
	check(presenter.modifier_text({"stat_id":"stat.spell_power","operation":"add","value":500}).contains("+5%"),"basis-point unit addition displays percent")
	v.free()

func run() -> void:
	var normal_before: String = FileAccess.get_sha256(Storage.PATH) if FileAccess.file_exists(Storage.PATH) else "absent"
	save_directory = "res://evidence/phase5/verification/scene-storage-"+str(OS.get_process_id())+"-"+str(Time.get_ticks_usec())
	check(DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(save_directory)) == OK,"isolated GUI save directory created")
	var packed: PackedScene = load("res://Baseline.tscn")
	var view = packed.instantiate()
	var isolated = IsolatedSim.new()
	isolated.test_save_path = save_directory+"/gui.json"
	isolated.reset(0)
	view.sim = isolated
	view.initial_enemies = 0
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	await settled()
	check(view.sim.equipment_valid and not view.is_equipment_open() and not view.sim.paused,"actual scene starts playable with equipment available")
	view._unhandled_input(key(KEY_F))
	view.held = true
	view.queued_cast = true
	view._unhandled_input(key(KEY_I))
	var p = view.equipment_presenter
	check(view.is_equipment_open() and view.sim.paused and not view.pause_cover.visible,"I opens modal and pauses without ordinary pause cover")
	check(not view.input_controller.auto_cast and not view.held and not view.queued_cast,"opening clears automatic and held/queued pointer input")
	check(p.item_buttons.size() == 3 and p.slot_buttons.size() == 3 and not p.save_button.disabled and not p.load_button.disabled,"real modal exposes three items/slots and storage buttons")
	check(p.item_buttons[2].disabled and p.context_label.text.contains("레벨 1"),"level2 charm visibly blocked for base level1")
	var selected: String = view.sim.selected_skill_id
	var tick_before: int = view.sim.tick
	for code in [KEY_F,KEY_1,KEY_2,KEY_3,KEY_TAB]: view._unhandled_input(key(code))
	view._unhandled_input(pointer(true))
	view._input(pointer(false))
	view._physics_process(Sim.STEP)
	check(view.sim.selected_skill_id == selected and not view.input_controller.auto_cast and not view.held and not view.queued_cast and not view.comparison.visible and view.sim.tick == tick_before,"modal blocks combat hotkeys/pointer/Tab and fixed tick")
	view.sim.life = 17
	view.sim.mana_raw = 1234
	p.item_buttons[0].pressed.emit()
	check(view.sim.equipment_snapshot().equipped == {"focus":1} and view.cast_status.text.contains("Lv.2"),"actual item button equips and refreshes effective skill HUD")
	check(view.sim.life == 17 and view.sim.mana_raw == 1234,"GUI equipment action grants no healing")
	var equipment_before: Dictionary = view.sim.equipment_snapshot()
	p.item_buttons[2].pressed.emit()
	check(view.sim.equipment_snapshot() == equipment_before and p.notice_label.text.contains("장착할 수 없습니다"),"direct disabled-button signal still fails at authoritative requirements")
	p.slot_buttons.focus.pressed.emit()
	check(view.sim.equipment_snapshot().equipped.is_empty() and view.cast_status.text.contains("Lv.1"),"slot button unequips and refreshes baseline level")
	p.save_button.pressed.emit()
	check(FileAccess.file_exists(isolated.test_save_path) and p.notice_label.text.contains("저장했습니다"),"storage button routes through simulation to isolated save")
	p.item_buttons[1].pressed.emit()
	check(view.sim.life_max_raw == 12800 and view.sim.life == 17,"robe GUI changes maximum without recovery")
	p.load_button.pressed.emit()
	check(view.sim.equipment_snapshot().equipped.is_empty() and view.sim.life_max_raw == 10240 and view.sim.life == 17 and p.notice_label.text.contains("불러왔습니다"),"load button restores gear only without healing")
	var good_path: String = isolated.test_save_path
	isolated.test_save_path = save_directory+"/malformed.json"
	var fixture := FileAccess.open(isolated.test_save_path,FileAccess.WRITE)
	fixture.store_string("{bad")
	fixture.close()
	equipment_before = view.sim.equipment_snapshot()
	p.load_button.pressed.emit()
	check(view.sim.equipment_snapshot() == equipment_before and p.notice_label.text.contains("현재 장비는 유지"),"failed GUI load preserves state with plain-language notice")
	isolated.test_save_path = good_path
	view.get_window().focus_exited.emit()
	check(view.is_equipment_open() and view.sim.paused and not view.held and not view.input_controller.auto_cast,"focus loss keeps modal paused and clears requests")
	view._unhandled_input(key(KEY_ESCAPE))
	check(not view.is_equipment_open() and not view.sim.paused and not view.pause_cover.visible,"Esc closes only equipment and restores previous playing state")
	view.toggle_pause()
	check(view.sim.paused and view.pause_cover.visible,"ordinary pause is separate")
	view.toggle_equipment()
	check(view.is_equipment_open() and view.sim.paused and not view.pause_cover.visible,"equipment can open from paused state")
	view._unhandled_input(key(KEY_I))
	check(not view.is_equipment_open() and view.sim.paused and view.pause_cover.visible,"I closing preserves previously paused state")
	view.toggle_pause()
	view.comparison.show()
	view.equipment_button.pressed.emit()
	check(view.is_equipment_open() and not view.comparison.visible,"equipment button opens modal and hides comparison panel")
	p.item_buttons[0].pressed.emit()
	p.item_buttons[1].pressed.emit()
	equipment_before = view.sim.equipment_snapshot()
	view.sim.life = 3
	view.sim.mana_raw = 1
	view._unhandled_input(key(KEY_R))
	check(view.is_equipment_open() and view.sim.paused and not view.pause_cover.visible and view.sim.equipment_snapshot() == equipment_before,"R retains modal and exact inventory/UID/RNG/equipment")
	check(view.sim.life == 50 and view.sim.mana_raw == 8960 and view.cast_status.text.contains("Lv.2"),"explicit R restores modified combat maxima and equipped skill HUD")
	for dimensions in [Vector2i(1440,810),Vector2i(1920,1080)]:
		root.size = dimensions
		await settled()
		panel_layout(view,str(dimensions))
	while view.sim.equipment_inventory.items_snapshot().size() < 64:
		view.sim.equipment_inventory.create_item("item.ember_focus")
	p.refresh()
	await settled()
	check(p.item_buttons.size() == 64,"bounded64 inventory is represented inside modal")
	var scroll: ScrollContainer = p.card.find_child("EquipmentItemsScroll",true,false)
	check(scroll != null and p.items_box.size.y > scroll.size.y and scroll.get_v_scroll_bar().max_value > scroll.size.y,"long inventory scrolls rather than expanding card")
	panel_layout(view,"64 items")
	p.close_button.pressed.emit()
	check(not view.is_equipment_open() and not view.sim.paused,"close button restores play after modal reset")
	view._input(pointer(true))
	check(not view.held and not view.queued_cast,"GUI-handled pointer press cannot become combat request")
	view.free()
	await settled()
	unit_labels(packed)
	var historical = Catalog.new()
	check(historical.load_file("res://evidence/phase4/reference-phase3/game_data/catalog.json"),"historical unnamed catalog source loads")
	var old_doc: Dictionary = historical.snapshot()
	for skill in old_doc.skills: skill.erase("display_name")
	check(historical.replace_document(old_doc),"historical no-name v1 remains valid")
	var old_view = packed.instantiate()
	old_view.sim = Sim.new(historical)
	old_view.sim.reset(0)
	old_view.initial_enemies = 0
	root.add_child(old_view)
	old_view.set_process(false)
	old_view.set_physics_process(false)
	await settled()
	old_view.toggle_equipment()
	check(old_view.is_equipment_open() and old_view.equipment_presenter.item_buttons.is_empty() and old_view.equipment_presenter.save_button.disabled and old_view.equipment_presenter.load_button.disabled,"v1 scene presents unavailable equipment safely")
	old_view.toggle_equipment()
	check(not old_view.cast_status.text.is_empty() and not old_view.sim.paused,"v1 combat HUD survives equipment modal")
	old_view.free()
	var normal_after: String = FileAccess.get_sha256(Storage.PATH) if FileAccess.file_exists(Storage.PATH) else "absent"
	check(normal_after == normal_before,"GUI tests never modify normal user equipment save")
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional scene harness failure proof")
	print(JSON.stringify({"scope":"Independent actual scene modal/signal/layout contracts; no OS/GPU appearance claim","checks":checks,"failures":failures,"success":failures.is_empty(),"user_data_dir":OS.get_user_data_dir(),"normal_save_state":normal_after,"test_storage":save_directory}))
	quit(0 if failures.is_empty() else 1)
