extends RefCounted
## Current definitions drive HUD; original observation text stays separate.
static func quantity(value: float) -> String:
	var result: String = "%.3f" % value
	while result.ends_with("0"): result = result.left(-1)
	return result.trim_suffix(".")

static func sync(view: Node, sim: RefCounted, camera: Camera3D, registry: RefCounted, aim: Vector2) -> void:
	var maximum_life: float = sim.evidence_profile.player.life
	var maximum_mana: float = float(sim.mana_max_raw)/256.0
	var display: Dictionary = {}
	if sim.has_method("skill_display"):
		display = sim.skill_display()
		maximum_life = float(sim.life_max_raw)/256.0
	view.life_label.text = "생명 %s / %s" % [quantity(sim.life),quantity(maximum_life)]
	view.life_bar.max_value = maximum_life
	view.life_bar.value = sim.life
	view.mana_label.text = "마나 %s / %s" % [quantity(float(sim.mana_raw)/256.0),quantity(maximum_mana)]
	view.mana_bar.max_value = maximum_mana
	view.mana_bar.value = float(sim.mana_raw)/256.0
	if display.is_empty():
		view.cast_status.text = "화염탄   피해 %s–%s   ·   마나 %s" % [quantity(float(sim.damage_min_raw)/256.0),quantity(float(sim.damage_max_raw)/256.0),quantity(float(sim.mana_cost_raw)/256.0)]
		view.stats_text.text = "적 체력 %s · 이동/공격/피해는 실험값\n재시전 %s초 · 비행속도 %s 세계단위/초\n마나 재생 끔 · 피해 난수는 검증판 규칙\n3D 모델은 KayKit 대역, 탄은 클래식 자산" % [quantity(float(sim.params.enemy_hp)),quantity(float(sim.cycle_ticks)/sim.HZ),quantity(sim.bolt_speed)]
	else:
		var skill_name: String = String(display.display_name)+" Lv.%d" % int(display.get("effective_level",1))
		view.cast_status.text = "%s   피해 %s–%s   ·   마나 %s   ·   재시전 %s초" % [skill_name,quantity(float(display.damage_min_raw)/256.0),quantity(float(display.damage_max_raw)/256.0),quantity(float(display.cost_raw)/256.0),quantity(float(display.cycle_ticks)/sim.HZ)]
		view.stats_text.text = "적 체력 %s · 이동/공격/피해는 실험값\n선택: %s · 재시전 %s초\n사거리/반경 %s · 최대 대상 %d (독립 규칙)\n기본 화염탄 비행속도 %s · 마나 재생 끔\n3D 모델은 KayKit 대역 · 화염탄은 연구 자산" % [quantity(float(sim.params.enemy_hp)),display.display_name,quantity(float(display.cycle_ticks)/sim.HZ),quantity(float(display.range_world)),int(display.max_targets),quantity(sim.bolt_speed)]
		var ids: Array = sim.available_skill_ids()
		for index in range(view.skill_buttons.size()):
			var definition: Dictionary = sim.skill_definition(ids[index])
			view.skill_buttons[index].text = "%s[%d] %s" % ["◆ " if ids[index] == sim.selected_skill_id else "",index+1,definition.get("display_name",ids[index])]
			view.skill_buttons[index].disabled = sim.paused
		if view.auto_button:
			view.auto_button.text = "자동 시전 %s [F]" % ["켜짐" if view.input_controller.auto_cast else "꺼짐"]
			view.auto_button.disabled = sim.paused
		if view.skill_mode_label:
			var policy := "자동 시전 · 사거리 안 가까운 적" if view.input_controller.auto_cast else "수동 시전 · 포인터 조준"
			var casting: String = sim.casting_skill_id()
			var detail := "공격자 스탯 적용 · 대상 저항 적용 전"
			if not casting.is_empty():
				var committed: Dictionary = sim.pending_context_snapshot() if sim.has_method("pending_context_snapshot") else {}
				detail = "시전 중: "+str(sim.skill_definition(casting).get("display_name",casting))+" Lv.%d" % (int(committed.get("bonus_level",0))+1)
			view.skill_mode_label.text = policy+"\n"+detail
	var selected: Dictionary = sim.nearest_enemy(aim)
	var actor: Node3D = registry.actor_for(selected)
	view.enemy_label.visible = actor != null
	view.enemy_bar.visible = actor != null
	if actor:
		var screen: Vector2 = camera.unproject_position(actor.position+Vector3(0,2.2,0))
		view.enemy_label.position = screen+Vector2(-66,-30)
		view.enemy_bar.position = screen+Vector2(-68,-5)
		view.enemy_bar.value = float(selected.life_raw)/float(selected.max_raw)
	view.crowd_label.text = "생존 %d / 논리 개체 %d / 배우 %d   ·   처치 %d" % [sim.alive_count(),sim.enemies.size(),registry.actors.size(),sim.kills]
	var progression: Dictionary = sim.progression_snapshot()
	var next_xp: int = int(progression.get("next_level_xp",0))
	view.crowd_label.text += "   ·   Lv.%d  XP %d%s  ·  바닥 %d / 32" % [int(progression.get("level",1)),int(progression.get("xp",0))," / %d" % next_xp if next_xp > 0 else " (최고)",sim.ground_loot_snapshot().size()]
