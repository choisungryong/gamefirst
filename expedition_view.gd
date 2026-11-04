extends Node3D
## Expedition glue only. RunController owns time, scheduling, resources/outcomes;
## Sim owns combat/rewards. Presenters receive snapshots and never decide damage.
const Simulation = preload("res://baseline_sim.gd")
const Controller = preload("res://run/expedition_controller.gd")
const InputController = preload("res://presentation/input_controller.gd")
const ActorRegistry = preload("res://presentation/actor_registry.gd")
const SkinnedMeshBatch = preload("res://presentation/skinned_mesh_batch.gd")
var skinned_mesh_batch = SkinnedMeshBatch.new()
const EquipmentPresenter = preload("res://presentation/equipment_presenter.gd")
const ExpeditionWorld = preload("res://presentation/expedition_world.gd")
const ExpeditionHUD = preload("res://presentation/expedition_hud.gd")
const ExpeditionEffects = preload("res://presentation/expedition_effects.gd")
const ExpeditionAudio = preload("res://presentation/expedition_audio.gd")
const ExpeditionLoot = preload("res://presentation/expedition_loot.gd")
var sim = Simulation.new()
var controller = Controller.new(sim)
var input_controller = InputController.new()
var actor_registry = ActorRegistry.new()
var equipment_presenter = EquipmentPresenter.new()
var world_presenter = ExpeditionWorld.new()
var hud = ExpeditionHUD.new()
var effects = ExpeditionEffects.new()
var audio = ExpeditionAudio.new()
var loot = ExpeditionLoot.new()
var camera: Camera3D
var hero: Node3D
var enemy_actor: Node3D
var world: Node3D
var tinted_materials: Dictionary = {}
var aim := Vector2.ZERO
var equipment_previous_paused := false
var last_hero_state := ""
var hero_hurt_ticks := 0
var muted := false
var age := 0.0
var _qa_quit_after := -1.0

func _ready() -> void:
	if not sim.valid_profile:
		get_tree().quit(1)
		return
	world_presenter.setup(self)
	hud.setup(self)
	hud.connect("start",start_run)
	hud.connect("retry",restart)
	hud.connect("load",load_run)
	hud.connect("menu",start_menu)
	hud.connect("equipment",toggle_equipment)
	hud.connect("skill",select_skill_index)
	hud.connect("auto",toggle_auto_cast)
	hud.connect("mute",toggle_mute)
	hud.connect("volume",audio.set_master_volume)
	equipment_presenter.setup(self,hud.root)
	equipment_presenter.load_button.tooltip_text = "성장 기록을 불러오면 원정 시간이 00:00인 새 원정을 시작합니다. 현재 생명과 마나는 유지됩니다."
	effects.setup(self)
	audio.setup(self)
	loot.setup(self)
	get_window().focus_exited.connect(focus_lost)
	var should_start := false
	var auto := false
	for argument in OS.get_cmdline_user_args():
		if argument == "--expedition-start": should_start = true
		elif argument == "--auto-skill": auto = true
		elif argument.begins_with("--expedition-quit-after="): _qa_quit_after = float(argument.trim_prefix("--expedition-quit-after="))
	if should_start:
		start_run()
		input_controller.auto_cast = auto
	sync_actors()
	apply_pause_visuals()
	sync_equipment_hud()
	print("EXPEDITION_READY: fixed-tick run; independent effects; KayKit prototype actors")

func material(color: Color, glow: float = 0.0) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color = color
	mat.roughness = .9
	if glow > 0:
		mat.emission_enabled = true
		mat.emission = color
		mat.emission_energy_multiplier = glow
	return mat

func add_mesh(mesh: Mesh, at: Vector3, mat: Material, parent: Node3D = null) -> MeshInstance3D:
	var n := MeshInstance3D.new()
	n.mesh = mesh
	n.material_override = mat
	n.position = at
	(parent if parent else self).add_child(n)
	return n

func load_model(path: String, at: Vector3, parent: Node3D = null) -> Node3D:
	var scene: PackedScene = load(path)
	var node: Node3D = scene.instantiate()
	(parent if parent else self).add_child(node)
	node.position = at
	var ap: AnimationPlayer = find_animation(node)
	if ap:
		var names: Dictionary = {}
		for clip in ap.get_animation_list():
			var short_name: String = String(clip).get_file()
			names[short_name] = clip
			if short_name in ["Idle","Walking_A","Running_A"]:
				ap.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
		node.set_meta("animations", names)
		node.set_meta("player", ap)
	return node

func find_animation(node: Node) -> AnimationPlayer:
	if node is AnimationPlayer: return node
	for child in node.get_children():
		var found: AnimationPlayer = find_animation(child)
		if found: return found
	return null

