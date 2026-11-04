extends RefCounted
## Independent 60Hz combat experiment; catalog assumptions are not D2R facts.
## Dictionary references preserve entity state: https://docs.godotengine.org/en/4.5/classes/class_dictionary.html
const Catalog = preload("res://data/game_catalog.gd")
const StatBlock = preload("res://combat/stat_block.gd")
const CombatResolver = preload("res://combat/combat_resolver.gd")
const EquipmentCatalog = preload("res://data/equipment_catalog.gd")
const EquipmentInventory = preload("res://data/equipment_inventory.gd")
const EquipmentStorage = preload("res://data/equipment_storage.gd")
const LootCatalog = preload("res://data/loot_catalog.gd")
const Progression = preload("res://data/progression.gd")
const ProgressStorage = preload("res://data/progress_storage.gd")
const HZ := 60
const STEP := 1.0 / HZ
const UNIT := 256
const MANA_MAX := 35 * UNIT
const MANA_COST := 640
const MIN_DAMAGE := 768
const MAX_DAMAGE := 1536
const STARTUP_TICKS := 18
const GRID_SIZE := 2.0
const MAX_ENTITIES := 2000
const HISTORY_CAPACITY := 4096
var mana_max_raw := MANA_MAX
var mana_cost_raw := MANA_COST
var damage_min_raw := MIN_DAMAGE
var damage_max_raw := MAX_DAMAGE
var startup_ticks := STARTUP_TICKS
var catalog: RefCounted
var tick := 0
var paused := false
var player := Vector2(0,3.5)
var move_target := Vector2(0,3.5)
var life := 40.0
var mana_raw := MANA_MAX
## Legacy first-entity alias points into enemies, never an independent copy.
var enemy: Dictionary = {}
var enemies: Dictionary = {}
var generations: Dictionary = {}
var free_ids: Array[int] = []
var next_id := 1
var initial_count := 1
var corpse_ticks := 300
var bolts: Array = []
var pending: Dictionary = {}
var events: Array = []
var _history: Array = []
var _history_head := 0
var history_dropped := 0
var history: Array:
	get: return history_snapshot()
var profiling_enabled := false
var profile_us: Dictionary = {"ai":0,"grid":0,"query":0,"narrowphase":0,"bolts":0}
var next_cast_tick := 0
var next_no_mana_notice_tick := 0
var shots := 0
var hits := 0
var kills := 0
var rng := RandomNumberGenerator.new()
var enemy_ai := true
var cycle_ticks := 33
var bolt_speed := 12.0
var last_direction := Vector2(0,-1)
var evidence_profile: Dictionary = {}
var params: Dictionary = {}
var valid_profile := false
var spatial_grid: Dictionary = {}
var query_cache: Dictionary = {}
var query_cache_enabled := true
var query_cache_hits := 0
var query_cache_misses := 0
var broadphase_candidates := 0
var narrowphase_checks := 0
var default_skill_id := ""
var selected_skill_id := ""
var life_max_raw := 40*UNIT
var player_stats: RefCounted
var stat_errors: Array[String] = []
var _stat_definitions: Array = []
var _skill_definitions: Dictionary = {}
var _health_stat_id := "stat.health"
var _mana_stat_id := "stat.mana"
var _enemy_base: Dictionary = {}
var _default_enemy_stats: RefCounted
var _enemy_stats: Dictionary = {}
var statuses: Dictionary = {}
var _pending_context: Dictionary = {}
var _paid_pending := false
var _shot_contexts: Dictionary = {}
var _issued_projectiles: Dictionary = {}
var _instant_releases: Array = []
var combat_trace: Array = []
var combat_errors: Array[String] = []
var equipment_catalog: RefCounted
var equipment_inventory: RefCounted
var equipment_valid := false
var equipment_errors: Array[String] = []
var _external_modifiers: Array = []
var _equipment_modifiers: Array = []
const COMBAT_TRACE_CAPACITY := 256
const MAX_COUNTER := 2147483647
const GROUND_CAPACITY := 32
const LOOT_TTL := 1800
const PICKUP_RADIUS := 1.75
var progression := Progression.new()
var loot_catalog: RefCounted
var loot_rng := RandomNumberGenerator.new()
var progress_errors: Array[String] = []
var progress_events: Array = []
var progress_history: Array = []
var _ground_loot: Dictionary = {}
var _reward_claims: Dictionary = {}
var _loot_epoch := 0
var _generation_floor := 0
var _generation_high_water := 0

func _init(catalog_override: RefCounted = null) -> void:
	catalog = catalog_override if catalog_override != null else Catalog.new()
	if catalog_override == null and not catalog.load_file():
		push_error("Invalid independent catalog: "+str(catalog.errors))
		return
	var definitions: Dictionary = catalog.snapshot()
	if definitions.is_empty(): return
	_stat_definitions = definitions.stats.duplicate(true)
	_health_stat_id = definitions.player.health_stat_id
	_mana_stat_id = definitions.player.mana_stat_id
	# Historical v1 health definitions omitted bounds. Their maximum-health
	# semantic now supplies the positive floor without changing default values.
	for definition in _stat_definitions:
		if definition.id == _health_stat_id and not definition.has("minimum_raw"):
			definition["minimum_raw"] = 1
			definition["default_raw"] = 1
	player_stats = StatBlock.new(_stat_definitions,{_health_stat_id:int(definitions.player.max_health_raw),_mana_stat_id:int(definitions.player.max_mana_raw)})
	if not player_stats.valid:
		push_error("Invalid independent player stats: "+str(player_stats.errors))
		return
	default_skill_id = definitions.experiment.skill_id
	selected_skill_id = default_skill_id
	for definition in definitions.skills: _skill_definitions[definition.id] = definition.duplicate(true)
	var enemy_definition: Dictionary = catalog.definition("enemies",definitions.experiment.enemy_id)
	_enemy_base = enemy_definition.get("defenses",{}).duplicate(true)
	_enemy_base[enemy_definition.health_stat_id] = int(enemy_definition.max_health_raw)
	_default_enemy_stats = StatBlock.new(_stat_definitions,_enemy_base)
	if not _default_enemy_stats.valid:
		push_error("Invalid independent enemy stats: "+str(_default_enemy_stats.errors))
		return
	evidence_profile = catalog.legacy_profile()
	params = evidence_profile.provisional_parameters
	var skill: Dictionary = catalog.definition("skills",definitions.experiment.skill_id)
	mana_max_raw = int(definitions.player.max_mana_raw)
	life_max_raw = int(definitions.player.max_health_raw)
	mana_cost_raw = int(skill.cost.raw)
	damage_min_raw = int(skill.damage.min_raw)
	damage_max_raw = int(skill.damage.max_raw)
	startup_ticks = int(skill.startup_ticks)
	cycle_ticks = int(skill.cycle_ticks)
	bolt_speed = float(params.projectile_world_speed)
	valid_profile = true
	reset()
	_initialize_equipment()
	_initialize_progress()

