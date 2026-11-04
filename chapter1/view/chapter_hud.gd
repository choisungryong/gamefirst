extends "res://chapter1/view/cloister_hud.gd"
var boss_bar: ProgressBar
signal stash_show
signal stash_equip(storage_id: int)
signal stash_salvage(storage_id: int)
signal save_retry
var profile_state: Dictionary={}
var profile_note := ""
var stash_open := false
var _storage_selection := -1
func _init() -> void:
	menu_title="잿빛 회랑 · 제1장"
	menu_description="세 봉인을 돌파하고 재의 성소에 도달하세요. 장비와 기술을 성장시켜 회랑의 파수왕을 처치하세요."
	menu_scope="WASD / 좌클릭 이동 · Q 회복약 · E 의식 · 선택 의식은 위험과 추가 보상"
	victory_title="제1장 · 회랑의 파수왕을 처치했습니다"
func setup(view: Node3D) -> void:
	super.setup(view)
	boss_bar=_bar(Color("943929"),9);boss_bar.set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	boss_bar.offset_left=-210;boss_bar.offset_right=210;boss_bar.offset_top=93;boss_bar.offset_bottom=102;boss_bar.visible=false;root.add_child(boss_bar)
func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	if run.hero.is_empty():return
	var goal: Dictionary=run.objective()
	objective.text="%s · %02d:%02d\n%s"%[goal.title,run.tick/3600,(run.tick/60)%60,goal.text]
	dash.text=("Space 회피 준비" if run.tick>=run.get_next_dash_tick() else "회피 %.1f초"%(float(run.get_next_dash_tick()-run.tick)/60))+"  ·  Q 회복약 %d / 5"%run.potions
	for def in run.RITUALS:
		if def.zone==run.zone and run.rituals[def.id].state=="ready" and run.hero.position.distance_squared_to(def.position)<=3*3:
			objective.text+="\n[E] "+def.name+" · 선택 보상"
	boss_bar.visible=run._champion_id>0 and run.enemies.has(run._champion_id)
	if boss_bar.visible:
		var e: Dictionary=run.enemies[run._champion_id];boss_bar.max_value=e.max_hp_raw;boss_bar.value=e.hp_raw
	if not run.pending_rewards.is_empty():objective.text+=" · 보관 대기 %d"%run.pending_rewards.size()
func _stats(stats: Dictionary) -> String:
	var lines: Array[String]=[]
	for pair in [["damage_bps","피해"],["cooldown_bps","시전 속도"],["slow_bps","냉기 감속"],["fire_damage_bps","화염 피해"],["arc_damage_bps","번개 피해"]]:
		if stats.has(pair[0]):lines.append("%s %+.1f%%"%[pair[1],float(stats[pair[0]])/100])
	if stats.has("max_hp_raw"):lines.append("최대 생명력 %+d"%(stats.max_hp_raw/256))
	if stats.has("damage_reduction_bps"):lines.append("받는 피해 -%.1f%%"%(float(stats.damage_reduction_bps)/100))
	if stats.has("pickup_radius_cm"):lines.append("회수 반경 +%.1fm"%(float(stats.pickup_radius_cm)/100))
	if stats.has("radius_cm"):lines.append("화염 폭발·번개 연결 거리 +%.1fm"%(float(stats.radius_cm)/100))
	for pair in [["projectiles","발사체 (번개는 대상)"],["chain_targets","연쇄 대상"],["shatter_count","파쇄 파편 (빙결 필요)"],["pierce","투사체 관통"],["fire_burst","화염 처치 폭발"],["frost_threshold","빙결 문턱 감소"],["arc_branches","번개 분기"]]:
		if stats.has(pair[0]):lines.append("%s %+d"%[pair[1],stats[pair[0]]])
	return "\n".join(lines) if not lines.is_empty() else "추가 효과 없음"

func _build_modal(run: RefCounted) -> void:
	if stash_open:
		_build_stash();return
	super._build_modal(run)
	if run.mode in ["menu","victory","defeat"]:
		var box: VBoxContainer=modal.get_child(0)
		box.add_child(_button("장비 보관함 · %d개"%profile_state.get("items",[]).size(),func():stash_show.emit()))
		if not profile_note.is_empty():box.add_child(_label(profile_note,14,Color("b4b49d")))
		if run.mode in ["victory","defeat"]:box.add_child(_button("보상 저장 다시 확인",func():save_retry.emit()))

func _build_stash() -> void:
	for child in modal.get_children():modal.remove_child(child);child.queue_free()
	overlay.visible=true
	var box := VBoxContainer.new();box.add_theme_constant_override("separation",12);modal.add_child(box)
	box.add_child(_label("장비 보관함 · %d / 256"%profile_state.get("items",[]).size(),29,Color("e3cd9d")))
	box.add_child(_label("다음 도전에 가져갈 장비를 슬롯별로 선택하세요. 해체는 해당 장비를 재로 바꿉니다.",16))
	var row := HBoxContainer.new();row.size_flags_vertical=Control.SIZE_EXPAND_FILL;row.add_theme_constant_override("separation",24);box.add_child(row)
	var scroll := ScrollContainer.new();scroll.custom_minimum_size.x=320;scroll.size_flags_vertical=Control.SIZE_EXPAND_FILL;row.add_child(scroll)
	var list := VBoxContainer.new();list.size_flags_horizontal=Control.SIZE_EXPAND_FILL;scroll.add_child(list)
	var selected: Dictionary={}
	for record in profile_state.get("items",[]):
		if _storage_selection<0:_storage_selection=record.storage_id
		var id_: int=record.storage_id;var item: Dictionary=record.item
		var active: bool=profile_state.get("equipped",{}).get(item.slot,-1)==id_
		list.add_child(_button(("◆ " if active else "")+item.name,func():_storage_selection=id_;invalidate()))
		if id_==_storage_selection:selected=record
	var details := VBoxContainer.new();details.size_flags_horizontal=Control.SIZE_EXPAND_FILL;details.custom_minimum_size.x=250;row.add_child(details)
	if selected.is_empty():details.add_child(_label("새로 획득한 장비는 전투가 끝나면 여기에 보관됩니다.",18))
	else:
		var item: Dictionary=selected.item;var id_: int=selected.storage_id
		details.add_child(_label(item.name,23,Color("dfc695")))
		details.add_child(_label(SLOT_NAMES[item.slot]+" · "+{"common":"일반","magic":"마법","rare":"희귀","unique":"고유"}[item.quality],16))
		details.add_child(_label(_stats(item.stats),16))
		if not item.description.is_empty():details.add_child(_label(item.description,16))
		details.add_child(_button("다음 도전에 장착",func():stash_equip.emit(id_)))
		details.add_child(_button("해체하여 재로 전환",func():_storage_selection=-1;stash_salvage.emit(id_)))
	box.add_child(_label("재 %d · 완료한 도전 %d · %s"%[profile_state.get("essence",0),profile_state.get("completed_runs",0),profile_note],14))
	box.add_child(_button("돌아가기",func():stash_open=false;invalidate()))
