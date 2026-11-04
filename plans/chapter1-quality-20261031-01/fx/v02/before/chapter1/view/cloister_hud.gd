extends RefCounted
## UI consumes run state; only explicit signals request core transitions.
signal start(primary: String)
signal choice(token: String, card_id: String)
signal equipment
signal close_equipment
signal equip_item(uid: int)
signal pause_toggle
signal retry
signal mute_toggle
signal motion_toggle(enabled: bool)
const Emblem=preload("res://chapter1/view/element_emblem.gd")
var root: Control
var overlay: ColorRect
var modal: PanelContainer
var hp: ProgressBar
var xp: ProgressBar
var status: Label
var skills: Label
var objective: Label
var dash: Label
var debug: Label
var toast: Label
var _last_signature := ""
var _last_hud_tick := -99
var _toast_left := 0.0
var _selected_item := -1
var temporary_art := true
var motion_enabled := true
var skill_labels: Dictionary={}
const SKILL_NAMES={"chapter1.skill.ember":"잿불탄","chapter1.skill.frost":"서리창","chapter1.skill.arc":"연쇄 전류"}
const SLOT_NAMES={"weapon":"무기","body":"갑옷","charm":"부적","ring":"반지"}

func setup(view: Node3D) -> void:
	var layer := CanvasLayer.new()
	view.add_child(layer)
	root=Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter=Control.MOUSE_FILTER_IGNORE
	layer.add_child(root)
	var theme := Theme.new()
	var font := SystemFont.new()
	font.font_names=PackedStringArray(["Malgun Gothic","맑은 고딕","sans-serif"])
	theme.default_font=font
	theme.default_font_size=17
	root.theme=theme
	var top := MarginContainer.new()
	top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	top.offset_left=28;top.offset_right=-28;top.offset_top=24
	root.add_child(top)
	var row := HBoxContainer.new()
	top.add_child(row)
	objective=_label("잿빛 회랑",20,Color("ded8c4"))
	objective.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	row.add_child(objective)
	var item_button := _button("장비 [I]",func():equipment.emit())
	row.add_child(item_button)
	row.add_child(_button("정지 [Esc]",func():pause_toggle.emit()))
	row.add_child(_button("음소거 [M]",func():mute_toggle.emit()))
	var bottom := PanelContainer.new()
	bottom.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	bottom.offset_top=-94;bottom.offset_left=22;bottom.offset_right=-22;bottom.offset_bottom=-18
	var frame := _style(Color(.055,.048,.038,.92),Color("69543b"))
	frame.content_margin_top=12;frame.content_margin_bottom=12;frame.content_margin_left=18;frame.content_margin_right=18
	bottom.add_theme_stylebox_override("panel",frame)
	root.add_child(bottom)
	var bottom_row := HBoxContainer.new()
	bottom_row.add_theme_constant_override("separation",24)
	bottom.add_child(bottom_row)
	var bars := VBoxContainer.new()
	bars.custom_minimum_size.x=245
	bottom_row.add_child(bars)
	status=_label("생명력",15)
	bars.add_child(status)
	hp=_bar(Color("a93b2d"),13)
	xp=_bar(Color("a68b4d"),5)
	bars.add_child(hp);bars.add_child(xp)
	skills=_label("",17)
	# Retain the text summary for accessibility/QA, while visible skill identities
	# have distinct source-code sigils and colors rather than one long sentence.
	skills.visible=false;root.add_child(skills)
	var sigils := HBoxContainer.new();sigils.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	sigils.add_theme_constant_override("separation",22);bottom_row.add_child(sigils)
	for pair in [["ember",Color("e88b43")],["frost",Color("8ac8de")],["arc",Color("b5bde4")]]:
		var chip := HBoxContainer.new();chip.custom_minimum_size.x=165;chip.size_flags_horizontal=Control.SIZE_EXPAND_FILL;chip.alignment=BoxContainer.ALIGNMENT_CENTER
		var icon := Emblem.new();icon.element=pair[0];icon.tint=pair[1];chip.add_child(icon)
		var text := _label("미습득",16,pair[1]);text.vertical_alignment=VERTICAL_ALIGNMENT_CENTER;chip.add_child(text)
		skill_labels["chapter1.skill."+pair[0]]=text;sigils.add_child(chip)
	dash=_label("Space 회피",14,Color("b9aa90"))
	dash.vertical_alignment=VERTICAL_ALIGNMENT_CENTER
	dash.custom_minimum_size.x=138
	bottom_row.add_child(dash)
	debug=_label("",14)
	debug.position=Vector2(28,92)
	debug.visible=false
	root.add_child(debug)
	toast=_label("",20,Color("f0d68b"))
	toast.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	toast.offset_left=-400;toast.offset_right=400;toast.offset_top=80
	toast.horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER
	root.add_child(toast)
	overlay=ColorRect.new()
	overlay.color=Color(.015,.012,.01,.78)
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_child(overlay)
	modal=PanelContainer.new()
	modal.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	modal.offset_left=190;modal.offset_right=-190;modal.offset_top=120;modal.offset_bottom=-120
	modal.add_theme_stylebox_override("panel",_style(Color("211c16"),Color("8b6b43")))
	overlay.add_child(modal)

