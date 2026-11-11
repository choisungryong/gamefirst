extends "res://chapter1/view/chapter_hud_quality36.gd"
## Presentation successor only: inherited signals, saves, rewards and scrolling.
const LifeSeal38=preload("res://chapter1/view/ui38/life_seal.gd")
const ElementSeal38=preload("res://chapter1/view/ui38/element_seal.gd")
const BRASS38=Color("aa8d58")
var life_seal38: Control
var level38: Label
var _focus_return38: WeakRef

func _style(color: Color, border: Color=BRASS38) -> StyleBoxFlat:
	# Normalize the inherited warm surfaces to carbonized stone; rarity remains.
	var surface := color
	if color.r>color.b*1.12 and color.r<0.34:surface=Color("17191b")
	var s := StyleBoxFlat.new()
	s.bg_color=surface;s.border_color=border;s.set_border_width_all(1)
	s.set_content_margin_all(20)
	s.border_width_top=2
	s.shadow_color=Color(0,0,0,.45);s.shadow_size=8;s.shadow_offset=Vector2(0,4)
	return s

func _button(text: String, action: Callable) -> Button:
	var b := Button.new();b.text=text;b.custom_minimum_size.y=48
	b.add_theme_font_size_override("font_size",18)
	b.add_theme_color_override("font_color",Color("e7dfc9"))
	b.add_theme_color_override("font_disabled_color",Color("777a78"))
	for entry in [["normal","202628","665c46"],["hover","303a3d","c8ae76"],["pressed","111719","e7dfc9"],["disabled","191d1f","3e4343"]]:
		var s := _style(Color(entry[1]),Color(entry[2]));s.set_content_margin_all(12)
		b.add_theme_stylebox_override(entry[0],s)
	var focus := StyleBoxFlat.new();focus.bg_color=Color(0,0,0,0);focus.border_color=Color("f1d6a1");focus.set_border_width_all(3)
	b.add_theme_stylebox_override("focus",focus)
	b.pressed.connect(action)
	return b

func setup(view: Node3D) -> void:
	super.setup(view)
	root.theme.default_font_size=19
	# Reuse the live labels and bars; only replace their layout containers.
	var old_top := objective.get_parent().get_parent()
	var old_bottom := status.get_parent().get_parent().get_parent()
	var top := HBoxContainer.new();top.set_anchors_and_offsets_preset(Control.PRESET_TOP_WIDE)
	top.offset_left=28;top.offset_right=-28;top.offset_top=22;top.add_theme_constant_override("separation",10)
	root.add_child(top)
	objective.reparent(top);objective.custom_minimum_size.x=480
	objective.add_theme_font_size_override("font_size",19)
	for child in old_top.get_child(0).get_children():
		if child is Button:child.reparent(top)
	old_top.queue_free()
	var dock := HBoxContainer.new();dock.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	dock.offset_left=28;dock.offset_right=-28;dock.offset_top=-142;dock.offset_bottom=-22
	dock.add_theme_constant_override("separation",22);root.add_child(dock)
	life_seal38=LifeSeal38.new();dock.add_child(life_seal38)
	var vital := VBoxContainer.new();vital.custom_minimum_size.x=255;vital.alignment=BoxContainer.ALIGNMENT_CENTER;dock.add_child(vital)
	status.reparent(vital);status.add_theme_font_size_override("font_size",18)
	hp.reparent(vital);hp.custom_minimum_size.y=8
	level38=_label("",16,Color("b5b0a3"));vital.add_child(level38)
	xp.reparent(vital);xp.custom_minimum_size.y=5
	var sigils := old_bottom.get_child(0).get_child(1)
	sigils.reparent(dock)
	for chip in sigils.get_children():
		chip.custom_minimum_size.x=175
		for child in chip.get_children():
			if child is Label:child.custom_minimum_size.x=120;child.add_theme_font_size_override("font_size",18)
	dash.reparent(dock);dash.custom_minimum_size.x=195;dash.add_theme_font_size_override("font_size",18)
	old_bottom.queue_free()
	# Keep overlays above the replacement dock, and retain boss/toast layering.
	root.move_child(overlay,root.get_child_count()-1)
	modal.offset_left=90;modal.offset_right=-90;modal.offset_top=104;modal.offset_bottom=-76
	modal.add_theme_stylebox_override("panel",_style(Color("17191b"),BRASS38))
	overlay.color=Color(.025,.035,.045,.87)

func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	if run.hero.is_empty():return
	life_seal38.fraction=float(run.hero.hp_raw)/maxf(1,float(run.hero.max_hp_raw))
	status.text="생명  %d / %d"%[ceili(float(run.hero.hp_raw)/256),ceili(float(run.hero.max_hp_raw)/256)]
	var growth: Dictionary=run.growth.snapshot()
	level38.text="레벨 %d    경험치 %d / %d"%[growth.level,int(xp.value),int(xp.max_value)]

