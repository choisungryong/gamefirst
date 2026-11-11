extends "res://chapter1/view/ui38/chapter_hud_quality38.gd"
## Read-only presentation successor. All gear/save transitions retain the
## inherited signals; filters never change profile_state or run inventory.
var _stash_slot40 := ""
var _stash_quality40 := ""
var _stash_sort40 := 0
var _stash_scroll40: ScrollContainer
var _stash_offset40 := 0
var _stash_reset_scroll40 := false
var _route40: PanelContainer
var _route_labels40: Array[Label]=[]
var _route_hint40: Label

func setup(view: Node3D) -> void:
	super.setup(view)
	_route40=_backplate38();_route40.name="ChapterRoute40"
	_route40.position=Vector2(28,128);_route40.custom_minimum_size.x=500
	root.add_child(_route40)
	var column := VBoxContainer.new();column.add_theme_constant_override("separation",5);_route40.add_child(column)
	var row := HBoxContainer.new();row.add_theme_constant_override("separation",8);column.add_child(row)
	for i in 3:
		if i>0:
			var separator := _label("›",16,Color("716c60"));separator.autowrap_mode=TextServer.AUTOWRAP_OFF;row.add_child(separator)
		var entry := _label("",15);entry.mouse_filter=Control.MOUSE_FILTER_IGNORE
		entry.autowrap_mode=TextServer.AUTOWRAP_OFF
		row.add_child(entry);_route_labels40.append(entry)
	_route_hint40=_label("",14,Color("c4bcaa"));_route_hint40.autowrap_mode=TextServer.AUTOWRAP_OFF;column.add_child(_route_hint40)
	root.move_child(overlay,root.get_child_count()-1)

func sync(run: RefCounted,delta: float) -> void:
	var overlay_was_visible := overlay.visible
	super.sync(run,delta)
	# HUD17 reveals victory after 1.3s, after the initial deferred focus has
	# already returned while hidden. Focus once on the actual reveal edge.
	if run.mode=="victory" and not stash_open and overlay.visible and not overlay_was_visible:
		_focus_modal38.call_deferred()
	_route40.visible=not run.hero.is_empty() and run.mode=="playing"
	if not _route40.visible:return
	var goal: Dictionary=run.objective()
	for i in 3:
		var cleared: bool=i<run.seals.size() and bool(run.seals[i].get("cleared",false))
		var current: bool=i==int(goal.zone)
		_route_labels40[i].text=("✓ " if cleared else ("◆ " if current else "○ "))+String(run.ZONE_NAMES[i])
		_route_labels40[i].add_theme_color_override("font_color",Color("a8baaa") if cleared else (Color("efdaa6") if current else Color("85877f")))
	if not bool(goal.entered):
		var destination: Vector2=goal.destination
		_route_hint40.text="다음 봉인까지 %.0fm · 열린 동쪽 회랑을 따라 이동"%run.hero.position.distance_to(destination)
	else:_route_hint40.text="마지막 봉인 · 회랑의 파수왕을 처치하세요" if int(goal.boss_phase)>0 else "현재 구역의 봉인을 돌파하세요"

func _build_modal(run: RefCounted) -> void:
	super._build_modal(run)
	if not stash_open and run.mode in ["victory","defeat"]:
		_build_result40(run)
		modal.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
		modal.offset_left=-620;modal.offset_right=620;modal.offset_top=-260;modal.offset_bottom=260
		_focus_modal38.call_deferred()

func _clear_modal40() -> VBoxContainer:
	for child in modal.get_children():modal.remove_child(child);child.queue_free()
	var box := VBoxContainer.new();box.add_theme_constant_override("separation",12);modal.add_child(box)
	return box