func _style(color: Color, border: Color=Color("65523c")) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color=color;s.border_color=border;s.set_border_width_all(1);s.set_content_margin_all(22)
	s.corner_radius_top_left=2;s.corner_radius_top_right=2;s.corner_radius_bottom_left=2;s.corner_radius_bottom_right=2
	return s

func _label(text: String, size: int=18, color: Color=Color("e0d8c7")) -> Label:
	var label := Label.new()
	label.text=text;label.add_theme_font_size_override("font_size",size);label.add_theme_color_override("font_color",color)
	label.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	if size>=25:
		var heading := SystemFont.new();heading.font_names=PackedStringArray(["Batang","바탕","Georgia"])
		label.add_theme_font_override("font",heading)
	return label

func _bar(color: Color, height: float) -> ProgressBar:
	var bar := ProgressBar.new()
	bar.show_percentage=false;bar.custom_minimum_size.y=height
	var fill := _style(color,color);fill.set_content_margin_all(0)
	var back := _style(Color("332a20"),Color("332a20"));back.set_content_margin_all(0)
	bar.add_theme_stylebox_override("fill",fill)
	bar.add_theme_stylebox_override("background",back)
	return bar

func _button(text: String, action: Callable) -> Button:
	var b := Button.new()
	b.text=text;b.custom_minimum_size.y=42
	for variant in [["normal",Color("30271d"),Color("70583b")],["hover",Color("493922"),Color("b9955f")],["focus",Color("463823"),Color("d2b27c")]]:
		var style := _style(variant[1],variant[2]);style.content_margin_left=12;style.content_margin_right=12;style.content_margin_top=8;style.content_margin_bottom=8
		b.add_theme_stylebox_override(variant[0],style)
	b.pressed.connect(action)
	return b

func sync(run: RefCounted, delta: float) -> void:
	_toast_left=maxf(0,_toast_left-delta)
	toast.visible=_toast_left>0
	var signature: String=run.mode
	if run.mode=="choice": signature+=str(run.get_offer().get("token",""))
	if run.mode=="inventory": signature+=str(run.equipped)+str(run.inventory.size())+str(_selected_item)
	var mode_changed := signature!=_last_signature
	if mode_changed:
		_last_signature=signature
		_build_modal(run)
	if run.hero.is_empty(): return
	# Terminal/modal transitions can occur on the same tick as the previous HUD
	# update. Refresh their final values immediately instead of retaining old HP.
	if not mode_changed and run.tick-_last_hud_tick<6 and run.tick>=_last_hud_tick:return
	_last_hud_tick=run.tick
	var g: Dictionary=run.growth.snapshot()
	status.text="생명력 %d / %d   ·   레벨 %d" % [ceili(float(run.hero.hp_raw)/256.0),ceili(float(run.hero.max_hp_raw)/256.0),g.level]
	hp.max_value=run.hero.max_hp_raw;hp.value=run.hero.hp_raw
	var thresholds := [0,6,18,36,60,90,126,168,216,270,330,396]
	var index := mini(int(g.level)-1,11)
	xp.max_value=thresholds[index+1]-thresholds[index] if index<11 else 1
	xp.value=g.xp-thresholds[index] if index<11 else 1
	var texts: Array[String]=[]
	for id_ in skill_labels:skill_labels[id_].text=SKILL_NAMES[id_]+"\n미습득"
	for id_ in g.ranks:
		var d: Dictionary=run.effective_skill(id_)
		texts.append((d.name if d.evolved else SKILL_NAMES.get(id_,id_))+" %d" % d.rank)
		if skill_labels.has(id_):skill_labels[id_].text=(d.name if d.evolved else SKILL_NAMES.get(id_,id_))+"\n"+("진화 · " if d.evolved else "")+"랭크 %d" % d.rank
	skills.text="   /   ".join(texts)
	var elite_alive := false
	for e in run.enemies.values():
		if e.elite and e.hp_raw>0:
			elite_alive=true
			objective.text="회랑 수호자  %d / %d" % [ceili(float(e.hp_raw)/256),ceili(float(e.max_hp_raw)/256)]
	if not elite_alive:
		objective.text="잿빛 회랑  ·  %02d:%02d  ·  %d 처치" % [run.tick/3600,(run.tick/60)%60,run.kills]
	dash.text="Space 회피 준비" if run.tick>=run.get_next_dash_tick() else "회피 %.1f초" % (float(run.get_next_dash_tick()-run.tick)/60)
	debug.text="tick %d · alive %d · projectiles %d · XP %d\nF1 진단 화면" % [run.tick,run.alive_count(),run.projectiles.size(),g.xp]