func _build_modal(run: RefCounted) -> void:
	var previous := overlay.visible
	if not previous:
		var owner := root.get_viewport().gui_get_focus_owner()
		if owner!=null:_focus_return38=weakref(owner)
	super._build_modal(run)
	if overlay.visible:
		if run.mode=="choice" and not stash_open:_growth_cards38(run)
		_decorate38(modal)
		_focus_modal38.call_deferred()
	elif previous and _focus_return38!=null:
		var owner = _focus_return38.get_ref()
		if is_instance_valid(owner):owner.grab_focus.call_deferred()

func _growth_cards38(run: RefCounted) -> void:
	# Preserve the authoritative token/card callbacks built by the inherited HUD.
	var box := modal.get_child(0)
	var cards := box.get_child(2)
	var offer: Dictionary=run.get_offer()
	for i in cards.get_child_count():
		var panel := cards.get_child(i)
		var card: Dictionary=offer.cards[i]
		var element := String(card.get("skill_id","")).get_slice(".",2)
		var tint: Color={"ember":Color("e8a05a"),"frost":Color("7cc9d9"),"arc":Color("abb8ec")}.get(element,BRASS38)
		var frame := _style(Color("202628"),tint.darkened(.35));frame.border_width_top=4
		panel.add_theme_stylebox_override("panel",frame)
		var column := panel.get_child(0)
		var old_icon := column.get_child(0)
		column.remove_child(old_icon);old_icon.queue_free()
		var crest := ElementSeal38.new();crest.element=element;crest.tint=tint
		column.add_child(crest);column.move_child(crest,0)
		column.get_child(2).add_theme_color_override("font_color",tint)
		column.get_child(3).add_theme_font_size_override("font_size",19)
		var button := column.get_child(column.get_child_count()-1)
		button.text="서약 선택"

func _inventory(box: VBoxContainer,run: RefCounted) -> void:
	super._inventory(box,run)
	# Give the two truthful comparison columns their own stone tablets.
	var comparison := box.get_child(1).get_child(1)
	var data: Dictionary=run.compare_item(_selected_item)
	if not data.is_empty():
		var difference: Dictionary={}
		var current: Dictionary=data.equipped.get("stats",{})
		var candidate: Dictionary=data.candidate.get("stats",{})
		for key in candidate:
			var value := int(candidate[key])-int(current.get(key,0))
			if value!=0:difference[key]=value
		for key in current:
			if not candidate.has(key) and int(current[key])!=0:difference[key]=-int(current[key])
		var chosen := comparison.get_child(1)
		chosen.add_child(_label("장착 시 변화",16,Color("b5b0a3")))
		chosen.add_child(_label(_delta_text38(difference),16,Color("e7dfc9")))
	for column in comparison.get_children():
		var panel := PanelContainer.new();panel.size_flags_horizontal=Control.SIZE_EXPAND_FILL
		panel.add_theme_stylebox_override("panel",_style(Color("202628"),BRASS38))
		comparison.add_child(panel)
		var details := ScrollContainer.new();details.size_flags_horizontal=Control.SIZE_EXPAND_FILL;details.size_flags_vertical=Control.SIZE_EXPAND_FILL
		details.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
		panel.add_child(details);column.reparent(details)

func _delta_text38(stats: Dictionary) -> String:
	if stats.is_empty():return "능력치 변화 없음"
	# Existing formatter owns units and vocabulary; normalize signed negative cases.
	var text := _stats(stats)
	text=text.replace("--","+").replace("+-","-")
	return text

func _decorate38(node: Node) -> void:
	# Inherited card/equipment structure and callbacks are retained verbatim.
	for child in node.get_children():
		if child is PanelContainer and child!=modal and not child.has_theme_stylebox_override("panel"):
			child.add_theme_stylebox_override("panel",_style(Color("202628"),BRASS38))
		_decorate38(child)

func _focus_modal38() -> void:
	if not overlay.visible:return
	var buttons: Array[Control]=[]
	_collect_focus38(modal,buttons)
	if buttons.is_empty():return
	for i in buttons.size():
		var b := buttons[i]
		b.focus_next=b.get_path_to(buttons[(i+1)%buttons.size()])
		b.focus_previous=b.get_path_to(buttons[(i+buttons.size()-1)%buttons.size()])
	buttons[0].grab_focus()

func _collect_focus38(node: Node,items: Array[Control]) -> void:
	for child in node.get_children():
		if child is BaseButton and not child.disabled:items.append(child)
		_collect_focus38(child,items)