func _filter40(values: Array,names: Array,current: int,change: Callable) -> OptionButton:
	var option := OptionButton.new();option.custom_minimum_size=Vector2(170,42)
	for state in ["normal","hover","pressed","disabled"]:
		var compact := _style(Color("202628"),Color("665c46"));compact.content_margin_top=8;compact.content_margin_bottom=8
		compact.content_margin_left=12;compact.content_margin_right=12
		option.add_theme_stylebox_override(state,compact)
	var focus := StyleBoxFlat.new();focus.bg_color=Color.TRANSPARENT
	focus.border_color=Color("f1d6a1");focus.set_border_width_all(3)
	option.add_theme_stylebox_override("focus",focus)
	for name_ in names:option.add_item(String(name_))
	option.select(current)
	option.item_selected.connect(func(index: int):change.call(values[index]))
	return option

func _stash_records40() -> Array[Dictionary]:
	var result: Array[Dictionary]=[]
	for record in profile_state.get("items",[]):
		var item: Dictionary=record.item
		if not _stash_slot40.is_empty() and item.slot!=_stash_slot40:continue
		if not _stash_quality40.is_empty() and item.quality!=_stash_quality40:continue
		result.append(record)
	result.sort_custom(func(a: Dictionary,b: Dictionary) -> bool:
		if _stash_sort40==1:
			var rarity := {"common":0,"magic":1,"rare":2,"unique":3}
			var left: int=rarity.get(a.item.quality,0);var right: int=rarity.get(b.item.quality,0)
			if left!=right:return left>right
		elif _stash_sort40==2:
			var left: String=a.item.name;var right: String=b.item.name
			if left!=right:return left.naturalnocasecmp_to(right)<0
		return int(a.storage_id)>int(b.storage_id))
	return result

func _build_stash() -> void:
	if is_instance_valid(_stash_scroll40) and not _stash_reset_scroll40:_stash_offset40=_stash_scroll40.scroll_vertical
	_stash_reset_scroll40=false
	var box := _clear_modal40();overlay.visible=true
	box.add_child(_label("다음 도전의 장비",30,Color("e8d5a6")))
	box.add_child(_label("보유 장비 %d개 · 슬롯마다 하나씩 장착합니다"%profile_state.get("items",[]).size(),17,Color("c4bcaa")))
	var filters := HBoxContainer.new();filters.add_theme_constant_override("separation",10);box.add_child(filters)
	var slots: Array=["","weapon","body","charm","ring"]
	var qualities: Array=["","common","magic","rare","unique"]
	var slot_filter := _filter40(slots,["모든 슬롯","무기","갑옷","부적","반지"],slots.find(_stash_slot40),func(value):_stash_slot40=value;_reset_stash_filter40())
	slot_filter.tooltip_text="장비 슬롯 필터";filters.add_child(slot_filter)
	var rarity_filter := _filter40(qualities,["모든 등급","일반","마법","희귀","고유"],qualities.find(_stash_quality40),func(value):_stash_quality40=value;_reset_stash_filter40())
	rarity_filter.tooltip_text="장비 등급 필터";filters.add_child(rarity_filter)
	var order := _filter40([0,1,2],["최근 획득 순","등급 높은 순","이름 순"],_stash_sort40,func(value):_stash_sort40=int(value);_reset_stash_filter40())
	order.tooltip_text="보관함 정렬";filters.add_child(order)
	var records: Array[Dictionary]=_stash_records40()
	var count_label := _label("표시 %d개"%records.size(),15,Color("c4bcaa"));count_label.autowrap_mode=TextServer.AUTOWRAP_OFF
	count_label.vertical_alignment=VERTICAL_ALIGNMENT_CENTER;filters.add_child(count_label)
	var row := HBoxContainer.new();row.size_flags_vertical=Control.SIZE_EXPAND_FILL;row.add_theme_constant_override("separation",20);box.add_child(row)
	_stash_scroll40=ScrollContainer.new();_stash_scroll40.custom_minimum_size.x=390
	_stash_scroll40.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;row.add_child(_stash_scroll40)
	var list := VBoxContainer.new();list.size_flags_horizontal=Control.SIZE_EXPAND_FILL;list.add_theme_constant_override("separation",7);_stash_scroll40.add_child(list)
	var selected: Dictionary={}
	for record in records:
		if int(record.storage_id)==_storage_selection:selected=record
	if selected.is_empty() and not records.is_empty():selected=records[0];_storage_selection=int(selected.storage_id)
	for record in records:
		var id_: int=record.storage_id;var item: Dictionary=record.item
		var active: bool=profile_state.get("equipped",{}).get(item.slot,-1)==id_
		var button := _button(("[장착] " if active else "")+String(item.name),func():_storage_selection=id_;invalidate())
		button.alignment=HORIZONTAL_ALIGNMENT_LEFT;button.add_theme_font_size_override("font_size",17)
		button.add_theme_color_override("font_color",QUALITY_COLORS.get(item.quality,Color.WHITE))
		button.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS
		button.tooltip_text=String(SLOT_NAMES[item.slot])+" · "+String(QUALITY_NAMES[item.quality])+"\n"+String(item.name)
		if id_==_storage_selection:button.add_theme_stylebox_override("normal",_style(Color("303a3d"),BRASS38))
		list.add_child(button)
	if records.is_empty():list.add_child(_label("조건에 맞는 장비가 없습니다.\n슬롯이나 등급 필터를 바꿔 보세요." if not profile_state.get("items",[]).is_empty() else "전투에서 얻은 장비는 도전이 끝나면 여기에 보관됩니다.",17))
	var detail_frame := PanelContainer.new();detail_frame.size_flags_horizontal=Control.SIZE_EXPAND_FILL
	detail_frame.add_theme_stylebox_override("panel",_style(Color("171e21"),BRASS38));row.add_child(detail_frame)
	var detail_scroll := ScrollContainer.new();detail_scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;detail_frame.add_child(detail_scroll)
	var details := VBoxContainer.new();details.size_flags_horizontal=Control.SIZE_EXPAND_FILL;details.add_theme_constant_override("separation",14);detail_scroll.add_child(details)
	if not selected.is_empty():_stash_detail40(details,selected)
	else:details.add_child(_label("장비를 선택하면 효과와 장착 상태를 확인할 수 있습니다.",18))
	box.add_child(_label("재 %d · 완료한 도전 %d\n%s"%[profile_state.get("essence",0),profile_state.get("completed_runs",0),profile_note if not profile_note.is_empty() else "저장 상태 확인 중"],15,Color("c4bcaa")))
	box.add_child(_button("돌아가기 [Esc]",func():stash_open=false;invalidate()))
	_restore_stash40.call_deferred(_stash_scroll40,_stash_offset40)