func notify(text: String) -> void:
	toast.text=text;_toast_left=2.5

func _build_modal(run: RefCounted) -> void:
	for child in modal.get_children():modal.remove_child(child);child.queue_free()
	overlay.visible=run.mode!="playing"
	if not overlay.visible:return
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation",16)
	modal.add_child(box)
	match run.mode:
		"menu":
			box.add_child(_label("잿빛 회랑",40,Color("ddc995")))
			box.add_child(_label("무리를 휩쓸고, 장비와 기술을 성장시켜 회랑 수호자를 처치하세요.",21))
			box.add_child(_label("WASD / 좌클릭 이동 · Space 회피 · 기술 자동 시전 · I 장비 · Esc 정지",17,Color("aabbaf")))
			var classes := HBoxContainer.new()
			classes.add_theme_constant_override("separation",16)
			box.add_child(classes)
			for pair in [["잿불탄","chapter1.skill.ember"],["서리창","chapter1.skill.frost"],["연쇄 전류","chapter1.skill.arc"]]:
				var id_: String=pair[1]
				var b := _button(pair[0]+"으로 시작",func():start.emit(id_))
				b.size_flags_horizontal=Control.SIZE_EXPAND_FILL;classes.add_child(b)
			var spacer := Control.new();spacer.size_flags_vertical=Control.SIZE_EXPAND_FILL;box.add_child(spacer)
			box.add_child(_motion_control())
			box.add_child(_label("회랑 진입전 · 한 장을 완성하기 위한 첫 전투 구간",15,Color("a69a86")))
			if temporary_art:box.add_child(_label("캐릭터와 음향 일부는 제작 중입니다.",14,Color("a6a692")))
		"choice":
			var offer: Dictionary=run.get_offer()
			box.add_child(_label("성장 선택",32,Color("e4d09b")))
			box.add_child(_label("강화할 기술을 선택하세요. 선택하는 동안 전투가 멈춥니다.",17))
			var cards := HBoxContainer.new();cards.add_theme_constant_override("separation",18)
			cards.size_flags_vertical=Control.SIZE_EXPAND_FILL;box.add_child(cards)
			for card in offer.get("cards",[]):
				var panel := PanelContainer.new();panel.size_flags_horizontal=Control.SIZE_EXPAND_FILL
				panel.add_theme_stylebox_override("panel",_style(Color("2a241c"),Color("8f744b")))
				cards.add_child(panel)
				var column := VBoxContainer.new();column.add_theme_constant_override("separation",14);panel.add_child(column)
				var emblem := Emblem.new()
				emblem.custom_minimum_size=Vector2(42,42)
				emblem.element=String(card.get("skill_id","chapter1.skill.ember")).get_slice(".",2)
				emblem.tint={"ember":Color("e88b43"),"frost":Color("8ac8de"),"arc":Color("b5bde4")}.get(emblem.element,Color("bc9a63"))
				column.add_child(emblem)
				column.add_child(_label(card.title,25,Color("e5d19b")))
				column.add_child(_label({"unlock":"새 기술","rank":"기술 강화","passive":"진화 준비","evolve":"기술 진화"}.get(card.kind,""),16,Color("91bca6")))
				column.add_child(_label(_card_description(card,run),17))
				var space := Control.new();space.size_flags_vertical=Control.SIZE_EXPAND_FILL;column.add_child(space)
				var token: String=offer.token
				var card_id: String=card.id
				column.add_child(_button("선택",func():choice.emit(token,card_id)))
		"inventory": _inventory(box,run)
		"paused":
			box.add_child(_label("잠시 멈춤",34))
			box.add_child(_label("전투·발사체·경험치 회수가 정지됐습니다.",18))
			box.add_child(_button("계속하기 [Esc]",func():pause_toggle.emit()))
			box.add_child(_motion_control())
		"victory","defeat":
			box.add_child(_label("회랑 수호자를 처치했습니다" if run.mode=="victory" else "회랑에 쓰러졌습니다",32,Color("e5ca94")))
			box.add_child(_label("%d 처치 · 레벨 %d · 획득 장비 %d개" % [run.kills,run.growth.snapshot().level,run.inventory.size()],20))
			box.add_child(_label("다른 기술과 장비 조합으로 다시 도전할 수 있습니다.",18))
			box.add_child(_button("다시 도전",func():retry.emit()))
			if run.mode=="victory":box.add_child(_button("획득 장비 확인",func():equipment.emit()))

