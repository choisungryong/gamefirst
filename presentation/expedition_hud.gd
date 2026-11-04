extends RefCounted
## An output-only expedition HUD. The view routes every intent to the controller.
signal start
signal retry
signal load
signal menu
signal equipment
signal skill(index: int)
signal auto
signal mute
signal volume(value: float)
const BONE := Color("e0dccd")
const BRONZE := Color("a38b56")
const INK := Color("142026")
const MUTED := Color("a5b6b9")
var view: Node3D
var root: Control
var timer: Label
var objective: Label
var phase_label: Label
var life_label: Label
var mana_label: Label
var xp_label: Label
var life_bar: ProgressBar
var mana_bar: ProgressBar
var xp_bar: ProgressBar
var skill_buttons: Array[Button] = []
var auto_button: Button
var mute_button: Button
var volume_slider: HSlider
var equip_button: Button
var pause_label: Label
var overlay: Control
var overlay_title: Label
var overlay_body: Label
var start_button: Button
var retry_button: Button
var load_button: Button
var menu_button: Button
var help_label: Label
var notice: Label
var muted := false
var _last_state := ""
var _last_paused := false

func setup(owner_view: Node3D) -> void:
	view = owner_view
	var layer := CanvasLayer.new()
	layer.name = "ExpeditionInterface"
	view.add_child(layer)
	root = Control.new()
	root.name = "ExpeditionHUD"
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(root)
	var header := PanelContainer.new()
	anchor(header,Vector2(.5,0),Vector2(.5,0),Rect2(-300,18,600,106))
	header.add_theme_stylebox_override("panel",style(Color(.06,.10,.12,.89),Color(.46,.45,.33,.65),14))
	root.add_child(header)
	var headbox := VBoxContainer.new()
	headbox.alignment = BoxContainer.ALIGNMENT_CENTER
	headbox.add_theme_constant_override("separation",2)
	header.add_child(headbox)
	timer = text("00:00",32,BONE)
	timer.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	headbox.add_child(timer)
	objective = text("수호자를 쓰러뜨리고 4분을 버티세요",19,Color("dcc694"))
	objective.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	headbox.add_child(objective)
	phase_label = text("회랑 입구",14,MUTED)
	phase_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	headbox.add_child(phase_label)
	var title := text("잿빛 회랑",24,BONE)
	anchor(title,Vector2.ZERO,Vector2.ZERO,Rect2(32,24,290,36))
	root.add_child(title)
	xp_label = text("레벨 1   경험치 0 / 6",16,MUTED)
	anchor(xp_label,Vector2.ZERO,Vector2.ZERO,Rect2(33,64,280,26))
	root.add_child(xp_label)
	xp_bar = bar(Color("af9558"))
	anchor(xp_bar,Vector2.ZERO,Vector2.ZERO,Rect2(33,96,240,4))
	root.add_child(xp_bar)
	var topactions := HBoxContainer.new()
	anchor(topactions,Vector2(1,0),Vector2(1,0),Rect2(-355,24,325,42))
	topactions.add_theme_constant_override("separation",8)
	root.add_child(topactions)
	equip_button = action("장비 [I]",func(): equipment.emit())
	topactions.add_child(equip_button)
	mute_button = action("소리 켜짐 [M]",func(): mute.emit())
	topactions.add_child(mute_button)
	var volume_row := HBoxContainer.new()
	anchor(volume_row,Vector2(1,0),Vector2(1,0),Rect2(-254,76,222,24))
	root.add_child(volume_row)
	volume_row.add_child(text("전체 음량",14,MUTED))
	volume_slider=HSlider.new()
	volume_slider.custom_minimum_size=Vector2(140,20)
	volume_slider.min_value=0
	volume_slider.max_value=1
	volume_slider.step=.01
	volume_slider.value=.35
	volume_slider.tooltip_text="전체 음량"
	volume_slider.value_changed.connect(func(value: float): volume.emit(value))
	volume_row.add_child(volume_slider)
	var bottom := PanelContainer.new()
	anchor(bottom,Vector2(0,1),Vector2(1,1),Rect2(0,-130,0,130))
	bottom.add_theme_stylebox_override("panel",style(Color(.045,.07,.085,.96),Color("665d43"),24))
	root.add_child(bottom)
	var foot := HBoxContainer.new()
	foot.add_theme_constant_override("separation",30)
	bottom.add_child(foot)
	var health := VBoxContainer.new()
	health.custom_minimum_size.x = 320
	health.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	foot.add_child(health)
	life_label = text("생명 40 / 40",22,BONE)
	health.add_child(life_label)
	life_bar = bar(Color("b8584c"))
	life_bar.custom_minimum_size.y = 18
	health.add_child(life_bar)
	health.add_child(text("이동  WASD / 좌클릭",14,MUTED))
	var center := VBoxContainer.new()
	center.custom_minimum_size.x = 590
	foot.add_child(center)
	var skills := HBoxContainer.new()
	skills.add_theme_constant_override("separation",8)
	center.add_child(skills)
	var colors := [Color("e7a067"),Color("82cad4"),Color("bdabec")]
	var names := ["◈  화염탄 [1]","◇  서리 파동 [2]","ϟ  연쇄 번개 [3]"]
	for i in range(3):
		var b := action(names[i],func(): skill.emit(i))
		b.custom_minimum_size = Vector2(188,44)
		b.add_theme_color_override("font_color",colors[i])
		skills.add_child(b)
		skill_buttons.append(b)
	auto_button = action("자동 시전 켜기 [F]",func(): auto.emit())
	auto_button.custom_minimum_size.y = 30
	center.add_child(auto_button)
	var mana := VBoxContainer.new()
	mana.custom_minimum_size.x = 320
	mana.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	foot.add_child(mana)
	mana_label = text("마나 35 / 35",22,BONE)
	mana_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	mana.add_child(mana_label)
	mana_bar = bar(Color("568ea6"))
	mana_bar.custom_minimum_size.y = 18
	mana.add_child(mana_bar)
	var mana_hint := text("우클릭 시전   ·   초당 마나 +3",14,MUTED)
	mana_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	mana.add_child(mana_hint)
	notice = text("가까이 다가가 장비를 획득하세요",17,Color("d8c498"))
	notice.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	anchor(notice,Vector2(.5,1),Vector2(.5,1),Rect2(-420,-173,840,30))
	root.add_child(notice)
	pause_label = text("일시 정지   Esc로 계속",27,BONE)
	pause_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	anchor(pause_label,Vector2(.5,.5),Vector2(.5,.5),Rect2(-250,-25,500,50))
	root.add_child(pause_label)
	pause_label.hide()
	build_overlay()

