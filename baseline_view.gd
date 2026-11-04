extends Node3D
## Small independent scene, not the earlier survivor pilot.
## Godot 4.5 APIs: Camera3D.project_ray_origin/project_ray_normal,
## Plane.intersects_ray, Sprite3D.frame_coords, AnimationPlayer.play.
## https://docs.godotengine.org/en/4.5/classes/class_camera3d.html
## https://docs.godotengine.org/en/4.5/classes/class_sprite3d.html
const Simulation = preload("res://baseline_sim.gd")
const InputController = preload("res://presentation/input_controller.gd")
const ActorRegistry = preload("res://presentation/actor_registry.gd")
const EffectPresenter = preload("res://presentation/effect_presenter.gd")
const HUDPresenter = preload("res://presentation/hud_presenter.gd")
const LootPresenter = preload("res://presentation/loot_presenter.gd")
const EquipmentPresenter = preload("res://presentation/equipment_presenter.gd")
const QAOutput = preload("res://presentation/qa_output.gd")
const StaticBatch = preload("res://presentation/static_batch.gd")
const SkinnedMeshBatch = preload("res://presentation/skinned_mesh_batch.gd")
var skinned_mesh_batch = SkinnedMeshBatch.new()
var tinted_materials: Dictionary = {}
var floor_stats: Dictionary = {}
var input_controller = InputController.new()
var actor_registry = ActorRegistry.new()
var effect_presenter = EffectPresenter.new()
var equipment_presenter = EquipmentPresenter.new()
var loot_presenter = LootPresenter.new()
var equipment_button: Button
var equipment_previous_paused := false
var initial_enemies := 1
var crowd_label: Label
var skill_buttons: Array[Button] = []
var auto_button: Button
var skill_mode_label: Label
var sim = Simulation.new()
var camera: Camera3D
var hero: Node3D
var enemy_actor: Node3D
var world: Node3D
var projectile_nodes: Dictionary:
	get: return effect_presenter.projectile_nodes
var particles: Array:
	get: return effect_presenter.particles
var held: bool:
	get: return input_controller.held
	set(value): input_controller.held = value
var queued_cast: bool:
	get: return input_controller.queued_cast
	set(value): input_controller.queued_cast = value
var aim := Vector2(3.4,-2.5)
var comparison: PanelContainer
var status_label: Label
var mana_label: Label
var life_label: Label
var mana_bar: ProgressBar
var life_bar: ProgressBar
var enemy_bar: ProgressBar
var enemy_label: Label
var hint: Label
var cast_status: Label
var stats_text: Label
var pause_cover: PanelContainer
var move_marker: Node3D
var cast_glow: OmniLight3D
var last_enemy_state := ""
var last_hero_state := ""
var status_until := 0.0
var age := 0.0
var fx_time := 0.0
var hero_hurt_ticks := 0
var qa := false
var capture_path := ""
var capture_at := 1.15
var quit_after := 3.0
var captured := false
var capture_size := Vector2i.ZERO
var capture_saved := false
var report_dir := "user://evidence"
var atlas: Texture2D = preload("res://assets/firebolt-sheet.png")
var direction_angles := [135.0,-135.0,-45.0,45.0,90.0,180.0,-90.0,0.0,112.5,157.5,-157.5,-112.5,-67.5,-22.5,22.5,67.5]

func _ready() -> void:
	if not sim.valid_profile:
		get_tree().quit(1)
		return
	var requested_skill := ""
	var requested_auto := false
	for arg in OS.get_cmdline_user_args():
		if arg == "--qa": qa = true
		elif arg.begins_with("--capture="): capture_path = arg.trim_prefix("--capture=")
		elif arg.begins_with("--capture-at="): capture_at = float(arg.trim_prefix("--capture-at="))
		elif arg.begins_with("--quit-after="): quit_after = float(arg.trim_prefix("--quit-after="))
		elif arg.begins_with("--report="): report_dir = arg.trim_prefix("--report=")
		elif arg.begins_with("--skill="): requested_skill = arg.trim_prefix("--skill=")
		elif arg == "--auto-skill": requested_auto = true
		elif arg.begins_with("--enemies="):
			var count_text: String = arg.trim_prefix("--enemies=")
			if not count_text.is_valid_int() or int(count_text)<0 or int(count_text)>sim.MAX_ENTITIES:
				push_error("--enemies requires0..2000")
				get_tree().quit(1)
				return
			initial_enemies = int(count_text)
	if initial_enemies != 1: sim.reset(initial_enemies)
	if not requested_skill.is_empty():
		if not sim.has_method("select_skill") or not sim.select_skill(requested_skill):
			push_error("Unknown independent skill: "+requested_skill)
			get_tree().quit(1)
			return
	build_world()
	build_ui()
	effect_presenter.setup(self,add_mesh,material)
	get_window().focus_exited.connect(clear_pointer_state)
	input_controller.auto_cast = requested_auto
	if OS.get_cmdline_user_args().has("--reference-open"): comparison.show()
	if qa: sim.enemy_ai = false
	sync_actors()
	print("BASELINE_READY: independent core; actors+original classic atlas loaded")

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