func animate(node: Node3D, clip: String, speed: float = 1.0, force: bool = false, blend: float = .06) -> void:
	var ap: AnimationPlayer = node.get_meta("player",null)
	var names: Dictionary = node.get_meta("animations",{})
	if not ap or not names.has(clip):
		push_error("Required animation missing: "+clip)
		return
	if force or ap.current_animation != names[clip]:
		if force: ap.stop()
		ap.play(names[clip], blend, speed)
		ap.advance(0)

func tint_model(node: Node, tint: Color) -> void:
	if node is MeshInstance3D:
		for surface in range(node.mesh.get_surface_count()):
			var original: Material = node.get_active_material(surface)
			if original is StandardMaterial3D:
				var signature: String = str(original.get_instance_id())+":"+tint.to_html()
				if not tinted_materials.has(signature):
					var mat: StandardMaterial3D = original.duplicate()
					mat.albedo_color *= tint
					tinted_materials[signature] = mat
				node.set_surface_override_material(surface,tinted_materials[signature])
	for child in node.get_children(): tint_model(child,tint)
	# Imported proxy pieces have no leaf animation tracks. Preserve the complete
	# Skeleton3D and Skin; merge only the proven-compatible material groups.
	if node is Node3D and node.has_meta("animations") and not OS.get_cmdline_user_args().has("--unmerged-actors"):
		node.set_meta("mesh_batch",skinned_mesh_batch.merge(node))

func label(text: String, size: int, color: Color = Color("e4e3d8")) -> Label:
	var n := Label.new()
	n.text = text
	n.add_theme_font_size_override("font_size",size)
	n.add_theme_color_override("font_color",color)
	return n

func style(bg: Color, border: Color = Color(0,0,0,0)) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = border
	s.set_border_width_all(1 if border.a>0 else 0)
	s.set_content_margin_all(20)
	return s

func bar_style(color: Color) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = color
	s.set_content_margin_all(0)
	return s

func button(text: String, action: Callable) -> Button:
	var n := Button.new()
	n.text = text
	n.custom_minimum_size.y = 40
	var normal := style(Color(.10,.15,.14,.92),Color("5c6b5f"))
	var hover := style(Color(.20,.27,.23,.95),Color("a8b2a2"))
	for button_style in [normal,hover]:
		button_style.content_margin_top = 8
		button_style.content_margin_bottom = 8
		button_style.content_margin_left = 14
		button_style.content_margin_right = 14
	n.add_theme_stylebox_override("normal",normal)
	n.add_theme_stylebox_override("hover",hover)
	n.pressed.connect(action)
	return n

func quantity_text(value: float) -> String:
	return str(roundf(value*100)/100.0)

func _reset_presentation() -> void:
	actor_registry.reset()
	effects.reset()
	audio.reset()
	loot.reset()
	input_controller.clear()
	last_hero_state = ""
	hero_hurt_ticks = 0
	var animation: AnimationPlayer = hero.get_meta("player",null)
	if animation: animation.stop()
	sync_actors()
	apply_pause_visuals()
	sync_equipment_hud()

func start_run() -> void:
	if is_equipment_open(): equipment_presenter.close()
	if controller.start(): _reset_presentation()

func restart() -> void:
	if is_equipment_open(): equipment_presenter.close()
	if controller.restart(): _reset_presentation()

func start_menu() -> void:
	if is_equipment_open(): equipment_presenter.close()
	controller.return_to_menu()
	input_controller.clear()
	apply_pause_visuals()
	sync_equipment_hud()

func load_run() -> void:
	if controller.load_profile(): _reset_presentation()
	elif hud.has_method("show_notice"): hud.show_notice("기록을 불러오지 못했습니다. 현재 상태는 유지됩니다.")

func progress_loaded() -> void:
	# Shared equipment modal has already committed the profile. No second reset.
	controller.adopt_loaded_profile()
	_reset_presentation()
	if is_equipment_open():
		controller.set_paused(true)
		apply_pause_visuals()
	sync_equipment_hud()

func equipment_action_completed(action: String,success: bool) -> void:
	if not success: return
	if action in ["equip","unequip"]:
		audio.play_ui("equip",sim.tick)
	elif action == "load":
		equipment_presenter.notice_label.text = "성장 기록으로 새 원정을 시작했습니다 (00:00). 현재 생명과 마나는 유지됩니다."

func is_equipment_open() -> bool:
	return equipment_presenter.is_open()

func toggle_equipment() -> void:
	input_controller.clear()
	if is_equipment_open():
		equipment_presenter.close()
		if controller.state == "active": controller.set_paused(equipment_previous_paused)
	else:
		equipment_previous_paused = controller.paused
		equipment_presenter.open()
		controller.set_paused(true)
	apply_pause_visuals()
	sync_equipment_hud()

func select_skill_index(index: int) -> void:
	if controller.state != "active" or sim.paused or is_equipment_open(): return
	var ids: Array = sim.available_skill_ids()
	if index >= 0 and index < ids.size() and sim.select_skill(ids[index]):
		input_controller.clear_pointer()
		sync_equipment_hud()