func build_overlay() -> void:
	overlay = Control.new()
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(overlay)
	var shade := ColorRect.new()
	shade.color = Color(.015,.025,.035,.35)
	shade.mouse_filter=Control.MOUSE_FILTER_IGNORE
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.add_child(shade)
	var panel := PanelContainer.new()
	anchor(panel,Vector2(0,.5),Vector2(0,.5),Rect2(70,-245,520,490))
	panel.add_theme_stylebox_override("panel",style(Color(.045,.075,.095,.97),Color("8e7951"),34))
	overlay.add_child(panel)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation",16)
	panel.add_child(box)
	box.add_child(text("잿빛 회랑",19,BRONZE))
	overlay_title = text("무너진 빛을 따라",38,BONE)
	box.add_child(overlay_title)
	overlay_body = text("네 개의 횃불 사이에서 망자를 막아내세요.\n3분에 나타나는 수호자를 쓰러뜨리고\n4분을 버티면 회랑이 열립니다.",20,Color("b7c7c8"))
	overlay_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	overlay_body.custom_minimum_size.y = 130
	box.add_child(overlay_body)
	start_button = action("원정 시작",func(): start.emit(),true)
	start_button.custom_minimum_size.y = 52
	box.add_child(start_button)
	retry_button = action("다시 도전",func(): retry.emit(),true)
	retry_button.custom_minimum_size.y = 52
	box.add_child(retry_button)
	load_button = action("성장 기록 불러오기",func(): load.emit())
	load_button.tooltip_text = "성장 기록으로 시간이 00:00인 새 원정을 시작합니다. 현재 생명과 마나는 유지됩니다."
	box.add_child(load_button)
	menu_button = action("시작 화면",func(): menu.emit())
	box.add_child(menu_button)
	help_label = text("WASD 이동 · 우클릭 시전 · F 자동 · I 장비\nR 새 원정 · Esc 정지 · M 음소거",14,MUTED)
	box.add_child(help_label)
	start_button.grab_focus()