func _initialize_equipment() -> void:
	equipment_catalog = EquipmentCatalog.new(_stat_definitions,JSON.stringify(catalog.snapshot(),"",true,true).sha256_text())
	if not equipment_catalog.load_file():
		# Historical v1 catalogs remain valid combat catalogs without the new
		# equipment semantic stat. Equipment is unavailable in that compatibility case.
		equipment_errors = equipment_catalog.errors.duplicate()
		return
	equipment_inventory = EquipmentInventory.new(equipment_catalog,_apply_equipment_modifiers)
	if not equipment_inventory.valid:
		equipment_errors = equipment_inventory.errors.duplicate()
		return
	equipment_catalog = equipment_inventory.catalog
	for id_ in ["item.ember_focus","item.ward_robe","item.well_charm"]:
		if equipment_inventory.create_item(id_).is_empty():
			equipment_errors = equipment_inventory.errors.duplicate()
			return
	equipment_valid = true

func equipment_context() -> Dictionary:
	return equipment_inventory.context_snapshot() if equipment_valid else {"actor_tag":"caster","level":1}

func replace_equipment_context(candidate: Variant) -> bool:
	if not equipment_valid: return false
	var accepted: bool = equipment_inventory.replace_context(candidate)
	equipment_errors = equipment_inventory.errors.duplicate()
	return accepted

func equipment_snapshot() -> Dictionary:
	return equipment_inventory.snapshot() if equipment_valid else {}

func equipment_items() -> Array:
	var result: Array = []
	if not equipment_valid: return result
	var equipped: Dictionary = equipment_inventory.equipped_snapshot()
	for item in equipment_inventory.items_snapshot():
		var definition: Dictionary = equipment_catalog.definition("items",item.base_id)
		var modifiers: Array = []
		for modifier in definition.base_modifiers:
			modifiers.append({"stat_id":modifier.stat_id,"operation":modifier.operation,"value":int(modifier.value)})
		var names: Array = []
		for affix in item.affixes:
			var affix_definition: Dictionary = equipment_catalog.definition("affixes",affix.id)
			var modifier: Dictionary = affix_definition.modifier
			modifiers.append({"stat_id":modifier.stat_id,"operation":modifier.operation,"value":int(affix.value)})
			names.append(affix_definition.display_name)
		result.append({"uid":int(item.uid),"display_name":definition.display_name,"slot":definition.slot,"minimum_level":int(definition.minimum_level),"eligible":equipment_inventory.eligible(definition),"equipped":int(equipped.get(definition.slot,0)) == int(item.uid),"modifiers":modifiers,"affix_names":names})
	return result

func equip_item(uid: int) -> bool:
	if not equipment_valid: return false
	var accepted: bool = equipment_inventory.equip(uid)
	equipment_errors = equipment_inventory.errors.duplicate()
	return accepted

func unequip_item(slot: String) -> bool:
	if not equipment_valid: return false
	var accepted: bool = equipment_inventory.unequip(slot)
	equipment_errors = equipment_inventory.errors.duplicate()
	return accepted

func replace_equipment_document(candidate: Variant) -> bool:
	if not equipment_valid: return false
	# Legacy equipment-only imports must not steal reserved ground identities.
	if not _ground_loot.is_empty():
		var issues: Array = equipment_inventory.validate(candidate)
		if not issues.is_empty():
			equipment_errors.assign(issues)
			return false
		for item in candidate.items:
			if _ground_loot.has(int(item.uid)):
				equipment_errors.assign(["Owned UID collides with reserved ground loot"])
				return false
		for uid in _ground_loot:
			if int(candidate.next_uid) <= int(uid):
				equipment_errors.assign(["UID counter would reuse a ground identity"])
				return false
	var accepted: bool = equipment_inventory.replace_document(candidate)
	equipment_errors = equipment_inventory.errors.duplicate()
	return accepted

func save_equipment(path: String = EquipmentStorage.PATH) -> bool:
	if not equipment_valid: return false
	var document: Dictionary = equipment_snapshot()
	var issues: Array = equipment_inventory.validate(document)
	if not issues.is_empty():
		equipment_errors.assign(issues)
		return false
	var storage = EquipmentStorage.new()
	var accepted: bool = storage.write_document(document,path)
	equipment_errors = storage.errors.duplicate()
	return accepted

func load_equipment(path: String = EquipmentStorage.PATH) -> bool:
	if not equipment_valid: return false
	var storage = EquipmentStorage.new()
	var candidate: Variant = storage.read_document(path)
	if candidate == null:
		equipment_errors = storage.errors.duplicate()
		return false
	return replace_equipment_document(candidate)

func reset(count: int = -1) -> void:
	if _loot_epoch >= MAX_COUNTER or _generation_high_water >= MAX_COUNTER:
		progress_errors.assign(["Progress counter exhausted; reset rejected"])
		return
	_loot_epoch += 1
	_ground_loot.clear()
	progress_events.clear()
	progress_history.clear()
	if count >= 0: initial_count = clampi(count,0,MAX_ENTITIES)
	tick = 0
	paused = false
	player = Vector2(params.spawn_player_world[0],params.spawn_player_world[1])
	move_target = player
	life = float(life_max_raw)/UNIT
	mana_raw = mana_max_raw
	# Never reset generation counters: pre-reset handles must remain invalid.
	for id_ in enemies:
		if not free_ids.has(int(id_)): free_ids.append(int(id_))
	free_ids.sort()
	enemies.clear()
	enemy = {}
	bolts.clear()
	pending.clear()
	_pending_context.clear()
	_paid_pending = false
	_shot_contexts.clear()
	_issued_projectiles.clear()
	_instant_releases.clear()
	_enemy_stats.clear()
	statuses.clear()
	combat_trace.clear()
	combat_errors.clear()
	selected_skill_id = default_skill_id
	events.clear()
	clear_history()
	spatial_grid.clear()
	query_cache.clear()
	query_cache_hits = 0
	query_cache_misses = 0
	next_cast_tick = 0
	next_no_mana_notice_tick = 0
	shots = 0
	hits = 0
	kills = 0
	broadphase_candidates = 0
	narrowphase_checks = 0
	last_direction = Vector2(0,-1)
	rng.seed = int(params.rng_seed)
	populate(initial_count)
	events.clear()
	clear_history()

func clear_history() -> void:
	_history.clear()
	_history_head = 0
	history_dropped = 0

func history_count() -> int:
	return _history.size()