func build_world() -> void:
	world = Node3D.new()
	add_child(world)
	var env_node := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("172321")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("b6c6c2")
	env.ambient_light_energy = .48
	env.tonemap_mode = Environment.TONE_MAPPER_LINEAR
	env.fog_enabled = true
	env.fog_light_color = Color("263432")
	env.fog_density = .008
	env_node.environment = env
	add_child(env_node)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55,-28,0)
	sun.light_color = Color("c6d5cc")
	sun.light_energy = .95
	sun.shadow_enabled = true
	add_child(sun)
	var plane := PlaneMesh.new()
	plane.size = Vector2(70,70)
	add_mesh(plane,Vector3(0,-.10,0),material(Color("283530")),world)
	var rng := RandomNumberGenerator.new()
	rng.seed = 415
	var floor_roots: Array[Node3D] = []
	for x in range(-6,7):
		for z in range(-5,6):
			var name_: String = "floor_dirt_large_rocky.gltf.glb" if absi(x)>3 or absi(z)>3 else "floor_tile_large.gltf.glb"
			var tile: Node3D = load_model("res://assets/environment/"+name_,Vector3(x*2,-.04,z*2),world)
			tile.rotation.y = rng.randi_range(0,3)*PI*.5
			tint_model(tile,Color(.43,.49,.43))
			floor_roots.append(tile)
	if not OS.get_cmdline_user_args().has("--unbatched-floor"):
		floor_stats = StaticBatch.batch(world,floor_roots)
	for pos in [Vector3(-7,0,-5),Vector3(7,0,-5),Vector3(-8,0,5),Vector3(8,0,5)]:
		var pillar: Node3D = load_model("res://assets/environment/column.gltf.glb",pos,world)
		tint_model(pillar,Color(.55,.58,.51))
	for x in [-5.0,-1.0,3.0,7.0]:
		var wall: Node3D = load_model("res://assets/environment/wall_broken.gltf.glb",Vector3(x,0,-8),world)
		tint_model(wall,Color(.49,.54,.48))
	for pos in [Vector3(-6,0,1),Vector3(6,0,-3)]:
		load_model("res://assets/environment/torch_lit.gltf.glb",pos,world)
		var light := OmniLight3D.new()
		light.position = pos+Vector3(0,1.8,0)
		light.light_color = Color("f0bd7c")
		light.light_energy = 1.3
		light.omni_range = 6
		add_child(light)
	hero = load_model("res://assets/actors/Mage.glb",Vector3.ZERO)
	hero.scale = Vector3.ONE*1.15
	enemy_actor = load_model("res://assets/actors/Skeleton_Minion.glb",Vector3.ZERO)
	enemy_actor.scale = Vector3.ONE*1.12
	tint_model(enemy_actor,Color(.74,.86,.68))
	actor_registry.setup(enemy_actor,load_model,animate,tint_model)
	cast_glow = OmniLight3D.new()
	cast_glow.light_color = Color("ffb35e")
	cast_glow.omni_range = 4.0
	cast_glow.light_energy = 0
	add_child(cast_glow)
	camera = Camera3D.new()
	camera.position = Vector3(12,18,15)
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 18.8
	add_child(camera)
	camera.look_at(Vector3(0,.2,0))
	camera.current = true
	move_marker = Node3D.new()
	add_child(move_marker)
	var ring := TorusMesh.new()
	ring.inner_radius = .23
	ring.outer_radius = .27
	ring.rings = 24
	ring.ring_segments = 4
	add_mesh(ring,Vector3(0,.04,0),material(Color("b6c6a6"),.3),move_marker)
	move_marker.hide()

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