func toggle_auto_cast() -> void:
	if controller.state != "active" or sim.paused or is_equipment_open(): return
	input_controller.toggle_auto()
	sync_equipment_hud()

func toggle_mute() -> void:
	muted = not muted
	audio.set_muted(muted)
	hud.set_muted(muted)
	sync_equipment_hud()

func toggle_pause() -> void:
	if is_equipment_open():
		toggle_equipment()
		return
	if controller.state != "active": return
	controller.set_paused(not controller.paused)
	input_controller.clear()
	apply_pause_visuals()
	sync_equipment_hud()

func apply_pause_visuals() -> void:
	var freeze: bool = sim.paused or is_equipment_open()
	actor_registry.set_paused(freeze)
	if hero:
		var animation: AnimationPlayer = hero.get_meta("player",null)
		if animation: animation.speed_scale = 0.0 if freeze else 1.0
	audio.set_paused(freeze)

func focus_lost() -> void:
	input_controller.clear()
	if controller.state == "active":
		# Focus loss while a modal is open must survive that modal closing.
		if is_equipment_open(): equipment_previous_paused = true
		controller.set_paused(true)
		apply_pause_visuals()
		sync_equipment_hud()

func _input(event: InputEvent) -> void:
	input_controller.global_input(event)

func _unhandled_input(event: InputEvent) -> void:
	if is_equipment_open():
		if event is InputEventKey and event.pressed and not event.echo:
			if event.keycode in [KEY_I,KEY_ESCAPE]: toggle_equipment()
			elif event.keycode == KEY_R: restart()
		get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_R: restart()
		elif event.keycode == KEY_I: toggle_equipment()
		elif event.keycode == KEY_ESCAPE: toggle_pause()
		elif event.keycode == KEY_M: toggle_mute()
		elif not sim.paused:
			if event.keycode == KEY_1: select_skill_index(0)
			elif event.keycode == KEY_2: select_skill_index(1)
			elif event.keycode == KEY_3: select_skill_index(2)
			elif event.keycode == KEY_F: toggle_auto_cast()
	if controller.state != "active" or sim.paused: return
	input_controller.unhandled(event)
	var destination: Variant = input_controller.destination_request(event,camera)
	if destination is Vector3: sim.set_destination(Vector2(destination.x,destination.z))

func _physics_process(_delta: float) -> void:
	if controller.state != "active" or sim.paused: return
	var point: Variant = InputController.ground_point(camera,get_viewport().get_mouse_position())
	if point is Vector3: aim = Vector2(point.x,point.z)
	var movement: Vector2 = input_controller.movement_world(camera)
	if movement.length_squared() > .01: sim.set_destination(sim.player+movement)
	var request: Dictionary = input_controller.consume_request(sim,aim)
	controller.step(request.cast,request.aim)
	hero_hurt_ticks = maxi(0,hero_hurt_ticks-1)
	for event in sim.events:
		if event.kind == "cast_start":
			hero_hurt_ticks = 0
			animate(hero,"Spellcast_Shoot",float(sim.params.proxy_cast_animation_speed),true)
			last_hero_state = "cast"
		elif event.kind == "player_hurt":
			hero_hurt_ticks = 18
			animate(hero,"Hit_A",1.5,true)
			last_hero_state = "hurt"
		elif event.kind == "player_dead":
			animate(hero,"Death_A",1.0,true)
			last_hero_state = "dead"
	effects.consume(sim.events,sim)
	audio.consume(sim.events,sim.progress_events)
	sync_actors()
	if controller.state != "active":
		input_controller.clear()
		apply_pause_visuals()
	sync_equipment_hud()

func sync_actors() -> void:
	if not hero: return
	hero.position = Vector3(sim.player.x,0,sim.player.y)
	if sim.last_direction.length_squared() > .01: hero.rotation.y = atan2(sim.last_direction.x,sim.last_direction.y)
	actor_registry.sync(sim)
	if sim.life > 0 and hero_hurt_ticks <= 0 and sim.pending.is_empty() and sim.tick >= sim.next_cast_tick:
		var desired := "Walking_A" if sim.player.distance_to(sim.move_target) > .05 else "Idle"
		if desired != last_hero_state:
			animate(hero,desired)
			last_hero_state = desired
	world_presenter.sync_elite(controller.elite_identity,actor_registry)
	loot.sync(sim,camera)

func sync_equipment_hud() -> void:
	hud.update(controller.snapshot(),sim,controller.paused,is_equipment_open())

func _process(delta: float) -> void:
	age += delta
	if controller.state == "active" and not sim.paused:
		sync_actors()
		actor_registry.advance(delta,camera,sim.player)
		effects.sync(sim,delta)
	sync_equipment_hud()
	if _qa_quit_after > 0 and age >= _qa_quit_after: get_tree().quit(0)
