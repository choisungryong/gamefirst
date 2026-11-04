extends SceneTree
## Headless real-scene integration. This does not prove OS input routing or GPU
## appearance; those require the final exported executable and native inspection.
const Sim = preload("res://baseline_sim.gd")
const Catalog = preload("res://data/game_catalog.gd")
var checks := 0
var failures: Array[String] = []

func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("PHASE4 SCENE FAILED: "+message)

func key(code: int) -> InputEventKey:
	var event := InputEventKey.new()
	event.keycode = code
	event.pressed = true
	return event

func pointer(pressed: bool) -> InputEventMouseButton:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_RIGHT
	event.pressed = pressed
	return event

func sample(view: Node) -> Dictionary:
	return {"tick":view.sim.tick,"mana":view.sim.mana_raw,"rng":view.sim.rng.state,"history":view.sim.history.duplicate(true),"enemies":view.sim.enemies.duplicate(true),"pending":view.sim.pending.duplicate(true)}

func unnamed_catalog_scene(packed: PackedScene, historical: bool) -> void:
	var c = Catalog.new()
	check(c.load_file("res://evidence/phase4/reference-phase3/game_data/catalog.json" if historical else "res://game_data/catalog.json"),"optional name catalog source loads historical="+str(historical))
	var document: Dictionary = c.snapshot()
	for definition in document.skills: definition.erase("display_name")
	check(c.replace_document(document),"unnamed definitions remain valid historical="+str(historical))
	var view = packed.instantiate()
	view.sim = Sim.new(c)
	view.sim.reset(0)
	view.initial_enemies = 0
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	check(view.sim.valid_profile and view.skill_buttons.size() == document.skills.size() and not view.skill_buttons[0].text.is_empty(),"real scene initializes optional name catalog historical="+str(historical))
	for index in range(document.skills.size()):
		view.select_skill_index(index)
		view.sync_actors()
		check(not view.cast_status.text.is_empty() and not view.skill_buttons[index].text.is_empty(),"unnamed skill HUD/selector fallback "+str(historical)+"/"+str(index))
	view.sim.step(true,view.sim.player+Vector2.RIGHT)
	view.sync_actors()
	check(view.skill_mode_label.text.contains("시전 중:") and not view.cast_status.text.is_empty(),"unnamed committed-skill HUD fallback historical="+str(historical))
	view.free()

