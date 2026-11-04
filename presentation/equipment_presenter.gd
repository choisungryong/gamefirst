extends RefCounted
## Output and button routing only. Inventory, validation and save authority stay
## in the simulation. Containers keep the bounded inventory inside one modal.
## https://docs.godotengine.org/en/4.5/classes/class_scrollcontainer.html
const SLOT_NAMES := {"focus":"주무기","body":"몸통","charm":"부적"}
var view: Node
var panel: Control
var card: PanelContainer
var context_label: Label
var notice_label: Label
var items_box: VBoxContainer
var item_buttons: Array[Button] = []
var slot_buttons: Dictionary = {}
var save_button: Button
var load_button: Button
var close_button: Button

func setup(owner_view: Node, ui: Control) -> void:
	view = owner_view
	panel = Control.new()
	panel.name = "EquipmentModal"
	panel.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	ui.add_child(panel)
	var shade := ColorRect.new()
	shade.color = Color(0,0,0,.65)
	shade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	shade.mouse_filter = Control.MOUSE_FILTER_STOP
	panel.add_child(shade)
	card = PanelContainer.new()
	card.name = "EquipmentCard"
	card.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	card.offset_left = -430
	card.offset_top = -340
	card.offset_right = 430
	card.offset_bottom = 340
	card.add_theme_stylebox_override("panel",view.style(Color(.045,.08,.075,.99),Color("8c9785")))
	panel.add_child(card)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation",12)
	card.add_child(box)
	var heading := HBoxContainer.new()
	box.add_child(heading)
	var title: Label = view.label("장비와 소지품",26,Color("e6d6b8"))
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	heading.add_child(title)
	close_button = view.button("닫기 [I / Esc]",view.toggle_equipment)
	heading.add_child(close_button)
	context_label = view.label("",15,Color("bdd0d7"))
	box.add_child(context_label)
	var slots := HBoxContainer.new()
	slots.add_theme_constant_override("separation",10)
	box.add_child(slots)
	for slot in SLOT_NAMES:
		var slot_button: Button = view.button("",perform.bind("unequip",slot))
		slot_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		slot_buttons[slot] = slot_button
		slots.add_child(slot_button)
	var scroll := ScrollContainer.new()
	scroll.name = "EquipmentItemsScroll"
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	box.add_child(scroll)
	items_box = VBoxContainer.new()
	items_box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	items_box.add_theme_constant_override("separation",10)
	scroll.add_child(items_box)
	notice_label = view.label("장비 변경은 현재 생명과 마나를 회복하지 않습니다.",15,Color("c6d9c3"))
	notice_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	notice_label.custom_minimum_size.y = 44
	box.add_child(notice_label)
	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation",10)
	box.add_child(actions)
	save_button = view.button("성장과 장비 저장",perform.bind("save",null))
	load_button = view.button("성장 기록 불러오기",perform.bind("load",null))
	save_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	load_button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	actions.add_child(save_button)
	actions.add_child(load_button)
	var footer: Label = view.label("전투 일시 정지 · R은 성장과 장비를 유지하며 바닥 보상을 비웁니다.",13,Color("acb7a9"))
	box.add_child(footer)
	panel.hide()

func is_open() -> bool:
	return panel != null and panel.visible

func open() -> void:
	refresh()
	notice_label.text = "장비 변경은 현재 생명과 마나를 회복하지 않습니다."
	notice_label.add_theme_color_override("font_color",Color("c6d9c3"))
	panel.show()
	close_button.grab_focus()

func close() -> void:
	panel.hide()
	var focused: Control = view.get_viewport().gui_get_focus_owner()
	if focused and panel.is_ancestor_of(focused): focused.release_focus()

func refresh() -> void:
	for child in items_box.get_children():
		items_box.remove_child(child)
		child.queue_free()
	item_buttons.clear()
	var ready: bool = view.sim.has_method("equipment_items") and bool(view.sim.get("equipment_valid"))
	var items: Array = view.sim.equipment_items() if ready else []
	var context: Dictionary = view.sim.equipment_context() if ready else {}
	var progression: Dictionary = view.sim.progression_snapshot()
	var next_xp := str(progression.get("next_level_xp",0)) if int(progression.get("next_level_xp",0)) > 0 else "최고 레벨"
	context_label.text = "시전자 · 레벨 %d · 경험치 %d · 다음 %s · 소지품 %d / 64" % [int(context.get("level",1)),int(progression.get("xp",0)),next_xp,items.size()]
	for slot in SLOT_NAMES:
		var equipped_name := ""
		for item in items:
			if item.slot == slot and item.equipped: equipped_name = item.display_name
		var slot_button: Button = slot_buttons[slot]
		slot_button.text = SLOT_NAMES[slot]+(" · 해제" if not equipped_name.is_empty() else " · 비어 있음")
		slot_button.tooltip_text = equipped_name
		slot_button.disabled = equipped_name.is_empty()
	for item in items:
		add_item(item)
	if items.is_empty(): items_box.add_child(view.label("소지한 장비가 없습니다." if ready else "장비를 사용할 수 없습니다.",17))
	save_button.disabled = not ready
	load_button.disabled = not ready