func build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var ui := Control.new()
	ui.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	ui.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(ui)
	var theme_ := Theme.new()
	var font := SystemFont.new()
	font.font_names = PackedStringArray(["Malgun Gothic"])
	theme_.default_font = font
	ui.theme = theme_
	var title := label("전투 기준실",27)
	var display_font := SystemFont.new()
	display_font.font_names = PackedStringArray(["Batang","Malgun Gothic"])
	title.add_theme_font_override("font",display_font)
	title.position = Vector2(35,24)
	ui.add_child(title)
	var subtitle := label("독립 전투 실험 · 임시 모델",14,Color("b9c9ba"))
	subtitle.position = Vector2(37,65)
	ui.add_child(subtitle)
	crowd_label = label("",15,Color("cad8c6"))
	crowd_label.position = Vector2(37,94)
	ui.add_child(crowd_label)
	for i in range(3):
		var count: int = [1,10,100][i]
		var crowd_button := button("%d마리" % count,set_enemy_count.bind(count))
		crowd_button.position = Vector2(37+i*112,125)
		crowd_button.size.x = 104
		ui.add_child(crowd_button)
	if sim.has_method("available_skill_ids"):
		var ids: Array = sim.available_skill_ids()
		for index in range(mini(ids.size(),3)):
			var definition: Dictionary = sim.skill_definition(ids[index])
			var skill_button := button("[%d] %s" % [index+1,definition.get("display_name",ids[index])],select_skill_index.bind(index))
			skill_button.position = Vector2(37+index*178,174)
			skill_button.size.x = 170
			skill_buttons.append(skill_button)
			ui.add_child(skill_button)
		auto_button = button("자동 시전 끔 [F]",toggle_auto_cast)
		auto_button.position = Vector2(37,220)
		auto_button.size.x = 220
		ui.add_child(auto_button)
		skill_mode_label = label("",14,Color("bdd0d7"))
		skill_mode_label.position = Vector2(37,274)
		skill_mode_label.size = Vector2(540,48)
		ui.add_child(skill_mode_label)
	var reference := button("근거와 가정  [Tab]",func(): comparison.visible = not comparison.visible)
	reference.position = Vector2(1335,26)
	reference.size.x = 230
	ui.add_child(reference)
	equipment_button = button("장비와 소지품 [I]",toggle_equipment)
	equipment_button.position = Vector2(1087,26)
	equipment_button.size.x = 230
	ui.add_child(equipment_button)
	var footer := Panel.new()
	footer.position = Vector2(0,790)
	footer.size = Vector2(1600,110)
	footer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	footer.add_theme_stylebox_override("panel",style(Color(.035,.065,.06,.94)))
	ui.add_child(footer)
	life_label = label("생명 40 / 40",18)
	life_label.position = Vector2(38,805)
	ui.add_child(life_label)
	life_bar = ProgressBar.new()
	life_bar.position = Vector2(38,839)
	life_bar.size = Vector2(285,10)
	life_bar.max_value = 40
	life_bar.show_percentage = false
	life_bar.add_theme_font_size_override("font_size",1)
	life_bar.add_theme_stylebox_override("fill",bar_style(Color("b54d4d")))
	life_bar.add_theme_stylebox_override("background",bar_style(Color("302b28")))
	ui.add_child(life_bar)
	mana_label = label("마나 35 / 35",18)
	mana_label.position = Vector2(1270,805)
	ui.add_child(mana_label)
	mana_bar = ProgressBar.new()
	mana_bar.position = Vector2(1270,839)
	mana_bar.size = Vector2(290,10)
	mana_bar.max_value = 35
	mana_bar.step = .01
	mana_bar.show_percentage = false
	mana_bar.add_theme_font_size_override("font_size",1)
	mana_bar.add_theme_stylebox_override("fill",bar_style(Color("598cb9")))
	mana_bar.add_theme_stylebox_override("background",bar_style(Color("253137")))
	ui.add_child(mana_bar)
	cast_status = label("화염탄   피해 3–6   ·   마나 2.5",18,Color("edc78f"))
	cast_status.position = Vector2(430,805)
	cast_status.size.x = 795
	ui.add_child(cast_status)
	hint = label("이동: 좌클릭/WASD · 시전: 우클릭 · 스킬: 1/2/3 · 자동: F · 장비: I · 정지: Esc · 초기화: R",13,Color("a9b6ad"))
	hint.position = Vector2(398,845)
	ui.add_child(hint)
	status_label = label("화염탄을 조준해 보세요",18,Color("f3dcab"))
	status_label.position = Vector2(590,743)
	status_label.size.x = 440
	status_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	ui.add_child(status_label)
	enemy_label = label("좀비 · 임시 외형",15,Color("dce2ce"))
	ui.add_child(enemy_label)
	enemy_bar = ProgressBar.new()
	enemy_bar.size = Vector2(136,7)
	enemy_bar.max_value = 1
	enemy_bar.step = .001
	enemy_bar.show_percentage = false
	enemy_bar.add_theme_font_size_override("font_size",1)
	enemy_bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	enemy_bar.add_theme_stylebox_override("fill",bar_style(Color("a85746")))
	enemy_bar.add_theme_stylebox_override("background",bar_style(Color("292e27")))
	ui.add_child(enemy_bar)
	comparison = PanelContainer.new()
	comparison.position = Vector2(1130,90)
	comparison.size = Vector2(435,665)
	comparison.add_theme_stylebox_override("panel",style(Color(.045,.08,.075,.97),Color("687467")))
	ui.add_child(comparison)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation",14)
	comparison.add_child(box)
	box.add_child(label("원작과 대조할 기준",23,Color("e6d6b8")))
	var image := TextureRect.new()
	image.texture = preload("res://assets/reference/original-cast-strip.png")
	image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	image.custom_minimum_size = Vector2(390,78)
	box.add_child(image)
	var facts := label("확인한 근거\n화염탄 툴팁: 피해 3–6 / 마나 2.5\n자세 변화→분리된 탄: 약 0.30초\n원작 좀비: 첫 명중 뒤 체력바 감소,\n다음 명중 뒤 넘어져 시체로 남음",16,Color("c6d9c3"))
	box.add_child(facts)
	box.add_child(label("독립 게임의 현재 설정",19,Color("e4ba80")))
	stats_text = label("적 체력 9 · 이동/공격/피해는 실험값\n재시전 0.55초 · 비행속도 12 세계단위/초\n마나 재생 끔 · 피해 난수는 검증판 규칙\n3D 모델은 KayKit 대역, 탄은 클래식 자산",15,Color("c1c8bc"))
	box.add_child(stats_text)
	box.add_child(label("광역·연쇄·둔화·스탯 계산은 독립 설계\n원작 HP·최대 연사·AI 수치는 미검증",14,Color("acb7a9")))
	box.add_child(button("마나와 적 초기화  [R]",restart))
	box.add_child(button("패널 닫기  [Tab]",func(): comparison.hide()))
	comparison.hide()
	pause_cover = PanelContainer.new()
	pause_cover.position = Vector2(580,320)
	pause_cover.size = Vector2(440,220)
	pause_cover.add_theme_stylebox_override("panel",style(Color(.045,.08,.075,.98),Color("8c9785")))
	ui.add_child(pause_cover)
	var paused_box := VBoxContainer.new()
	paused_box.add_theme_constant_override("separation",15)
	pause_cover.add_child(paused_box)
	paused_box.add_child(label("전투 일시 정지",27))
	paused_box.add_child(button("계속하기",toggle_pause))
	paused_box.add_child(button("처음부터 다시",restart))
	pause_cover.hide()
	equipment_presenter.setup(self,ui)