func _stash_detail40(details: VBoxContainer,record: Dictionary) -> void:
	var item: Dictionary=record.item;var id_: int=record.storage_id
	var active: bool=profile_state.get("equipped",{}).get(item.slot,-1)==id_
	var rarity: Color=QUALITY_COLORS.get(item.quality,BRASS38)
	var heading := HBoxContainer.new();heading.add_theme_constant_override("separation",16);details.add_child(heading)
	heading.add_child(_sigil(item));var title := VBoxContainer.new();title.size_flags_horizontal=Control.SIZE_EXPAND_FILL;heading.add_child(title)
	title.add_child(_label(String(SLOT_NAMES[item.slot])+" · "+String(QUALITY_NAMES[item.quality]),16,rarity))
	title.add_child(_label(item.name,25,Color("e8d5a6")))
	details.add_child(_label("다음 도전에 장착 중" if active else "보관 중 · 다음 도전에 장착할 수 있습니다",17,Color("a8baaa") if active else Color("c4bcaa")))
	details.add_child(HSeparator.new());details.add_child(_label(_stats(item.get("stats",{})),18))
	if not String(item.get("description","")).is_empty():details.add_child(_label(item.description,17,Color("c4bcaa")))
	var equip_button := _button("장착 중" if active else "다음 도전에 장착",func():stash_equip.emit(id_));equip_button.disabled=active;details.add_child(equip_button)
	details.add_child(_button("이 장비 해체",func():_storage_selection=-1;stash_salvage.emit(id_)))
	details.add_child(_label("해체하면 장비가 사라지고 재로 전환됩니다.",14,Color("bca58f")))