func add_item(item: Dictionary) -> void:
	var row := PanelContainer.new()
	var row_style: StyleBoxFlat = view.style(Color(.09,.14,.12,.97),Color("48594d"))
	row_style.set_content_margin_all(14)
	row.add_theme_stylebox_override("panel",row_style)
	items_box.add_child(row)
	var content := HBoxContainer.new()
	content.add_theme_constant_override("separation",12)
	row.add_child(content)
	var description := VBoxContainer.new()
	description.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	description.add_theme_constant_override("separation",5)
	content.add_child(description)
	var name_: Label = view.label(String(item.display_name)+("  · 장착 중" if item.equipped else ""),19,Color("edc78f"))
	name_.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	description.add_child(name_)
	var requirement := "%s · 필요 레벨 %d" % [SLOT_NAMES.get(String(item.slot),"장비"),int(item.minimum_level)]
	if not item.eligible: requirement += " · 지금은 장착할 수 없습니다"
	description.add_child(view.label(requirement,14,Color("bdd0d7") if item.eligible else Color("e7ad91")))
	var effects: Array[String] = []
	for modifier in item.modifiers: effects.append(modifier_text(modifier))
	var effects_label: Label = view.label(" · ".join(effects),15)
	effects_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	description.add_child(effects_label)
	if not item.affix_names.is_empty():
		var affixes: Label = view.label("옵션: "+" · ".join(item.affix_names),13,Color("acb7a9"))
		affixes.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		description.add_child(affixes)
	var item_button: Button = view.button("해제" if item.equipped else "장착",perform.bind("unequip" if item.equipped else "equip",item.slot if item.equipped else int(item.uid)))
	item_button.custom_minimum_size.x = 120
	item_button.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	item_button.disabled = not item.eligible and not item.equipped
	item_button.set_meta("item_uid",int(item.uid))
	content.add_child(item_button)
	item_buttons.append(item_button)

func modifier_text(modifier: Dictionary) -> String:
	var id_: String = modifier.stat_id
	var value: float = float(modifier.value)
	var sign_: String = "+" if value >= 0 else ""
	var names := {"stat.health":"최대 생명","stat.mana":"최대 마나","stat.spell_power":"주문 피해","stat.cast_speed":"시전 속도","stat.mana_cost":"마나 소모","stat.flat_reduction":"받는 피해 감소","stat.resist.fire":"화염 저항","stat.resist.cold":"냉기 저항","stat.resist.lightning":"번개 저항","stat.resist.physical":"물리 저항","stat.skill.ember_level":"화염탄"}
	var name_: String = names.get(id_,"능력치 보너스")
	if String(modifier.operation) == "percent_bps": return "%s %s%s%%" % [name_,sign_,view.quantity_text(value/100.0)]
	var definition: Dictionary = view.sim.catalog.definition("stats",id_)
	if not names.has(id_) and definition.get("display_name") is String and not String(definition.display_name).is_empty() and String(definition.display_name).length() <= 64: name_ = definition.display_name
	var unit: String = String(definition.get("unit",""))
	var scale: float = float(definition.get("scale",0))
	if unit == "count" and scale == 1: return "%s %s%d" % [name_,sign_,int(value)]
	if unit in ["health","mana"] and scale > 0: return "%s %s%s" % [name_,sign_,view.quantity_text(value/scale)]
	if unit == "basis_points" and scale == 10000: return "%s %s%s%%" % [name_,sign_,view.quantity_text(value/100.0)]
	return "효과 정보를 표시할 수 없습니다."

func perform(action: String, value: Variant) -> void:
	if not is_open(): return
	var success := false
	var message := ""
	match action:
		"equip":
			success = view.sim.equip_item(int(value))
			message = "장비를 장착했습니다." if success else "장착할 수 없습니다. 현재 장비는 유지됩니다."
		"unequip":
			success = view.sim.unequip_item(String(value))
			message = "장비를 해제했습니다." if success else "장비를 해제하지 못했습니다. 현재 장비는 유지됩니다."
		"save":
			success = view.sim.save_progress()
			message = "성장·장비·바닥 보상을 저장했습니다." if success else "저장하지 못했습니다. 이전 저장 기록은 유지됩니다."
		"load":
			success = view.sim.load_progress()
			if success: view.progress_loaded()
			message = "성장 기록을 불러왔습니다. 현재 생명과 마나는 유지됩니다." if success else "저장 기록을 불러오지 못했습니다. 현재 상태는 유지됩니다."
		_: return
	refresh()
	notice_label.text = message
	notice_label.add_theme_color_override("font_color",Color("c6d9c3") if success else Color("e7ad91"))
	view.sync_equipment_hud()
	# Optional presentation feedback; the Sim has already decided the outcome.
	if view.has_method("equipment_action_completed"):
		view.equipment_action_completed(action,success)