func history_snapshot() -> Array:
	if _history_head == 0: return _history.duplicate()
	var ordered: Array = []
	ordered.append_array(_history.slice(_history_head))
	ordered.append_array(_history.slice(0,_history_head))
	return ordered

func populate(count: int) -> void:
	var wanted: int = clampi(count,0,MAX_ENTITIES)
	for i in range(wanted):
		var p := Vector2(params.spawn_enemy_world[0],params.spawn_enemy_world[1])
		if i > 0:
			# Deterministic arena distribution; this is an independent spawn policy.
			var angle: float = float(i)*2.39996322972865
			var radius: float = 2.2+sqrt(float(i))*0.48
			var bound := Vector2(params.world_bounds[0],params.world_bounds[1])
			p = (player+Vector2(cos(angle),sin(angle))*radius).clamp(-bound,bound)
		spawn_enemy(p)

func spawn_enemy(point: Vector2, radius: float = -1.0) -> Dictionary:
	if enemies.size() >= MAX_ENTITIES or not point.is_finite(): return {}
	if radius == -1.0: radius = float(params.collision_radius)
	if not is_finite(radius) or radius <= 0.0 or radius > 64.0: return {}
	var id_: int
	if free_ids.is_empty():
		id_ = next_id
		next_id += 1
	else:
		id_ = free_ids.pop_front()
	var previous_generation: int = maxi(int(generations.get(id_,0)),_generation_floor)
	if id_ > MAX_ENTITIES or previous_generation >= MAX_COUNTER:
		if id_ <= MAX_ENTITIES:
			free_ids.append(id_)
			free_ids.sort()
		progress_errors.assign(["Entity identity counter exhausted"])
		return {}
	var generation: int = previous_generation+1
	_generation_high_water = maxi(_generation_high_water,generation)
	generations[id_] = generation
	var hp: int = roundi(float(params.enemy_hp)*UNIT)
	var state: Dictionary = {"id":id_,"generation":generation,"p":point,"life_raw":hp,"max_raw":hp,"state":"approach","timer":0,"facing":Vector2.DOWN,"radius":radius,"corpse_until":-1}
	enemies[id_] = state
	if enemy.is_empty(): enemy = state
	emit("enemy_spawn",{"entity":handle(state),"p":[point.x,point.y]})
	return handle(state)

func handle(state: Dictionary) -> Dictionary:
	return {"id":int(state.id),"generation":int(state.generation)}

func entity(identity: Dictionary) -> Dictionary:
	if not identity.get("id") is int or not identity.get("generation") is int: return {}
	var state: Dictionary = enemies.get(identity.id,{})
	if state.is_empty() or state.generation != identity.generation: return {}
	return state

func despawn_enemy(identity: Dictionary) -> bool:
	var state: Dictionary = entity(identity)
	if state.is_empty(): return false
	_enemy_stats.erase(int(state.id))
	statuses.erase(int(state.id))
	enemies.erase(state.id)
	if enemy.get("id",-1) == state.id:
		var live_ids: Array = enemies.keys()
		live_ids.sort()
		enemy = enemies[live_ids[0]] if not live_ids.is_empty() else {}
	free_ids.append(int(state.id))
	free_ids.sort()
	emit("enemy_despawn",{"entity":handle(state)})
	return true

func alive_count() -> int:
	var count := 0
	for state in enemies.values():
		if state.state != "dead": count += 1
	return count

func nearest_enemy(point: Vector2) -> Dictionary:
	var selected: Dictionary = {}
	var distance := INF
	for state in enemies.values():
		if state.state == "dead": continue
		var candidate: float = point.distance_squared_to(state.p)
		if candidate < distance or (is_equal_approx(candidate,distance) and not selected.is_empty() and int(state.id)<int(selected.id)):
			distance = candidate
			selected = state
	return selected

func emit(kind: String, details: Dictionary = {}) -> void:
	var entry: Dictionary = details.duplicate(true)
	entry["kind"] = kind
	entry["tick"] = tick
	entry["seconds"] = float(tick)/HZ
	events.append(entry)
	if _history.size() < HISTORY_CAPACITY:
		_history.append(entry)
	else:
		_history[_history_head] = entry
		_history_head = (_history_head+1)%HISTORY_CAPACITY
		history_dropped += 1

func set_destination(point: Vector2) -> void:
	if not point.is_finite(): return
	var bound := Vector2(params.world_bounds[0],params.world_bounds[1])
	move_target = point.clamp(-bound,bound)

func available_skill_ids() -> Array[String]:
	var ids: Array[String] = []
	for id_ in _skill_definitions: ids.append(String(id_))
	return ids

func select_skill(id_: String) -> bool:
	if not _skill_definitions.has(id_): return false
	selected_skill_id = id_
	return true

func skill_definition(id_: String = "") -> Dictionary:
	return _skill_definitions.get(selected_skill_id if id_.is_empty() else id_,{}).duplicate(true)

func pending_skill_id() -> String:
	return String(_pending_context.get("skill_id","")) if not pending.is_empty() else ""

func casting_skill_id() -> String:
	return pending_skill_id()

func pending_context_snapshot() -> Dictionary:
	return _pending_context.duplicate(true)

func skill_display(id_: String = "") -> Dictionary:
	var context: Dictionary = _make_context(selected_skill_id if id_.is_empty() else id_)
	if context.is_empty(): return {}
	return {"id":context.skill_id,"display_name":context.display_name,"kind":context.kind,"element":context.element,"effective_level":int(context.get("bonus_level",0))+1,"bonus_level":int(context.get("bonus_level",0)),"cost_raw":context.cost_raw,"damage_min_raw":CombatResolver.damage(context.base_min_raw,0,0,0,context.power_bps).after_power_raw,"damage_max_raw":CombatResolver.damage(context.base_max_raw,0,0,0,context.power_bps).after_power_raw,"startup_ticks":context.startup_ticks,"cycle_ticks":context.cycle_ticks,"range_world":context.range_world,"max_targets":context.effect.get("max_targets",1),"status":context.effect.get("status",{}).duplicate(true)}

func replace_player_modifiers(candidate: Variant) -> bool:
	if not candidate is Array or candidate.size() > StatBlock.MAX_MODIFIERS:
		stat_errors.assign(["External modifiers require a bounded array"])
		return false
	for modifier in candidate:
		if modifier is Dictionary and modifier.get("source_id") is String and modifier.source_id.begins_with(EquipmentInventory.SOURCE_PREFIX):
			stat_errors.assign(["Equipment modifier source is reserved"])
			return false
	if not _replace_combined_modifiers(candidate,_equipment_modifiers): return false
	_external_modifiers = candidate.duplicate(true)
	return true

func _apply_equipment_modifiers(candidate: Array) -> bool:
	if not _replace_combined_modifiers(_external_modifiers,candidate): return false
	_equipment_modifiers = candidate.duplicate(true)
	return true