func update(snapshot: Dictionary,sim: RefCounted,paused: bool,equipment_open: bool) -> void:
	var seconds := int(snapshot.get("elapsed_seconds",0))
	timer.text = "%02d:%02d" % [seconds/60,seconds%60]
	var state := String(snapshot.get("state","ready"))
	var elite_dead := bool(snapshot.get("elite_defeated",false))
	objective.text = "수호자 처치 완료 · 4분까지 생존" if elite_dead else ("쇠락한 수호자를 쓰러뜨리세요" if bool(snapshot.get("elite_spawned",false)) else "수호자가 나타날 때까지 생존하세요")
	var phase: String = str(snapshot.get("phase","회랑 입구"))
	phase={"arrival":"회랑 입구","awakening":"다가오는 망자","pressure":"무너진 경계","warning":"수호자의 전조","elite":"쇠락한 수호자","finale":"회랑의 끝"}.get(phase,phase)
	phase_label.text = "%s    처치 %d" % [phase,sim.kills]
	life_label.text = "생명 %s / %s" % [quantity(sim.life),quantity(float(sim.life_max_raw)/256.0)]
	mana_label.text = "마나 %s / %s" % [quantity(float(sim.mana_raw)/256.0),quantity(float(sim.mana_max_raw)/256.0)]
	life_bar.value = float(sim.life)*256.0/maxf(1,float(sim.life_max_raw))*100.0
	mana_bar.value = float(sim.mana_raw)/maxf(1,float(sim.mana_max_raw))*100.0
	var progress: Dictionary = sim.progression_snapshot()
	xp_label.text = "레벨 %d   경험치 %d%s" % [int(progress.level),int(progress.xp)," / %d" % int(progress.next_level_xp) if int(progress.next_level_xp)>0 else ""]
	var floor_xp := 6 if int(progress.level)==2 else 0
	if int(progress.level)>=3: floor_xp=18
	xp_bar.value = float(int(progress.xp)-floor_xp)/maxf(1,float(int(progress.next_level_xp)-floor_xp))*100.0 if int(progress.level)<3 else 100
	var ids: Array = sim._skill_definitions.keys()
	for i in range(mini(3,ids.size())):
		var selected: bool = ids[i] == sim.selected_skill_id
		skill_buttons[i].add_theme_stylebox_override("normal",style(Color("293d44") if selected else INK,BRONZE if selected else Color("465052"),8))
	var auto_enabled: bool = view.input_controller.auto_cast
	auto_button.text = "자동 시전 중 [F]" if auto_enabled else "자동 시전 켜기 [F]"
	mute_button.text = "소리 꺼짐 [M]" if muted else "소리 켜짐 [M]"
	var is_finished := state in ["victory","defeat","timeout"]
	overlay.visible = (state=="ready" or is_finished) and not equipment_open
	pause_label.visible = paused and state=="active" and not equipment_open
	equip_button.disabled = state=="ready"
	start_button.visible = state=="ready"
	retry_button.visible = is_finished
	menu_button.visible = is_finished
	load_button.visible = state=="ready"
	if state != _last_state:
		if state=="ready":
			overlay_title.text = "무너진 빛을 따라"
			overlay_body.text = "망자를 막고, 떨어진 장비로 힘을 갖추세요.\n3분에 나타나는 수호자를 처치하고\n4분을 버티면 회랑이 열립니다.\n성장 기록을 불러오면 00:00부터 새 원정을 시작합니다."
		else:
			overlay_title.text = {"victory":"회랑이 열렸습니다","defeat":"빛이 사라졌습니다","timeout":"회랑에 갇혔습니다"}.get(state,"")
			var summary: Dictionary = snapshot.get("summary",{})
			overlay_body.text = "%02d:%02d 생존 · %d 처치\n이번 원정 경험치 +%d\n성장과 소유 장비는 다음 원정에도 남습니다." % [seconds/60,seconds%60,sim.kills,int(summary.get("xp_delta",0))]
		if overlay.visible:
			(start_button if state=="ready" else retry_button).grab_focus()
		_last_state=state
	notice.visible = state=="active" and not paused and not equipment_open
	if sim.ground_loot_snapshot().size()>0: notice.text="가까이 다가가 장비를 획득하세요"
	elif seconds<15: notice.text="WASD로 이동 · F로 가까운 적을 자동 공격하세요"
	else: notice.text="I 장비 · Esc 정지 · R 새 원정"

func set_muted(value: bool) -> void:
	muted=value

func quantity(value: float) -> String:
	return "%.1f" % value if not is_equal_approx(value,roundf(value)) else str(roundi(value))

func text(content: String,size_: int,color: Color) -> Label:
	var label := Label.new()
	label.text=content
	label.add_theme_font_size_override("font_size",size_)
	label.add_theme_color_override("font_color",color)
	label.mouse_filter=Control.MOUSE_FILTER_IGNORE
	return label

func action(content: String,callback: Callable,primary: bool=false) -> Button:
	var button := Button.new()
	button.text=content
	button.custom_minimum_size=Vector2(130,38)
	button.add_theme_font_size_override("font_size",17)
	button.add_theme_color_override("font_color",BONE)
	button.add_theme_stylebox_override("normal",style(Color("38454a") if primary else INK,BRONZE if primary else Color("586567"),10))
	button.add_theme_stylebox_override("hover",style(Color("43545a"),Color("ccba87"),10))
	button.add_theme_stylebox_override("pressed",style(Color("25343b"),Color("e1d3a8"),10))
	button.add_theme_stylebox_override("focus",style(Color(0,0,0,0),Color("e1d3a8"),10))
	button.pressed.connect(callback)
	return button

func style(background: Color,border: Color,padding: int) -> StyleBoxFlat:
	var result:=StyleBoxFlat.new()
	result.bg_color=background
	result.border_color=border
	result.set_border_width_all(1)
	result.content_margin_left=padding
	result.content_margin_right=padding
	result.content_margin_top=padding/2.0
	result.content_margin_bottom=padding/2.0
	return result

func bar(color: Color) -> ProgressBar:
	var progress:=ProgressBar.new()
	progress.show_percentage=false
	progress.add_theme_stylebox_override("background",style(Color("172126"),Color("576164"),0))
	progress.add_theme_stylebox_override("fill",style(color,color,0))
	return progress

func anchor(control: Control,begin: Vector2,end: Vector2,rect: Rect2) -> void:
	control.anchor_left=begin.x
	control.anchor_top=begin.y
	control.anchor_right=end.x
	control.anchor_bottom=end.y
	control.offset_left=rect.position.x
	control.offset_top=rect.position.y
	control.offset_right=rect.end.x
	control.offset_bottom=rect.end.y