func mouse_ground(position_: Vector2) -> Variant:
	return InputController.ground_point(camera,position_)

func _unhandled_input(event: InputEvent) -> void:
	if is_equipment_open():
		if event is InputEventKey and event.pressed and not event.echo:
			if event.keycode in [KEY_I,KEY_ESCAPE]: toggle_equipment()
			elif event.keycode == KEY_R: restart()
		get_viewport().set_input_as_handled()
		return
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_I:
			toggle_equipment()
			get_viewport().set_input_as_handled()
			return
		elif event.keycode == KEY_ESCAPE: toggle_pause()
		elif event.keycode == KEY_R: restart()
		elif event.keycode == KEY_TAB: comparison.visible = not comparison.visible
		elif not sim.paused:
			if event.keycode == KEY_1: select_skill_index(0)
			elif event.keycode == KEY_2: select_skill_index(1)
			elif event.keycode == KEY_3: select_skill_index(2)
			elif event.keycode == KEY_F: toggle_auto_cast()
	if not sim.paused: input_controller.unhandled(event)
	if not sim.paused:
		var hit: Variant = input_controller.destination_request(event,camera)
		if hit is Vector3:
			sim.set_destination(Vector2(hit.x,hit.z))
			move_marker.position = Vector3(sim.move_target.x,.02,sim.move_target.y)
			move_marker.show()