func _replace_combined_modifiers(external: Array, gear: Array) -> bool:
	var combined: Array = external.duplicate(true)
	combined.append_array(gear.duplicate(true))
	if not player_stats.replace_modifiers(combined):
		stat_errors = player_stats.errors.duplicate()
		return false
	stat_errors.clear()
	life_max_raw = player_stats.value(_health_stat_id)
	mana_max_raw = player_stats.value(_mana_stat_id)
	life = minf(life,float(life_max_raw)/UNIT)
	mana_raw = mini(mana_raw,mana_max_raw)
	return true

func player_stats_snapshot() -> Dictionary:
	return player_stats.snapshot()

func replace_enemy_modifiers(identity: Dictionary, candidate: Variant) -> bool:
	var state: Dictionary = entity(identity)
	if state.is_empty() or state.state == "dead": return false
	# This phase exposes enemy defenses only; maximum-health changes need a
	# separate explicit current/max HP policy before they can be supported.
	if candidate is Array:
		for modifier in candidate:
			if modifier is Dictionary and not modifier.get("stat_id","") in ["stat.flat_reduction","stat.resist.fire","stat.resist.cold","stat.resist.lightning","stat.resist.physical"]:
				stat_errors.assign(["Enemy modifiers support defense stats only"])
				return false
	var block = StatBlock.new(_stat_definitions,_enemy_base)
	if not block.replace_modifiers(candidate):
		stat_errors = block.errors.duplicate()
		return false
	_enemy_stats[int(state.id)] = {"generation":int(state.generation),"block":block}
	stat_errors.clear()
	return true

func enemy_stats_snapshot(identity: Dictionary) -> Dictionary:
	var state: Dictionary = entity(identity)
	return {} if state.is_empty() else _defense_block(state).snapshot()

func status_snapshot(identity: Dictionary) -> Dictionary:
	var state: Dictionary = entity(identity)
	if state.is_empty() or not statuses.has(int(state.id)): return {}
	var status: Dictionary = statuses[int(state.id)]
	return status.duplicate(true) if int(status.generation) == int(state.generation) else {}

func _defense_block(state: Dictionary) -> RefCounted:
	var candidate: Dictionary = _enemy_stats.get(int(state.id),{})
	return candidate.block if not candidate.is_empty() and int(candidate.generation) == int(state.generation) else _default_enemy_stats

func _make_context(id_: String) -> Dictionary:
	if not _skill_definitions.has(id_): return {}
	var definition: Dictionary = _skill_definitions[id_]
	var kind: String = definition.get("kind","projectile")
	var legacy: bool = id_ == default_skill_id and kind == "projectile"
	var timing: Dictionary = CombatResolver.timing(startup_ticks if legacy else int(definition.startup_ticks),cycle_ticks if legacy else int(definition.cycle_ticks),player_stats.value("stat.cast_speed"))
	var effect: Dictionary = definition.get("effect",{}).duplicate(true)
	var context: Dictionary = {"skill_id":id_,"display_name":definition.get("display_name","화염탄"),"kind":kind,"element":definition.damage.element,"legacy":legacy,"cost_raw":CombatResolver.cost(mana_cost_raw if legacy else int(definition.cost.raw),player_stats.value("stat.mana_cost")),"base_min_raw":damage_min_raw if legacy else int(definition.damage.min_raw),"base_max_raw":damage_max_raw if legacy else int(definition.damage.max_raw),"power_bps":player_stats.value("stat.spell_power"),"startup_ticks":timing.startup_ticks,"cycle_ticks":timing.cycle_ticks,"effect":effect}
	if definition.has("bonus_curve"):
		var curve: Dictionary = definition.bonus_curve
		var bonus: int = clampi(player_stats.value(curve.stat_id),0,20)
		context["bonus_level"] = bonus
		context.base_min_raw = mini(CombatResolver.MAX_RAW,int(context.base_min_raw)+bonus*int(curve.min_per_bonus_raw))
		context.base_max_raw = mini(CombatResolver.MAX_RAW,int(context.base_max_raw)+bonus*int(curve.max_per_bonus_raw))
	if kind == "projectile":
		var projectile: Dictionary = catalog.definition("projectiles",definition.projectile_id)
		context["spawn_offset"] = float(params.projectile_spawn_offset) if legacy else float(projectile.spawn_offset_world)
		context["projectile_life_ticks"] = roundi(float(params.projectile_life_seconds)*HZ) if legacy else roundi(float(projectile.lifetime_seconds)*HZ)
		context["projectile_speed"] = bolt_speed if legacy else float(projectile.speed_world_per_second)
		context["range_world"] = float(context.projectile_speed)*float(context.projectile_life_ticks)/HZ+float(context.spawn_offset)
	else: context["range_world"] = float(effect.radius_world) if kind == "area" else float(effect.range_world)
	return context

func _add_skill_fields(details: Dictionary, context: Dictionary) -> void:
	if context.legacy: return
	details["skill_id"] = context.skill_id
	details["element"] = context.element
	details["effect_kind"] = context.kind

func _record_resolution(result: Dictionary, state: Dictionary, context: Dictionary) -> void:
	var trace: Dictionary = result.duplicate(true)
	trace["tick"] = tick
	trace["entity"] = handle(state)
	trace["skill_id"] = context.skill_id
	trace["source"] = context.get("source","committed_cast")
	if combat_trace.size() >= COMBAT_TRACE_CAPACITY: combat_trace.pop_front()
	combat_trace.append(trace)

func _apply_damage(state: Dictionary, context: Dictionary, impact: Vector2) -> bool:
	if state.is_empty() or state.state == "dead": return false
	var defense: RefCounted = _defense_block(state)
	var base: int = rng.randi_range(int(context.base_min_raw),int(context.base_max_raw))
	var result: Dictionary = CombatResolver.damage(base,int(state.life_raw),defense.value("stat.flat_reduction"),defense.value("stat.resist."+String(context.element)),int(context.power_bps),int(params.death_threshold_raw))
	state.life_raw = int(result.hp_after_raw)
	hits += 1
	var details := {"shot":int(context.shot),"entity":handle(state),"damage_raw":int(result.total_raw),"enemy_life_raw":int(state.life_raw),"p":[impact.x,impact.y]}
	_add_skill_fields(details,context)
	emit("hit",details)
	_record_resolution(result,state,context)
	if result.dead:
		state.state = "dead"
		state.timer = 0
		state.corpse_until = tick+corpse_ticks
		kills += 1
		_remove_status(state,"death")
		_enemy_stats.erase(int(state.id))
		emit("enemy_dead",{"entity":handle(state)})
		claim_death_reward(handle(state))
	elif int(result.total_raw) > 0:
		state.state = "hurt"
		state.timer = roundi(float(params.enemy_hurt_seconds)*HZ)
		if context.effect.has("status"): _apply_status(state,context.effect.status,String(context.skill_id))
	return true

