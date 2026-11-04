extends "res://chapter1/view/chapter_hud_quality16.gd"
const Sigil=preload("res://chapter1/view/equipment_sigil_quality17.gd")
const QUALITY_COLORS={"common":Color("c4c0ad"),"magic":Color("91bbd4"),"rare":Color("e0c47e"),"unique":Color("efac59")}
const QUALITY_NAMES={"common":"일반","magic":"마법","rare":"희귀","unique":"고유"}
var _gear_scroll: ScrollContainer
var _scroll_position := 0
var _scroll_ready := false
var _victory_age := 0.0
var _previous_mode := ""
var _seen_gear: Dictionary={}
var _discovery: PanelContainer
var _discovery_left := 0.0
func setup(view: Node3D) -> void:
	super.setup(view)
	_discovery=PanelContainer.new();_discovery.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	_discovery.offset_left=-255;_discovery.offset_right=255;_discovery.offset_top=112
	_discovery.add_theme_stylebox_override("panel",_style(Color(.07,.08,.08,.95),Color("c88b46")))
	_discovery.mouse_filter=Control.MOUSE_FILTER_IGNORE;_discovery.visible=false;root.add_child(_discovery)
func sync(run: RefCounted,delta: float) -> void:
	if run.mode=="victory":
		if _previous_mode not in ["victory","inventory"]:_victory_age=0
		_victory_age+=maxf(delta,0)
	_previous_mode=run.mode
	super.sync(run,delta)
	if run.mode=="victory" and not stash_open:overlay.visible=_victory_age>=1.3
	if run.mode=="playing":
		_discovery_left=maxf(0,_discovery_left-delta)
		for item in run.inventory:
			if _seen_gear.has(item.uid):continue
			_seen_gear[item.uid]=true
			if item.quality=="unique":_show_discovery(item)
	_discovery.visible=_discovery_left>0 and run.mode=="playing"
func _show_discovery(item: Dictionary) -> void:
	for child in _discovery.get_children():_discovery.remove_child(child);child.queue_free()
	var row := HBoxContainer.new();row.add_theme_constant_override("separation",16);_discovery.add_child(row)
	row.add_child(_sigil(item));var text := VBoxContainer.new();row.add_child(text)
	text.add_child(_label("고유 장비 발견 · "+SLOT_NAMES[item.slot],14,Color("efac59")))
	text.add_child(_label(item.name,23,Color("efd0a0")));_discovery_left=3.0
func _sigil(item: Dictionary) -> Control:
	var icon := Sigil.new();icon.slot=item.get("slot","charm");icon.tint=QUALITY_COLORS.get(item.get("quality","common"),Color.WHITE);return icon
func _build_modal(run: RefCounted) -> void:
	if is_instance_valid(_gear_scroll) and _scroll_ready:_scroll_position=_gear_scroll.scroll_vertical
	_scroll_ready=false
	_gear_scroll=null
	super._build_modal(run)
	if run.mode=="victory" and not stash_open:
		var box: VBoxContainer=modal.get_child(0)
		for item in run.inventory:
			if int(item.uid)!=int(run._elite_reward_uid):continue
			var panel := PanelContainer.new();panel.add_theme_stylebox_override("panel",_style(Color("28231b"),Color("b98140")))
			var row := HBoxContainer.new();row.add_theme_constant_override("separation",16);panel.add_child(row);row.add_child(_sigil(item))
			var column := VBoxContainer.new();column.size_flags_horizontal=Control.SIZE_EXPAND_FILL;row.add_child(column)
			column.add_child(_label("파수왕의 유산 · 고유 장비",14,Color("efac59")))
			column.add_child(_label(item.name,24,Color("f0d3a0")))
			column.add_child(_label(item.get("description",""),16))
			box.add_child(panel);box.move_child(panel,2)
func _inventory(box: VBoxContainer,run: RefCounted) -> void:
	box.add_child(_label("장비와 전투 선택",30,Color("e2d09c")))
	var rows := HBoxContainer.new();rows.add_theme_constant_override("separation",24);rows.size_flags_vertical=Control.SIZE_EXPAND_FILL;box.add_child(rows)
	_gear_scroll=ScrollContainer.new();_gear_scroll.custom_minimum_size.x=300;_gear_scroll.size_flags_vertical=Control.SIZE_EXPAND_FILL;rows.add_child(_gear_scroll)
	_gear_scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED
	var list := VBoxContainer.new();list.size_flags_horizontal=Control.SIZE_EXPAND_FILL;_gear_scroll.add_child(list)
	if run.inventory.is_empty():list.add_child(_label("장비를 발견하면 가까이 다가가 획득하세요.",18))
	for item in run.inventory:
		var uid: int=item.uid;var active: bool=run.equipped.get(item.slot,-1)==uid
		var b := _button(("◆ " if active else "")+item.name,func():_selected_item=uid;invalidate())
		b.alignment=HORIZONTAL_ALIGNMENT_LEFT;b.add_theme_color_override("font_color",QUALITY_COLORS.get(item.quality,Color.WHITE))
		b.add_theme_font_size_override("font_size",15);b.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS
		b.tooltip_text=SLOT_NAMES[item.slot]+" · "+QUALITY_NAMES[item.quality]+"\n"+item.name;list.add_child(b)
	_restore_scroll(_gear_scroll,_scroll_position)
	if _selected_item<0 and not run.inventory.is_empty():_selected_item=run.inventory[0].uid
	var comparison := HBoxContainer.new();comparison.add_theme_constant_override("separation",20);comparison.size_flags_horizontal=Control.SIZE_EXPAND_FILL;rows.add_child(comparison)
	var data: Dictionary=run.compare_item(_selected_item)
	if not data.is_empty():
		for pair in [["현재 장비",data.equipped],["선택한 장비",data.candidate]]:
			var column := VBoxContainer.new();column.size_flags_horizontal=Control.SIZE_EXPAND_FILL;column.custom_minimum_size.x=235;comparison.add_child(column)
			var item: Dictionary=pair[1]
			column.add_child(_label(pair[0],16,Color("99b9b0")))
			if not item.is_empty():column.add_child(_sigil(item))
			column.add_child(_label(item.get("name","장착 장비 없음"),22,QUALITY_COLORS.get(item.get("quality","common"),Color.WHITE)))
			if not item.is_empty():column.add_child(_label(SLOT_NAMES[item.slot]+" · "+QUALITY_NAMES[item.quality],14,Color("b7b0a1")))
			column.add_child(_label(_stats(item.get("stats",{})),16))
			if not item.get("description","").is_empty():column.add_child(_label(item.description,16,Color("e6c48e")))
			if pair[0]=="선택한 장비" and not item.is_empty():
				var uid: int=item.uid;column.add_child(_button("장착",func():equip_item.emit(uid)))
	box.add_child(_button("돌아가기 [I]",func():close_equipment.emit()))
func _restore_scroll(scroll: ScrollContainer,position_: int) -> void:
	# A deferred property assignment can run before containers have computed
	# the new list range and get clamped to zero. Restore after layout settles.
	for i in 2:await root.get_tree().process_frame
	if is_instance_valid(scroll) and scroll==_gear_scroll:
		scroll.scroll_vertical=position_;_scroll_ready=true
func _stats(stats: Dictionary) -> String:
	return super._stats(stats).replace("파쇄 파편 (빙결 필요)","파쇄 대상 (빙결 / 진화 냉기 처치)")
func reset() -> void:
	super.reset();_gear_scroll=null;_scroll_position=0;_scroll_ready=false;_victory_age=0;_previous_mode="";_seen_gear.clear();_discovery_left=0