func _input(event: InputEvent) -> void:
	input_controller.global_input(event)

func clear_pointer_state() -> void:
	input_controller.clear()

func select_skill_index(index: int) -> void:
	if sim.paused or not sim.has_method("available_skill_ids"): return
	var ids: Array = sim.available_skill_ids()
	if index < 0 or index >= ids.size(): return
	if sim.select_skill(ids[index]):
		input_controller.clear_pointer()
		sync_actors()

func toggle_auto_cast() -> void:
	if sim.paused: return
	input_controller.toggle_auto()
	HUDPresenter.sync(self,sim,camera,actor_registry,aim)

func set_enemy_count(count: int) -> void:
	if is_equipment_open(): return
	sim.initial_count = clampi(count,0,sim.MAX_ENTITIES)
	restart()

func toggle_pause() -> void:
	if is_equipment_open():
		toggle_equipment()
		return
	sim.paused = not sim.paused
	input_controller.clear()
	apply_pause_visuals()
	HUDPresenter.sync(self,sim,camera,actor_registry,aim)

func apply_pause_visuals() -> void:
	for actor in [hero,actor_registry.primary]:
		var ap: AnimationPlayer = actor.get_meta("player")
		ap.speed_scale = 0.0 if sim.paused else 1.0
	actor_registry.set_paused(sim.paused)
	pause_cover.visible = sim.paused and not is_equipment_open()

func is_equipment_open() -> bool:
	return equipment_presenter.is_open()

func toggle_equipment() -> void:
	input_controller.clear()
	move_marker.hide()
	if is_equipment_open():
		equipment_presenter.close()
		sim.paused = equipment_previous_paused
	else:
		equipment_previous_paused = sim.paused
		comparison.hide()
		equipment_presenter.open()
		sim.paused = true
	apply_pause_visuals()
	HUDPresenter.sync(self,sim,camera,actor_registry,aim)

func sync_equipment_hud() -> void:
	HUDPresenter.sync(self,sim,camera,actor_registry,aim)

func progress_loaded() -> void:
	# The modal remains paused after the simulation has restarted its combat.
	actor_registry.reset()
	effect_presenter.reset()
	loot_presenter.reset()
	input_controller.clear()
	last_enemy_state = ""
	last_hero_state = ""
	hero_hurt_ticks = 0
	move_marker.hide()
	cast_glow.light_energy = 0
	sim.paused = true
	sync_actors()
	apply_pause_visuals()

func restart() -> void:
	sim.reset()
	actor_registry.reset()
	effect_presenter.reset()
	loot_presenter.reset()
	input_controller.clear()
	last_enemy_state = ""
	last_hero_state = ""
	hero_hurt_ticks = 0
	pause_cover.hide()
	for actor in [hero,actor_registry.primary]:
		var ap: AnimationPlayer = actor.get_meta("player")
		ap.stop()
		ap.speed_scale = 1.0
	move_marker.hide()
	status_label.text = "선택한 스킬을 조준해 보세요"
	status_until = 0
	cast_glow.light_energy = 0
	sync_actors()
	if is_equipment_open():
		sim.paused = true
		apply_pause_visuals()
		equipment_presenter.refresh()
		HUDPresenter.sync(self,sim,camera,actor_registry,aim)

func _physics_process(_delta: float) -> void:
	if sim.paused: return
	hero_hurt_ticks = maxi(0,hero_hurt_ticks-1)
	var ground_hit: Variant = mouse_ground(get_viewport().get_mouse_position())
	if ground_hit is Vector3: aim = Vector2(ground_hit.x,ground_hit.z)
	if qa:
		var target: Dictionary = sim.nearest_enemy(sim.player)
		if not target.is_empty(): aim = target.p
		held = not target.is_empty()
	else:
		var movement: Vector2 = input_controller.movement_world(camera)
		if movement.length_squared() > .01:
			sim.set_destination(sim.player+movement)
	# Requests are consumed inside the core step, after its events.clear().
	# A quick press+release before the next tick still preserves one cast.
	if sim.has_method("skill_display"):
		var request: Dictionary = input_controller.consume_request(sim,aim)
		sim.step(request.cast,request.aim)
	else:
		sim.step(input_controller.consume(),aim)
	for event in sim.events: handle_event(event)