func _apply_status(state: Dictionary, definition: Dictionary, skill_id: String) -> void:
	var previous: Dictionary = status_snapshot(handle(state))
	var until: int = maxi(int(previous.get("until_tick",0)),tick+int(definition.duration_ticks))
	var strength: int = maxi(int(previous.get("slow_bps",0)),int(definition.slow_bps))
	statuses[int(state.id)] = {"generation":int(state.generation),"kind":"chill","until_tick":until,"slow_bps":strength}
	emit("status_applied",{"entity":handle(state),"skill_id":skill_id,"status":"chill","until_tick":until,"slow_bps":strength,"p":[state.p.x,state.p.y]})

func _remove_status(state: Dictionary, reason: String) -> void:
	if not statuses.has(int(state.id)): return
	statuses.erase(int(state.id))
	emit("status_expired",{"entity":handle(state),"status":"chill","reason":reason})

func _expire_statuses() -> void:
	for id_ in statuses.keys():
		var state: Dictionary = enemies.get(id_,{})
		var status: Dictionary = statuses[id_]
		if state.is_empty() or int(state.generation) != int(status.generation): statuses.erase(id_)
		elif state.state == "dead": _remove_status(state,"death")
		elif tick >= int(status.until_tick): _remove_status(state,"expired")

func _targets_in_range(origin: Vector2, radius: float, excluded: Dictionary = {}) -> Array:
	var targets: Array = []
	for id_ in query_segment(origin-Vector2.ONE*radius,origin+Vector2.ONE*radius):
		var state: Dictionary = enemies.get(id_,{})
		if state.is_empty() or state.state == "dead" or excluded.has(int(id_)): continue
		if origin.distance_squared_to(state.p) <= radius*radius: targets.append(state)
	targets.sort_custom(func(a: Dictionary,b: Dictionary) -> bool:
		var da: float = origin.distance_squared_to(a.p)
		var db: float = origin.distance_squared_to(b.p)
		return int(a.id) < int(b.id) if da == db else da < db)
	return targets

func _resolve_instant_releases() -> void:
	if _instant_releases.is_empty(): return
	rebuild_grid()
	for context in _instant_releases:
		var origin: Vector2 = context.origin
		var selected: Array = []
		var points: Array = []
		if context.kind == "area":
			var targets: Array = _targets_in_range(origin,float(context.effect.radius_world))
			for index in range(mini(targets.size(),int(context.effect.max_targets))): selected.append(targets[index])
		else:
			points.append([origin.x,origin.y])
			var visited: Dictionary = {}
			var from: Vector2 = origin
			for hop in range(int(context.effect.max_targets)):
				var radius: float = float(context.effect.range_world) if hop == 0 else float(context.effect.jump_range_world)
				# First chain target follows committed aim; subsequent jumps start at
				# the last target. Eligibility always stays inside the caster range.
				var candidates: Array = _targets_in_range(from,radius,visited)
				candidates = candidates.filter(func(candidate: Dictionary) -> bool: return origin.distance_squared_to(candidate.p) <= float(context.effect.range_world)*float(context.effect.range_world))
				if candidates.is_empty(): break
				if hop == 0:
					var aimed: Vector2 = origin+Vector2(context.direction)*float(context.effect.range_world)
					candidates.sort_custom(func(a: Dictionary,b: Dictionary) -> bool:
						var da: float = aimed.distance_squared_to(a.p)
						var db: float = aimed.distance_squared_to(b.p)
						return int(a.id) < int(b.id) if da == db else da < db)
				var target: Dictionary = candidates[0]
				selected.append(target)
				visited[int(target.id)] = true
				from = target.p
		var handles: Array = []
		for target in selected:
			var point: Vector2 = target.p
			if _apply_damage(target,context,point):
				handles.append(handle(target))
				points.append([point.x,point.y])
		emit("skill_effect",{"skill_id":context.skill_id,"effect_kind":context.kind,"element":context.element,"origin":[origin.x,origin.y],"radius_world":context.effect.get("radius_world",0.0),"points":points,"targets":handles})
	_instant_releases.clear()

func cast_request(aim: Vector2, skill_id: String = "") -> bool:
	if paused or life <= 0 or not aim.is_finite() or tick < next_cast_tick or not pending.is_empty(): return false
	var context: Dictionary = _make_context(selected_skill_id if skill_id.is_empty() else skill_id)
	if context.is_empty(): return false
	var payment: Dictionary = CombatResolver.pay_cost(mana_raw,int(context.cost_raw))
	if not payment.accepted:
		if tick >= next_no_mana_notice_tick:
			emit("no_mana")
			next_no_mana_notice_tick = tick+18
		return false
	var direction: Vector2 = (aim-player).normalized()
	if direction.length_squared() < .001: direction = last_direction
	last_direction = direction
	move_target = player
	mana_raw = int(payment.mana_after_raw)
	_pending_context = context
	_paid_pending = true
	pending = {"release":tick+int(context.startup_ticks),"direction":direction,"start":tick}
	next_cast_tick = tick+int(context.cycle_ticks)
	var details := {"mana_raw":mana_raw,"release_tick":int(pending.release)}
	_add_skill_fields(details,context)
	emit("cast_start",details)
	return true

func step(cast_held: bool = false, aim: Vector2 = Vector2.ZERO, skill_id: String = "") -> void:
	events.clear()
	progress_events.clear()
	if paused or life <= 0: return
	tick += 1
	_expire_statuses()
	if pending.is_empty() and tick >= next_cast_tick:
		var delta: Vector2 = move_target-player
		if delta.length() > .035:
			var travel: Vector2 = delta.limit_length(float(params.player_world_speed)*STEP)
			player += travel
			last_direction = travel.normalized()
	if cast_held: cast_request(aim,skill_id)
	if not pending.is_empty() and tick >= int(pending.release):
		if _paid_pending and _pending_context.is_empty():
			combat_errors.append("Paid pending cast context missing")
			pending.clear()
			_paid_pending = false
			return
		var direction: Vector2 = pending.direction
		var context: Dictionary = _pending_context.duplicate(true) if not _pending_context.is_empty() else _make_context(default_skill_id)
		shots += 1
		context["shot"] = shots
		context["origin"] = player
		context["direction"] = direction
		if context.kind == "projectile":
			bolts.append({"p":player+direction*float(context.spawn_offset),"direction":direction,"age":0,"life":int(context.projectile_life_ticks),"id":shots})
			_shot_contexts[shots] = context
			_issued_projectiles[shots] = true
		else: _instant_releases.append(context)
		var details := {"shot":shots,"direction":[direction.x,direction.y]}
		_add_skill_fields(details,context)
		emit("release",details)
		pending.clear()
		_pending_context.clear()
		_paid_pending = false
	var began: int = Time.get_ticks_usec() if profiling_enabled else 0
	step_enemy()
	if profiling_enabled: profile_us.ai = Time.get_ticks_usec()-began
	_resolve_instant_releases()
	began = Time.get_ticks_usec() if profiling_enabled else 0
	step_bolts()
	if profiling_enabled: profile_us.bolts = Time.get_ticks_usec()-began
	_step_ground_loot()

