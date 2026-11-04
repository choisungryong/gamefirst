extends "res://chapter1/view/chapter_hud_quality17.gd"
## Discovery follows actual inventory receipts, without granting or auto-equipping.
## Starter gear is seeded silently; at most one magic and one rare per slot.
var _discovery20_seeded := false
var _discovery20_magic := false
var _discovery20_slots: Dictionary={}
var _discovery20_uids: Dictionary={}
var _discovery20_queue: Array[Dictionary]=[]
var _discovery20_gap := 0.0
var _discovery20_name := ""
var discovery20_history: Array[Dictionary]=[]
func sync(run: RefCounted,delta: float) -> void:
	if run.mode=="playing":
		if _discovery20_seeded:
			for item in run.inventory:
				if not _seen_gear.has(item.uid):_queue_discovery20(item)
		else:
			_discovery20_seeded=true
			for item in run.inventory:_discovery20_uids[item.uid]=true
	super.sync(run,delta)
	if run.mode!="playing":return
	_discovery20_gap=maxf(0,_discovery20_gap-delta)
	if _discovery_left<=0 and _discovery20_gap<=0 and not _discovery20_queue.is_empty():
		_present_discovery20(_discovery20_queue.pop_front())
	_discovery.visible=_discovery_left>0
	if _discovery.visible:
		_discovery.modulate.a=minf(clampf((3.2-_discovery_left)/.18,0,1),clampf(_discovery_left/.4,0,1))
		if toast.text.begins_with("획득:") and toast.text.contains(_discovery20_name):toast.visible=false
func _show_discovery(item: Dictionary) -> void:
	_queue_discovery20(item)
func _queue_discovery20(item: Dictionary) -> void:
	if _discovery20_uids.has(item.uid):return
	var quality: String=item.get("quality","common")
	if quality=="magic":
		if _discovery20_magic:return
		_discovery20_magic=true
	elif quality=="rare":
		if _discovery20_slots.has(item.slot):return
		_discovery20_slots[item.slot]=true
	elif quality!="unique":return
	_discovery20_uids[item.uid]=true
	if _discovery20_queue.size()>=4:
		if quality!="unique":return
		_discovery20_queue.pop_back()
	if quality=="unique":_discovery20_queue.push_front(item.duplicate(true))
	else:_discovery20_queue.append(item.duplicate(true))
func _present_discovery20(item: Dictionary) -> void:
	for child in _discovery.get_children():_discovery.remove_child(child);child.queue_free()
	var color: Color=QUALITY_COLORS.get(item.quality,Color.WHITE)
	_discovery.offset_bottom=_discovery.offset_top+104
	_discovery.add_theme_stylebox_override("panel",_style(Color(.055,.06,.065,.97),color.darkened(.2)))
	var row := HBoxContainer.new();row.add_theme_constant_override("separation",16);_discovery.add_child(row)
	row.add_child(_sigil(item));var column := VBoxContainer.new();column.size_flags_horizontal=Control.SIZE_EXPAND_FILL;row.add_child(column)
	var header := "고유 장비 획득" if item.quality=="unique" else ("첫 희귀 장비" if item.quality=="rare" else "첫 마법 장비")
	var header_label := _label(header+" · "+SLOT_NAMES[item.slot],14,color);header_label.autowrap_mode=TextServer.AUTOWRAP_OFF;column.add_child(header_label)
	var name_label := _label(item.name,22,Color("eee4cf"));name_label.custom_minimum_size.x=410;name_label.autowrap_mode=TextServer.AUTOWRAP_OFF;name_label.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS;name_label.tooltip_text=item.name;column.add_child(name_label)
	var hint := _label("[I] 장비 능력 비교 · 장착",14,Color("bcb5a5"));hint.autowrap_mode=TextServer.AUTOWRAP_OFF;column.add_child(hint)
	_settle_discovery20(row)
	_discovery_left=3.2;_discovery20_gap=4.4
	_discovery20_name=item.name
	discovery20_history.append({"uid":item.uid,"quality":item.quality,"slot":item.slot,"name":item.name})
func _settle_discovery20(row: Control) -> void:
	# A temporary wrapped-label minimum can enlarge a PanelContainer; smaller
	# children do not automatically shrink its previous rect after replacement.
	for i in 2:await root.get_tree().process_frame
	if is_instance_valid(row) and row.get_parent()==_discovery:_discovery.offset_bottom=_discovery.offset_top+104
func reset() -> void:
	super.reset();_discovery20_seeded=false;_discovery20_magic=false;_discovery20_slots.clear();_discovery20_uids.clear();_discovery20_queue.clear();_discovery20_gap=0;_discovery20_name="";discovery20_history.clear()