func _motion_control() -> CheckButton:
	var toggle := CheckButton.new();toggle.text="화면 흔들림";toggle.button_pressed=motion_enabled
	toggle.toggled.connect(func(value: bool):motion_enabled=value;motion_toggle.emit(value))
	return toggle

func _card_description(card: Dictionary, run: RefCounted) -> String:
	if card.kind=="passive":return "주력 기술의 진화를 준비합니다.\n최대 랭크와 이 패시브를 갖추면 진화가 선택지에 나타납니다."
	var e: Dictionary=card.get("after",{})
	var rows: Array[String]=[]
	if card.kind=="rank":rows.append("랭크 %d → %d" % [int(card.rank)-1,card.rank])
	if card.kind=="evolve":rows.append("최대 랭크와 선행 패시브 달성")
	rows.append("기술 기본 피해 %d" % (int(e.get("damage_raw",0))/256))
	if e.get("projectiles",0)>0:rows.append("투사체 %d발" % e.projectiles)
	if e.get("chain_targets",0)>0:rows.append("연쇄 %d대상 · %d갈래" % [e.chain_targets,e.branches])
	if e.get("radius_cm",0)>0 and card.skill_id!="chapter1.skill.arc":rows.append("범위 %.1fm" % (float(e.radius_cm)/100))
	if e.get("freeze_stacks",0)>0:rows.append("냉각 누적으로 빙결")
	if e.get("shatter_count",0)>0:rows.append("빙결된 적 처치 시 파쇄")
	if e.get("death_burst",0)>0:rows.append("처치 시 추가 효과")
	return "\n".join(rows)

func _stats(stats: Dictionary) -> String:
	var result: Array[String]=[]
	for id_ in stats:
		var value := int(stats[id_])
		match String(id_):
			"damage_bps":result.append("피해 +%.1f%%" % (float(value)/100))
			"max_hp_raw":result.append("최대 생명력 +%d" % (value/256))
			"damage_reduction_bps":result.append("받는 피해 -%.1f%%" % (float(value)/100))
			"projectiles":result.append("발사체 +%d (연쇄 기술은 대상 +%d)" % [value,value])
			"chain_targets":result.append("연쇄 전류 대상 +%d" % value)
			"shatter_count":result.append("서리창 랭크4 / 진화의 파쇄 파편 +%d" % value)
			"pickup_radius_cm":result.append("회수 반경 +%.1fm" % (float(value)/100))
			"cooldown_bps":result.append("기술 주기 단축 +%.1f%%" % (float(value)/100))
	return "\n".join(result) if not result.is_empty() else "장착 장비 없음"

func _inventory(box: VBoxContainer, run: RefCounted) -> void:
	box.add_child(_label("장비와 전투 선택",30,Color("e2d09c")))
	var rows := HBoxContainer.new();rows.add_theme_constant_override("separation",24);rows.size_flags_vertical=Control.SIZE_EXPAND_FILL;box.add_child(rows)
	var scroll := ScrollContainer.new();scroll.custom_minimum_size.x=300;rows.add_child(scroll)
	var list := VBoxContainer.new();list.size_flags_horizontal=Control.SIZE_EXPAND_FILL;scroll.add_child(list)
	if run.inventory.is_empty():list.add_child(_label("장비를 발견하면 가까이 다가가 획득하세요.",18))
	for item in run.inventory:
		var uid: int=item.uid
		var equipped: bool=run.equipped.get(item.slot,-1)==uid
		list.add_child(_button(("✓ " if equipped else "")+item.name,func():_selected_item=uid;_last_signature=""))
	if _selected_item<0 and not run.inventory.is_empty():_selected_item=run.inventory[0].uid
	var comparison := HBoxContainer.new();comparison.add_theme_constant_override("separation",18);comparison.size_flags_horizontal=Control.SIZE_EXPAND_FILL;rows.add_child(comparison)
	var data: Dictionary=run.compare_item(_selected_item)
	if not data.is_empty():
		for pair in [["현재 장비",data.equipped],["선택한 장비",data.candidate]]:
			var column := VBoxContainer.new();column.size_flags_horizontal=Control.SIZE_EXPAND_FILL;comparison.add_child(column)
			var item: Dictionary=pair[1]
			column.add_child(_label(pair[0],18,Color("8fada1")))
			column.add_child(_label(item.get("name","장착 장비 없음"),23,Color("dec993")))
			column.add_child(_label(_stats(item.get("stats",{})),17))
			if pair[0]=="선택한 장비":
				var uid: int=item.uid
				column.add_child(_button("장착",func():equip_item.emit(uid)))
	box.add_child(_button("전투로 돌아가기 [I]",func():close_equipment.emit()))

func invalidate() -> void:
	_last_signature="";_last_hud_tick=-99

func reset() -> void:
	_selected_item=-1;invalidate()