func step_enemy() -> void:
	for id_ in enemies.keys():
		var state: Dictionary = enemies[id_]
		if state.state == "dead":
			if int(state.corpse_until) >= 0 and tick >= int(state.corpse_until): despawn_enemy(handle(state))
			continue
		step_one_enemy(state)

func step_one_enemy(state: Dictionary) -> void:
	if state.timer > 0: state.timer -= 1
	if state.state == "hurt":
		if state.timer <= 0: state.state = "approach"
		return
	if not enemy_ai or life <= 0: return
	var ep: Vector2 = state.p
	var toward: Vector2 = player-ep
	if state.state == "windup":
		if state.timer <= 0:
			if toward.length() < float(params.enemy_attack_hit_range):
				var result: Dictionary = CombatResolver.damage(roundi(float(params.enemy_damage)*UNIT),roundi(life*UNIT),player_stats.value("stat.flat_reduction"),player_stats.value("stat.resist.physical"))
				life = float(result.hp_after_raw)/UNIT
				emit("player_hurt",{"life":life,"entity":handle(state)})
				if life <= 0:
					pending.clear()
					_pending_context.clear()
					_paid_pending = false
					emit("player_dead")
			state.state = "recover"
			state.timer = roundi(float(params.enemy_attack_recovery_seconds)*HZ)
		return
	if state.state == "recover":
		if state.timer <= 0: state.state = "approach"
		return
	if toward.length() < float(params.enemy_attack_start_range):
		state.state = "windup"
		state.timer = roundi(float(params.enemy_attack_windup_seconds)*HZ)
		emit("enemy_windup",{"entity":handle(state)})
	else:
		var speed: float = float(params.enemy_speed)
		if statuses.has(int(state.id)):
			var status: Dictionary = statuses[int(state.id)]
			if int(status.generation) == int(state.generation): speed *= float(10000-int(status.slow_bps))/10000.0
		state.p = ep+toward.normalized()*speed*STEP
		state.facing = toward.normalized()

## Exact first segment-circle entry, including overlap and zero-length.
## Geometry is independent gameplay math, not a recovered D2R function.
func swept_fraction(before: Vector2, after: Vector2, point: Vector2, radius: float) -> float:
	var segment: Vector2 = after-before
	return swept_with_segment(before,segment,segment.length_squared(),point,radius)

func swept_with_segment(before: Vector2, segment: Vector2, a: float, point: Vector2, radius: float) -> float:
	var offset: Vector2 = before-point
	if offset.length_squared() <= radius*radius: return 0.0
	if a < 0.000000000001: return -1.0
	var b: float = 2.0*offset.dot(segment)
	var c: float = offset.length_squared()-radius*radius
	var discriminant: float = b*b-4.0*a*c
	if discriminant < 0.0: return -1.0
	var first: float = (-b-sqrt(maxf(0.0,discriminant)))/(2.0*a)
	return clampf(first,0.0,1.0) if first >= -0.0000001 and first <= 1.0000001 else -1.0

func grid_cell(point: Vector2) -> Vector2i:
	return Vector2i(floori(point.x/GRID_SIZE),floori(point.y/GRID_SIZE))

func rebuild_grid() -> void:
	spatial_grid.clear()
	query_cache.clear()
	query_cache_hits = 0
	query_cache_misses = 0
	for state in enemies.values():
		if state.state == "dead": continue
		var r: float = state.radius
		var first: Vector2i = grid_cell(state.p-Vector2.ONE*r)
		var last: Vector2i = grid_cell(state.p+Vector2.ONE*r)
		for x in range(first.x,last.x+1):
			for y in range(first.y,last.y+1):
				var cell := Vector2i(x,y)
				if not spatial_grid.has(cell): spatial_grid[cell] = []
				spatial_grid[cell].append(int(state.id))

func query_segment(before: Vector2, after: Vector2) -> Array:
	# Preserve caller-owned results. The combat loop reads the cached internal
	# Array directly and never mutates it, avoiding a copy per projectile.
	return _query_segment_cached(before,after).duplicate()

func _query_segment_cached(before: Vector2, after: Vector2) -> Array:
	var first: Vector2i = grid_cell(before.min(after)-Vector2.ONE*0.000001)
	var last: Vector2i = grid_cell(before.max(after)+Vector2.ONE*0.000001)
	var cache_key := Vector4i(first.x,first.y,last.x,last.y)
	if query_cache_enabled and query_cache.has(cache_key):
		query_cache_hits += 1
		return query_cache[cache_key]
	query_cache_misses += 1
	var selected: Dictionary = {}
	for x in range(first.x,last.x+1):
		for y in range(first.y,last.y+1):
			for id_ in spatial_grid.get(Vector2i(x,y),[]): selected[id_] = true
	var ids: Array = selected.keys()
	ids.sort()
	if query_cache_enabled: query_cache[cache_key] = ids
	return ids