func _restore_stash40(scroll: ScrollContainer,position_: int) -> void:
	for i in 2:await root.get_tree().process_frame
	if is_instance_valid(scroll) and scroll==_stash_scroll40:scroll.scroll_vertical=position_

func _reset_stash_filter40() -> void:
	_stash_offset40=0;_stash_reset_scroll40=true;invalidate()

func _build_result40(run: RefCounted) -> void:
	var box := _clear_modal40()
	var victorious: bool=run.mode=="victory"
	box.add_child(_label("회랑의 서약을 완수했습니다" if victorious else "이번 도전이 끝났습니다",32,Color("e8d5a6")))
	var growth: Dictionary=run.growth.snapshot()
	box.add_child(_label("%02d:%02d  ·  %d 처치  ·  레벨 %d"%[run.tick/3600,(run.tick/60)%60,run.kills,growth.level],19,Color("c4bcaa")))
	var columns := HBoxContainer.new();columns.size_flags_vertical=Control.SIZE_EXPAND_FILL;columns.add_theme_constant_override("separation",22);box.add_child(columns)
	var summary := VBoxContainer.new();summary.custom_minimum_size.x=350;summary.add_theme_constant_override("separation",12);columns.add_child(summary)
	summary.add_child(_label("이번 도전 장비",20,BRASS38))
	summary.add_child(_label("보유 %d개 · 보관 대기 %d개"%[run.inventory.size(),run.pending_rewards.size()],18))
	summary.add_child(_label("시작할 때 가져온 장비를 포함합니다.",14,Color("a4a597")))
	for slot in ["weapon","body","charm","ring"]:
		var equipped_name := "장착 없음"
		for item in run.inventory:
			if int(item.uid)==int(run.equipped.get(slot,-1)):equipped_name=String(item.name);break
		summary.add_child(_label(String(SLOT_NAMES[slot])+"  "+equipped_name,16))
	var rewards := VBoxContainer.new();rewards.size_flags_horizontal=Control.SIZE_EXPAND_FILL;rewards.add_theme_constant_override("separation",12);columns.add_child(rewards)
	rewards.add_child(_label("보상과 보관",20,BRASS38))
	var elite_item: Dictionary={}
	for item in run.inventory:
		if int(item.uid)==int(run._elite_reward_uid):elite_item=item;break
	if not elite_item.is_empty():
		var reward_frame := PanelContainer.new();reward_frame.add_theme_stylebox_override("panel",_style(Color("202628"),Color("b98140")));rewards.add_child(reward_frame)
		var reward_row := HBoxContainer.new();reward_row.add_theme_constant_override("separation",12);reward_frame.add_child(reward_row)
		reward_row.add_child(_sigil(elite_item));var names := VBoxContainer.new();names.size_flags_horizontal=Control.SIZE_EXPAND_FILL;reward_row.add_child(names)
		names.add_child(_label("파수왕의 유산",15,Color("efac59")));names.add_child(_label(elite_item.name,23,Color("e8d5a6")))
	else:rewards.add_child(_label("보유 장비는 보관함에서 확인하고 다음 도전에 장착할 수 있습니다.",18))
	rewards.add_child(_label("저장 상태",17,Color("a8baaa")))
	rewards.add_child(_label(profile_note if not profile_note.is_empty() else "저장 상태 확인 중",17))
	rewards.add_child(_button("보상 저장 다시 확인",func():save_retry.emit()))
	var actions := HBoxContainer.new();actions.add_theme_constant_override("separation",14);box.add_child(actions)
	var stash_button := _button("보관함에서 다음 장비 선택",func():stash_show.emit());stash_button.size_flags_horizontal=Control.SIZE_EXPAND_FILL;actions.add_child(stash_button)
	if victorious:
		var inspect_button := _button("이번 도전 장비 확인",func():equipment.emit());inspect_button.size_flags_horizontal=Control.SIZE_EXPAND_FILL;actions.add_child(inspect_button)
	var retry_button := _button("다시 도전",func():retry.emit());retry_button.size_flags_horizontal=Control.SIZE_EXPAND_FILL;actions.add_child(retry_button)