func run() -> void:
	var packed: PackedScene = load("res://Baseline.tscn")
	var view = packed.instantiate()
	view.sim.reset(0)
	view.initial_enemies = 0
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	view.sim.enemy_ai = false
	check(view.skill_buttons.size() == 3 and is_instance_valid(view.auto_button) and is_instance_valid(view.skill_mode_label),"actual scene has three skill selectors and automatic policy UI")
	check(view.sim.selected_skill_id == "skill.ember_bolt" and view.cast_status.text.contains("화염탄") and view.cast_status.text.contains("2.5"),"default HUD derives preserved FireBolt cost")
	view._unhandled_input(key(KEY_2))
	check(view.sim.selected_skill_id == "skill.frost_pulse" and view.cast_status.text.contains("서리 파동") and view.cast_status.text.contains("마나 4"),"key2 selects area and updates live cost/name")
	view._unhandled_input(key(KEY_3))
	check(view.sim.selected_skill_id == "skill.arc_chain" and view.cast_status.text.contains("연쇄 번개") and view.cast_status.text.contains("3.5"),"key3 selects chain and updates live HUD")
	view.sim.replace_player_modifiers([{"source_id":"test","id":"power","stat_id":"stat.spell_power","operation":"add","value":5000},{"source_id":"test","id":"mana","stat_id":"stat.mana","operation":"add","value":256}])
	view.sync_actors()
	check(view.cast_status.text.contains("6–9") and view.mana_label.text.contains("36"),"HUD derives modified raw damage and mana maximum")
	view.sim.replace_player_modifiers([])
	view._unhandled_input(key(KEY_F))
	check(view.input_controller.auto_cast and view.auto_button.text.contains("켜짐"),"F enables visible auto policy")
	view.held = true
	view.queued_cast = true
	view.select_skill_index(1)
	check(view.input_controller.auto_cast and not view.held and not view.queued_cast,"selection preserves auto and clears pointer request")
	view._unhandled_input(key(KEY_ESCAPE))
	check(view.sim.paused and not view.input_controller.auto_cast and view.skill_buttons[1].disabled and view.auto_button.disabled,"pause clears automatic policy and disables skill controls")
	var prior: String = view.sim.selected_skill_id
	view._unhandled_input(key(KEY_1))
	view._unhandled_input(key(KEY_F))
	view.select_skill_index(0)
	check(view.sim.selected_skill_id == prior and not view.input_controller.auto_cast,"paused keyboard and button handlers reject selection/auto")
	view._unhandled_input(key(KEY_ESCAPE))
	view.toggle_auto_cast()
	view.get_window().focus_exited.emit()
	check(not view.input_controller.auto_cast and not view.held and not view.queued_cast,"connected focus loss clears automatic and pointer requests")
	view._input(pointer(true))
	check(not view.held and not view.queued_cast,"global GUI-routed press alone cannot create gameplay request")
	view._unhandled_input(pointer(true))
	view._input(pointer(false))
	check(not view.held and view.queued_cast,"unhandled press plus global release preserves one quick click")
	view._physics_process(Sim.STEP)
	check(not view.sim.pending.is_empty() and view.sim.pending_skill_id() == "skill.frost_pulse" and view.sim.mana_raw == 7936,"quick click uses selected skill and same paid core path")
	view._unhandled_input(key(KEY_3))
	check(view.skill_mode_label.text.contains("시전 중: 서리 파동"),"HUD differentiates selected and already committed skill")
	view.restart()
	check(view.sim.selected_skill_id == "skill.ember_bolt" and not view.input_controller.auto_cast and view.sim.pending.is_empty(),"restart restores default skill and clears requests/pending")

	# Resolve actual core area release, then feed its events through view handlers.
	view.sim.player = Vector2.ZERO
	view.sim.move_target = Vector2.ZERO
	var handle: Dictionary = view.sim.spawn_enemy(Vector2(2,0))
	view.sim.entity(handle).life_raw = 100000
	var before_state: Dictionary = {}
	for i in range(19):
		view.sim.step(i == 0,Vector2.RIGHT,"skill.frost_pulse")
		before_state = sample(view)
		for event in view.sim.events: view.handle_event(event)
		check(sample(view) == before_state,"view event handling cannot mutate combat or RNG tick "+str(i))
	view.sync_actors()
	var fx = view.effect_presenter.skill_effects
	check(fx.active.size() == 1 and fx.statuses.size() == 1 and fx.created == 2,"real area event creates bounded ring and chill visual")
	var status_key: String = "%d:%d" % [handle.id,handle.generation]
	check(fx.statuses.has(status_key) and fx.statuses[status_key].until_tick == view.sim.status_snapshot(handle).until_tick,"chill visual uses exact logical handle and expiry")
	var life: float = fx.active[0].life
	var tick_before: int = view.sim.tick
	view.toggle_pause()
	view._process(.5)
	view._physics_process(.5)
	check(fx.active[0].life == life and view.sim.tick == tick_before,"pause freezes new FX clock and core")
	view.toggle_pause()
	view.effect_presenter.advance(.1)
	check(fx.active[0].life < life,"new FX advances after resume")
	view.sim.entity(handle).p = Vector2(3,1)
	view.sync_actors()
	check(fx.statuses[status_key].node.position == Vector3(3,.07,1),"chill visual follows logical target position")
	view.sim.despawn_enemy(handle)
	view.sync_actors()
	check(fx.statuses.is_empty(),"despawn sync clears stale chill visual")
	var replacement: Dictionary = view.sim.spawn_enemy(Vector2(3,1))
	view.sync_actors()
	check(replacement.id == handle.id and replacement.generation > handle.generation and fx.statuses.is_empty(),"new generation cannot inherit old visual status")
	var ring_event: Dictionary = {"kind":"skill_effect","effect_kind":"area","origin":[0,0],"radius_world":4.0,"points":[],"targets":[]}
	for i in range(100): fx.handle_event(ring_event)
	check(fx.created == fx.MAX_NODES and fx.active.size()+fx.statuses.size() <= fx.MAX_NODES and fx.dropped > 0,"FX allocation cap drops excess without growing nodes")
	var nodes: Array = []
	for visual in fx.active: nodes.append(visual.node)
	view.restart()
	var hidden := true
	for node in nodes: hidden = hidden and not node.visible and node.transform == Transform3D.IDENTITY
	check(fx.active.is_empty() and fx.statuses.is_empty() and fx.pool.size() == fx.created and hidden,"reset retires every new FX into identity hidden pool")
	var created_before: int = fx.created
	fx.handle_event({"kind":"skill_effect","effect_kind":"chain","origin":[0,0],"points":[[0,0],[1,0],[1,2]],"targets":[]})
	check(fx.created == created_before and fx.reused >= 2 and fx.active.size() == 2,"chain beam reuses shared bounded node pool")
	var beam: MeshInstance3D = fx.active[0].node
	check(beam.mesh == fx.beam_mesh and beam.material_override == fx.chain_material and is_equal_approx(beam.scale.y,1.0),"pooled area-to-chain reuse resets mesh/material/transform")
	var state_before: Dictionary = sample(view)
	for i in range(40):
		view.burst(Vector3.ZERO,Color.BLUE,100,.1)
		fx.handle_event(ring_event)
		view.effect_presenter.advance(.02)
		view.effect_presenter.sync(view.sim,view.camera,view.atlas)
	check(sample(view) == state_before,"heavy altered FX sequence leaves damage RNG and combat state unchanged")
	view.free()
	unnamed_catalog_scene(packed,false)
	unnamed_catalog_scene(packed,true)
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional scene harness failure proof")
	print(JSON.stringify({"scope":"Phase4 real scene headless contracts; not GPU appearance or OS GUI routing","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