func step_bolts() -> void:
	broadphase_candidates = 0
	narrowphase_checks = 0
	profile_us.grid = 0
	profile_us.query = 0
	profile_us.narrowphase = 0
	if bolts.is_empty():
		spatial_grid.clear()
		query_cache.clear()
		query_cache_hits = 0
		query_cache_misses = 0
		return
	var began: int = Time.get_ticks_usec() if profiling_enabled else 0
	rebuild_grid()
	if profiling_enabled: profile_us.grid = Time.get_ticks_usec()-began
	var remaining: Array = []
	var manual_context: Dictionary = {}
	for bolt in bolts:
		var shot_id: int = int(bolt.id)
		var context: Dictionary = _shot_contexts.get(shot_id,{})
		if context.is_empty():
			if _issued_projectiles.has(shot_id):
				combat_errors.append("Committed projectile context missing: "+str(shot_id))
				_issued_projectiles.erase(shot_id)
				continue
			# Legacy tests/stress can inject uncommitted projectiles. Only these
			# use current default parameters; a paid cast must retain its snapshot.
			if manual_context.is_empty():
				manual_context = _make_context(default_skill_id)
				manual_context["source"] = "uncommitted_fixture"
			context = manual_context.duplicate()
			context["shot"] = shot_id
		var before: Vector2 = bolt.p
		var after: Vector2 = before+Vector2(bolt.direction)*float(context.projectile_speed)*STEP
		var segment: Vector2 = after-before
		var segment_length_squared: float = segment.length_squared()
		var padding: Vector2 = segment.abs()*.0000001+Vector2.ONE*.000001
		var segment_min: Vector2 = before.min(after)-padding
		var segment_max: Vector2 = before.max(after)+padding
		bolt.age += 1
		bolt.life -= 1
		var best := INF
		var selected: Dictionary = {}
		began = Time.get_ticks_usec() if profiling_enabled else 0
		var candidates: Array = _query_segment_cached(before,after)
		if profiling_enabled: profile_us.query += Time.get_ticks_usec()-began
		broadphase_candidates += candidates.size()
		began = Time.get_ticks_usec() if profiling_enabled else 0
		for id_ in candidates:
			var state: Dictionary = enemies.get(id_,{})
			if state.is_empty() or state.state == "dead": continue
			narrowphase_checks += 1
			var center: Vector2 = state.p
			var radius: float = state.radius
			if center.x+radius < segment_min.x or center.x-radius > segment_max.x or center.y+radius < segment_min.y or center.y-radius > segment_max.y: continue
			var fraction: float = swept_with_segment(before,segment,segment_length_squared,center,radius)
			if fraction >= 0.0 and fraction < best-0.0000001:
				best = fraction
				selected = state
		if profiling_enabled: profile_us.narrowphase += Time.get_ticks_usec()-began
		if not selected.is_empty():
			var impact: Vector2 = before.lerp(after,best)
			_apply_damage(selected,context,impact)
		elif bolt.life > 0:
			bolt.p = after
			remaining.append(bolt)
			continue
		_shot_contexts.erase(shot_id)
		_issued_projectiles.erase(shot_id)
	bolts = remaining

func _initialize_progress() -> void:
	loot_rng.seed = 61483
	if not equipment_valid: return
	loot_catalog = LootCatalog.new(equipment_catalog)
	if not loot_catalog.load_file():
		progress_errors = loot_catalog.errors.duplicate()
		loot_catalog = null
		return
	loot_catalog.freeze()

func progression_snapshot() -> Dictionary:
	return progression.snapshot()

func _progress_emit(kind: String, details: Dictionary = {}) -> void:
	var event: Dictionary = details.duplicate(true)
	event["kind"] = kind
	event["tick"] = tick
	progress_events.append(event)
	if progress_history.size() >= 256: progress_history.pop_front()
	progress_history.append(event.duplicate(true))

func ground_loot_snapshot() -> Array:
	var result: Array = []
	var ids: Array = _ground_loot.keys()
	ids.sort()
	for uid in ids:
		var entry: Dictionary = _ground_loot[uid]
		result.append({"uid":int(uid),"epoch":_loot_epoch,"item":entry.item.duplicate(true),"p":entry.p.duplicate(),"remaining_ticks":maxi(0,int(entry.expires)-tick)})
	return result

func loot_handle(uid: int) -> Dictionary:
	return {"uid":uid,"epoch":_loot_epoch} if _ground_loot.has(uid) else {}

func pickup_loot(identity: Dictionary) -> bool:
	progress_errors.clear()
	if identity.size() != 2 or not identity.has_all(["uid","epoch"]) or not Catalog.integer(identity.uid,1,EquipmentInventory.MAX_UID) or not Catalog.integer(identity.epoch,1,MAX_COUNTER) or int(identity.epoch) != _loot_epoch or not _ground_loot.has(int(identity.uid)):
		progress_errors.assign(["Stale or invalid loot handle"])
		return false
	var entry: Dictionary = _ground_loot[int(identity.uid)]
	if int(entry.expires) <= tick or player.distance_squared_to(Vector2(entry.p[0],entry.p[1])) > PICKUP_RADIUS*PICKUP_RADIUS:
		progress_errors.assign(["Loot expired or out of pickup range"])
		return false
	if not equipment_inventory.acquire_reserved(entry.item):
		progress_errors = equipment_inventory.errors.duplicate()
		return false
	_ground_loot.erase(int(identity.uid))
	_progress_emit("loot_pickup",{"uid":int(identity.uid),"epoch":_loot_epoch})
	return true

func _step_ground_loot() -> void:
	var ids: Array = _ground_loot.keys()
	ids.sort()
	for uid in ids:
		var entry: Dictionary = _ground_loot[uid]
		if int(entry.expires) <= tick:
			_ground_loot.erase(uid)
			_progress_emit("loot_expired",{"uid":int(uid)})
		elif equipment_valid and equipment_inventory.items_snapshot().size() < EquipmentInventory.MAX_ITEMS and player.distance_squared_to(Vector2(entry.p[0],entry.p[1])) <= PICKUP_RADIUS*PICKUP_RADIUS:
			pickup_loot(loot_handle(int(uid)))

func claim_death_reward(identity: Dictionary) -> bool:
	var state: Dictionary = entity(identity)
	if state.is_empty() or state.state != "dead" or int(state.id) < 1 or int(state.id) > MAX_ENTITIES or int(_reward_claims.get(int(state.id),0)) >= int(state.generation): return false
	_reward_claims[int(state.id)] = int(state.generation)
	var old_level: int = progression.level()
	var earned: int = progression.award()
	# Level changes only owner eligibility; derived combat values are unchanged.
	if equipment_valid:
		equipment_inventory.replace_context({"actor_tag":"caster","level":progression.level()})
	_progress_emit("xp_awarded",{"entity":handle(state),"amount":earned,"xp":progression.xp})
	if old_level != progression.level(): _progress_emit("level_up",progression.snapshot())
	if loot_catalog == null:
		_progress_emit("loot_result",{"entity":handle(state),"reason":"definitions_unavailable"})
		return true
	var selection: Dictionary = loot_catalog.roll(loot_rng)
	var reason := "no_drop"
	var item: Dictionary = {}
	if selection.get("kind") == "item":
		if _ground_loot.size() >= GROUND_CAPACITY: reason = "ground_full"
		else:
			item = equipment_inventory.reserve_item(selection.base_id,selection.quality)
			if item.is_empty(): reason = "uid_exhausted"
			else:
				reason = "ground_created"
				_ground_loot[int(item.uid)] = {"item":item.duplicate(true),"p":[state.p.x,state.p.y],"expires":tick+LOOT_TTL}
	_progress_emit("loot_result",{"entity":handle(state),"selection":selection,"reason":reason,"uid":int(item.get("uid",0))})
	return true