func handle_event(event: Dictionary) -> void:
	if event.kind in ["skill_effect","status_applied","status_expired"]:
		effect_presenter.handle_skill_event(event)
	if event.kind == "cast_start":
		hero_hurt_ticks = 0
		animate(hero,"Spellcast_Shoot",float(sim.params.proxy_cast_animation_speed),true)
		last_hero_state = "cast"
		cast_glow.light_energy = 1.1
	elif event.kind == "release":
		burst(Vector3(sim.player.x,.8,sim.player.y),event_color(event),6,.3)
	elif event.kind == "hit":
		var point: Vector3 = Vector3(event.p[0],.8,event.p[1])
		burst(point,event_color(event,true),16,.4)
		var skill_name := "화염탄"
		if sim.has_method("skill_definition"):
			var definition: Dictionary = sim.skill_definition(event.get("skill_id",sim.default_skill_id))
			if not definition.is_empty(): skill_name = definition.get("display_name",definition.id)
		status_label.text = skill_name+" 명중"
		status_until = age+1.1
	elif event.kind == "enemy_dead":
		status_label.text = "좀비 처치 %d · R로 다시 비교" % sim.kills
		status_until = age+60

	elif event.kind == "no_mana":
		status_label.text = "마나가 부족합니다 · R로 초기화"
		status_until = age+1.5
	elif event.kind == "player_hurt":
		animate(hero,"Hit_A",1.5,true)
		last_hero_state = "hurt"
		hero_hurt_ticks = 18
		status_label.text = "피격 · 적 공격 수치는 임시 설정"
		status_until = age+1.4
	elif event.kind == "player_dead":
		animate(hero,"Death_A")
		status_label.text = "쓰러졌습니다 · R로 다시 시작"
		status_until = age+60

func event_color(event: Dictionary, impact: bool = false) -> Color:
	match String(event.get("element","fire")):
		"cold": return Color("76d5dc")
		"lightning": return Color("bcadff")
	return Color("ffbe68") if impact else Color("f0a542")

func burst(at: Vector3, color: Color, amount: int, duration: float) -> void:
	effect_presenter.burst(at,color,amount,duration)

func sync_actors() -> void:
	var desired_position := Vector3(sim.player.x,0,sim.player.y)
	if hero.position != desired_position: hero.position = desired_position
	if sim.last_direction.length_squared() > .01:
		var desired_yaw: float = atan2(sim.last_direction.x,sim.last_direction.y)
		if hero.rotation.y != desired_yaw: hero.rotation.y = desired_yaw
	actor_registry.sync(sim)
	if not sim.enemy.is_empty():
		var legacy_actor: Node3D = actor_registry.actor_for(sim.enemy)
		if legacy_actor: enemy_actor = legacy_actor
	if sim.life > 0 and hero_hurt_ticks <= 0:
		if sim.pending.is_empty() and sim.tick>=sim.next_cast_tick:
			var desired: String = "Walking_A" if sim.player.distance_to(sim.move_target)>.05 else "Idle"
			if desired != last_hero_state:
				animate(hero,desired)
				last_hero_state = desired
	if move_marker.visible and sim.player.distance_to(sim.move_target)<.1: move_marker.hide()
	HUDPresenter.sync(self,sim,camera,actor_registry,aim)
	cast_glow.position = hero.position+Vector3(0,1,0)
	effect_presenter.sync(sim,camera,atlas)
	loot_presenter.sync(self,sim)

func quantity_text(value: float) -> String:
	return HUDPresenter.quantity(value)

func _process(delta: float) -> void:
	age += delta
	if not sim.paused:
		sync_actors()
		actor_registry.advance(delta,camera,sim.player)
		fx_time += delta
		cast_glow.light_energy = maxf(0,cast_glow.light_energy-delta*2.5)
		effect_presenter.advance(delta)
	if status_until > 0 and age>status_until: status_label.text = ""
	if not captured and capture_path!="" and age>=capture_at:
		captured = true
		var result: Dictionary = await QAOutput.capture(get_viewport(),capture_path)
		capture_size = result["size"]
		capture_saved = result.saved
		if not capture_saved:
			push_error("Failed to save requested framebuffer: "+capture_path)
			get_tree().quit(1)
			return
	if qa and age>=quit_after:
		var report_ok: bool = write_report()
		get_tree().quit(0 if report_ok else 1)

func write_report() -> bool:
	return QAOutput.write_report(self)