func progress_document() -> Dictionary:
	if not equipment_valid or loot_catalog == null: return {}
	var claims: Array = []
	var ids: Array = _reward_claims.keys()
	ids.sort()
	for id_ in ids: claims.append({"id":int(id_),"generation":int(_reward_claims[id_])})
	var ground: Array = []
	for entry in ground_loot_snapshot():
		ground.append({"item":entry.item,"p":entry.p,"remaining_ticks":entry.remaining_ticks})
	return {"schema_version":1,"loot_sha256":loot_catalog.content_fingerprint(),"xp":progression.xp,"equipment":equipment_snapshot(),"loot_rng_state":str(loot_rng.state),"ground":ground,"generation_high_water":_generation_high_water,"claims":claims}

func _prepare_progress(candidate: Variant) -> Dictionary:
	progress_errors.clear()
	if not equipment_valid or loot_catalog == null or not candidate is Dictionary or candidate.size() != 8 or not candidate.has_all(["schema_version","loot_sha256","xp","equipment","loot_rng_state","ground","generation_high_water","claims"]):
		progress_errors.assign(["Invalid progress document fields or unavailable definitions"])
		return {}
	if not Catalog.integer(candidate.schema_version,1,1) or candidate.loot_sha256 != loot_catalog.content_fingerprint() or not Catalog.integer(candidate.xp,0,Progression.MAX_XP) or not EquipmentInventory.state_integer(candidate.loot_rng_state) or not Catalog.integer(candidate.generation_high_water,0,MAX_COUNTER-1) or not candidate.ground is Array or candidate.ground.size() > GROUND_CAPACITY or not candidate.claims is Array or candidate.claims.size() > MAX_ENTITIES:
		progress_errors.assign(["Invalid progress version/fingerprint/counters/capacity"])
		return {}
	var proposed_progress := Progression.new()
	proposed_progress.xp = int(candidate.xp)
	var trial_inventory = EquipmentInventory.new(equipment_catalog,Callable(),{"actor_tag":"caster","level":proposed_progress.level()})
	if not trial_inventory.replace_document(candidate.equipment):
		progress_errors = trial_inventory.errors.duplicate()
		return {}
	var all_uids := {}
	for item in trial_inventory.items_snapshot(): all_uids[int(item.uid)] = true
	var ground: Dictionary = {}
	for entry in candidate.ground:
		if not entry is Dictionary or entry.size() != 3 or not entry.has_all(["item","p","remaining_ticks"]) or not entry.p is Array or entry.p.size() != 2 or not Catalog.integer(entry.remaining_ticks,1,LOOT_TTL):
			progress_errors.assign(["Invalid ground entry fields/lifetime"])
			return {}
		for coordinate in entry.p:
			if not (coordinate is int or coordinate is float) or not is_finite(float(coordinate)) or absf(float(coordinate)) > 1000000:
				progress_errors.assign(["Invalid ground position"])
				return {}
		var probe: Dictionary = trial_inventory.snapshot()
		probe.items = [entry.item]
		probe.equipped = {}
		if not trial_inventory.validate(probe).is_empty():
			progress_errors.assign(["Invalid reserved item or shared UID counter"])
			return {}
		var uid: int = int(entry.item.uid)
		if all_uids.has(uid):
			progress_errors.assign(["Duplicate owned/ground UID"])
			return {}
		all_uids[uid] = true
		ground[uid] = {"item":entry.item.duplicate(true),"p":[float(entry.p[0]),float(entry.p[1])],"expires":int(entry.remaining_ticks)}
	var claims: Dictionary = {}
	var floor_value: int = maxi(_generation_high_water,int(candidate.generation_high_water))
	for claim in candidate.claims:
		if not claim is Dictionary or claim.size() != 2 or not claim.has_all(["id","generation"]) or not Catalog.integer(claim.id,1,MAX_ENTITIES) or not Catalog.integer(claim.generation,1,int(candidate.generation_high_water)) or claims.has(int(claim.id)):
			progress_errors.assign(["Invalid or duplicate death claim"])
			return {}
		claims[int(claim.id)] = int(claim.generation)
	for id_ in _reward_claims:
		claims[id_] = maxi(int(claims.get(id_,0)),int(_reward_claims[id_]))
	for generation in claims.values(): floor_value = maxi(floor_value,int(generation))
	if floor_value >= MAX_COUNTER or _loot_epoch >= MAX_COUNTER:
		progress_errors.assign(["Generation/epoch counter exhausted"])
		return {}
	var definitions: Dictionary = catalog.snapshot()
	var block := StatBlock.new(_stat_definitions,{_health_stat_id:int(definitions.player.max_health_raw),_mana_stat_id:int(definitions.player.max_mana_raw)})
	var gear: Array = trial_inventory._modifiers_for(trial_inventory.snapshot())
	var modifiers: Array = _external_modifiers.duplicate(true)
	modifiers.append_array(gear)
	if not block.replace_modifiers(modifiers):
		progress_errors = block.errors.duplicate()
		return {}
	return {"inventory":trial_inventory,"progression":proposed_progress,"ground":ground,"claims":claims,"floor":floor_value,"block":block,"gear":gear,"loot_rng_state":String(candidate.loot_rng_state).to_int()}

func replace_progress_document(candidate: Variant) -> bool:
	var prepared: Dictionary = _prepare_progress(candidate)
	if prepared.is_empty(): return false
	# All parsing, references, counters and derived stats are validated above.
	# Publish once; no fallible operations follow this point.
	var previous_life: float = life
	var previous_mana: int = mana_raw
	equipment_inventory = prepared.inventory
	equipment_inventory._apply = _apply_equipment_modifiers
	progression = prepared.progression
	player_stats = prepared.block
	_equipment_modifiers = prepared.gear
	life_max_raw = player_stats.value(_health_stat_id)
	mana_max_raw = player_stats.value(_mana_stat_id)
	_generation_floor = int(prepared.floor)
	_generation_high_water = int(prepared.floor)
	_reward_claims = prepared.claims
	loot_rng.state = int(prepared.loot_rng_state)
	reset()
	_ground_loot = prepared.ground
	life = minf(previous_life,float(life_max_raw)/UNIT)
	mana_raw = mini(previous_mana,mana_max_raw)
	_progress_emit("progress_loaded",progression.snapshot())
	return true

func save_progress(path: String = ProgressStorage.PATH) -> bool:
	var candidate: Dictionary = progress_document()
	if _prepare_progress(candidate).is_empty(): return false
	var storage := ProgressStorage.new()
	var accepted: bool = storage.write_document(candidate,path)
	progress_errors = storage.errors.duplicate()
	return accepted

func load_progress(path: String = ProgressStorage.PATH) -> bool:
	var storage := ProgressStorage.new()
	var candidate: Variant = storage.read_document(path)
	if candidate == null:
		progress_errors = storage.errors.duplicate()
		return false
	return replace_progress_document(candidate)
func progress_history_snapshot() -> Array:
	return progress_history.duplicate(true)
