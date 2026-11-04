extends RefCounted
## Phase 1: transactional, detached definition catalog; no runtime HP/cooldowns.
## JSON.parse/error pattern: https://docs.godotengine.org/en/4.5/classes/class_json.html
## FileAccess: https://docs.godotengine.org/en/4.5/classes/class_fileaccess.html
const DEFAULT_PATH := "res://game_data/catalog.json"
const STATUSES := ["observed", "derived", "hypothesis", "design_choice", "unknown"]
var errors: Array[String] = []
var _document: Dictionary = {}

func load_file(path: String = DEFAULT_PATH) -> bool:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		errors.assign(["Cannot read catalog: " + path])
		return false
	return load_text(file.get_as_text())

func load_text(text: String) -> bool:
	var parser := JSON.new()
	var result: Error = parser.parse(text)
	if result != OK:
		errors.assign(["JSON line %d: %s" % [parser.get_error_line(), parser.get_error_message()]])
		return false
	return replace_document(parser.data)

func replace_document(candidate: Variant) -> bool:
	errors = validate(candidate)
	if not errors.is_empty(): return false
	# Publish only after the entire candidate passes. Never expose a shared mutable definition.
	_document = candidate.duplicate(true)
	return true

func snapshot() -> Dictionary:
	return _document.duplicate(true)

func definition(group: String, id_: String) -> Dictionary:
	for value in _document.get(group, []):
		if value.id == id_: return value.duplicate(true)
	return {}

static func integer(value: Variant, minimum: int = 0, maximum: int = 2147483647) -> bool:
	if not (value is int or value is float): return false
	return is_finite(float(value)) and float(value) == floor(float(value)) and value >= minimum and value <= maximum

static func number(value: Variant, minimum: float = 0.0, maximum: float = 1000000.0) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and value >= minimum and value <= maximum

static func vector_pair(value: Variant, positive: bool = false) -> bool:
	return value is Array and value.size() == 2 and number(value[0], 0.001 if positive else -100000.0) and number(value[1], 0.001 if positive else -100000.0)

static func provenance(value: Variant) -> bool:
	return value is Dictionary and value.get("status") == "design_choice" and value.get("method") == "project_design" and value.get("note") is String and not value.note.is_empty()

static func has_reference(value: Variant, expected: String, ids: Dictionary) -> bool:
	return value is String and ids.get(value) == expected

static func sha256_text(value: Variant) -> bool:
	if not value is String or value.length() != 64: return false
	for character in value:
		if not character in "0123456789abcdefABCDEF": return false
	return true

static func source_locator(value: Variant) -> bool:
	return value is Dictionary and value.get("path") is String and not value.path.is_empty() and sha256_text(value.get("sha256"))

static func require_keys(value: Dictionary, keys: Array, prefix: String, found: Array[String]) -> bool:
	var valid := true
	for key in keys:
		if not value.has(key):
			found.append(prefix + "." + key + " missing")
			valid = false
	return valid

static func validate(candidate: Variant) -> Array[String]:
	var found: Array[String] = []
	if not candidate is Dictionary:
		found.append("Catalog root must be an object")
		return found
	var d: Dictionary = candidate
	if not require_keys(d,["schema_version","catalog_id","definition_version","numeric_scale","simulation_hz","stats","player","skills","projectiles","enemies","experiment","provenance","evidence_index"],"catalog",found): return found
	if not integer(d.schema_version,1,1): found.append("Unsupported schema_version")
	if not (d.catalog_id is String and d.catalog_id.begins_with("catalog.")): found.append("Invalid catalog ID")
	if not integer(d.definition_version,1): found.append("Invalid definition_version")
	if not integer(d.numeric_scale,256,256): found.append("Phase1 numeric_scale must be256")
	if not integer(d.simulation_hz,60,60): found.append("Phase1 simulation_hz must be60")
	if not provenance(d.provenance): found.append("Catalog must explicitly declare independent design provenance")
	var evidence_ids: Dictionary = {}
	if not d.evidence_index is Array:
		found.append("evidence_index must be an array")
	else:
		for evidence in d.evidence_index:
			if not evidence is Dictionary or not require_keys(evidence,["id","method","status","scope","locator"],"evidence_index",found): continue
			if not evidence.id is String or evidence.id.is_empty() or evidence_ids.has(evidence.id):
				found.append("Invalid/duplicate evidence ID")
			else: evidence_ids[evidence.id] = true
			if not evidence.method in ["classic_reference","runtime_observation"] or not evidence.status in ["observed","derived"]: found.append("Invalid evidence method/status")
			if not evidence.scope is String or evidence.scope.is_empty() or not source_locator(evidence.locator): found.append("Invalid evidence scope/locator")
	var ids: Dictionary = {}
	for group in ["stats","skills","projectiles","enemies"]:
		if not d[group] is Array or d[group].is_empty():
			found.append(group+" must be a nonempty array")
			continue
		for item in d[group]:
			if not item is Dictionary or not item.get("id") is String:
				found.append(group+" entry must have a string ID")
				continue
			var id_: String = item.id
			var prefix: String = {"stats":"stat.","skills":"skill.","projectiles":"projectile.","enemies":"enemy."}[group]
			if not id_.begins_with(prefix) or id_.length() <= prefix.length(): found.append("Invalid ID: "+id_)
			if ids.has(id_): found.append("Duplicate ID: "+id_)
			ids[id_] = group
	if not found.is_empty(): return found
	for stat in d.stats:
		if not require_keys(stat,["unit","scale","provenance"],stat.id,found): continue
		if not (stat.unit is String and stat.unit in ["health","mana","basis_points","count"]): found.append(stat.id+" invalid unit")
		var expected_scale: int = 10000 if stat.unit == "basis_points" else (1 if stat.unit == "count" else 256)
		if not integer(stat.scale,expected_scale,expected_scale): found.append(stat.id+" invalid scale")
		if not provenance(stat.provenance): found.append(stat.id+" invalid provenance")
		if stat.has("minimum_raw") or stat.has("maximum_raw") or stat.has("default_raw"):
			if not require_keys(stat,["minimum_raw","maximum_raw","default_raw"],stat.id,found): continue
			if not integer(stat.minimum_raw,-2147483647) or not integer(stat.maximum_raw,-2147483647) or not integer(stat.default_raw,-2147483647): found.append(stat.id+" invalid stat bounds/default")
			elif stat.minimum_raw > stat.maximum_raw or stat.default_raw < stat.minimum_raw or stat.default_raw > stat.maximum_raw: found.append(stat.id+" inverted stat bounds/default")
	if not found.is_empty(): return found
	var stat_units: Dictionary = {}
	for stat in d.stats: stat_units[stat.id] = stat.get("unit")
	var stat_definitions: Dictionary = {}
	for stat in d.stats: stat_definitions[stat.id] = stat
	# Optional for historical v1 catalogs; v2 explicitly declares these combat
	# semantics. Do not accept a definition which the runtime would reinterpret.
	var semantics: Dictionary = {"stat.spell_power":["basis_points",-10000,100000],"stat.cast_speed":["basis_points",-7500,30000],"stat.mana_cost":["basis_points",-9000,100000],"stat.flat_reduction":["health",0,2147483647],"stat.resist.fire":["basis_points",-10000,10000],"stat.resist.cold":["basis_points",-10000,10000],"stat.resist.lightning":["basis_points",-10000,10000],"stat.resist.physical":["basis_points",-10000,10000]}
	for id_ in semantics:
		if not stat_definitions.has(id_):
			if d.definition_version >= 2: found.append("Missing combat stat: "+id_)
			continue
		var stat: Dictionary = stat_definitions[id_]
		var rule: Array = semantics[id_]
		if stat.unit != rule[0] or not integer(stat.get("minimum_raw"),int(rule[1]),int(rule[2])) or not integer(stat.get("maximum_raw"),int(rule[1]),int(rule[2])): found.append(id_+" incompatible combat unit/bounds")
	if d.definition_version >= 3:
		var level_stat: Dictionary = stat_definitions.get("stat.skill.ember_level",{})
		if level_stat.get("unit") != "count" or not integer(level_stat.get("minimum_raw"),0,0) or not integer(level_stat.get("maximum_raw"),20,20) or not integer(level_stat.get("default_raw"),0,0): found.append("Invalid independent skill bonus stat")
	if not d.player is Dictionary or not d.experiment is Dictionary:
		found.append("player and experiment must be objects")
		return found
	var p: Dictionary = d.player
	if require_keys(p,["id","health_stat_id","mana_stat_id","max_health_raw","max_mana_raw","move_speed_world_per_second","spawn_world","provenance"],"player",found):
		if p.id != "actor.caster": found.append("Unsupported player ID")
		if not has_reference(p.health_stat_id,"health",stat_units) or not has_reference(p.mana_stat_id,"mana",stat_units): found.append("Player stat reference/unit mismatch")
		if not integer(p.max_health_raw,1) or not integer(p.max_mana_raw,0): found.append("Invalid player maxima")
		for pair in [[p.health_stat_id,p.max_health_raw],[p.mana_stat_id,p.max_mana_raw]]:
			if stat_definitions.has(pair[0]):
				var stat: Dictionary = stat_definitions[pair[0]]
				if not integer(pair[1],int(stat.get("minimum_raw",0)),int(stat.get("maximum_raw",2147483647))): found.append("Player maximum outside stat bounds")
				var floor_raw: int = 1 if pair[0] == p.health_stat_id else 0
				if int(stat.get("minimum_raw",floor_raw)) < floor_raw: found.append("Player stat bounds allow invalid negative/zero maximum")
		if not number(p.move_speed_world_per_second,.001) or not vector_pair(p.spawn_world): found.append("Invalid player movement/spawn")
		if not provenance(p.provenance): found.append("Invalid player provenance")
	for projectile in d.projectiles:
		if not require_keys(projectile,["speed_world_per_second","lifetime_seconds","spawn_offset_world","collision_radius_world","provenance"],projectile.id,found): continue
		for field in ["speed_world_per_second","lifetime_seconds","collision_radius_world"]:
			if not number(projectile[field],.001): found.append(projectile.id+" invalid "+field)
		if not number(projectile.spawn_offset_world): found.append(projectile.id+" invalid spawn offset")
		if not provenance(projectile.provenance): found.append(projectile.id+" invalid provenance")
	for skill in d.skills:
		if not require_keys(skill,["cost","damage","startup_ticks","cycle_ticks","provenance"],skill.id,found): continue
		var kind: String = skill.get("kind","projectile") if skill.get("kind","projectile") is String else "invalid"
		if not kind in ["projectile","area","chain"]: found.append(skill.id+" unsupported effect kind")
		if kind == "projectile" and not has_reference(skill.get("projectile_id"),"projectiles",ids): found.append(skill.id+" unresolved projectile")
		if skill.has("display_name") and (not skill.display_name is String or skill.display_name.is_empty() or skill.display_name.length() > 32): found.append(skill.id+" invalid display name")
		if skill.has("bonus_curve"):
			var curve: Variant = skill.bonus_curve
			if not curve is Dictionary or curve.size() != 3 or not curve.has_all(["stat_id","min_per_bonus_raw","max_per_bonus_raw"]): found.append(skill.id+" invalid skill bonus curve")
			elif not has_reference(curve.stat_id,"count",stat_units) or not integer(curve.min_per_bonus_raw,0,1000000) or not integer(curve.max_per_bonus_raw,0,1000000) or curve.min_per_bonus_raw > curve.max_per_bonus_raw: found.append(skill.id+" invalid skill bonus units/range")
		if kind in ["area","chain"]:
			if not skill.get("effect") is Dictionary:
				found.append(skill.id+" effect must be an object")
			else:
				var effect: Dictionary = skill.effect
				if not integer(effect.get("max_targets"),1,64): found.append(skill.id+" invalid effect target cap")
				if kind == "area":
					if not number(effect.get("radius_world"),.01,32): found.append(skill.id+" invalid area radius")
					if effect.has("status"):
						var status: Variant = effect.status
						if not status is Dictionary or status.get("kind") != "chill" or not integer(status.get("duration_ticks"),1,36000) or not integer(status.get("slow_bps"),1,9000): found.append(skill.id+" unsupported status definition")
				else:
					if effect.has("status"): found.append(skill.id+" chain status is unsupported")
					if not number(effect.get("range_world"),.01,32) or not number(effect.get("jump_range_world"),.01,32): found.append(skill.id+" invalid chain range")
		if not integer(skill.startup_ticks,0,36000) or not integer(skill.cycle_ticks,1,36000): found.append(skill.id+" invalid timing")
		elif skill.cycle_ticks <= skill.startup_ticks: found.append(skill.id+" cycle must exceed startup")
		if not skill.cost is Dictionary or not skill.damage is Dictionary:
			found.append(skill.id+" cost/damage must be objects")
			continue
		var cost: Dictionary = skill.cost
		if require_keys(cost,["stat_id","raw","unit","scale"],skill.id+".cost",found):
			if not has_reference(cost.stat_id,"mana",stat_units) or cost.unit != "mana" or not integer(cost.scale,256,256): found.append(skill.id+" cost reference/unit mismatch")
			if not integer(cost.raw,1): found.append(skill.id+" cost must be a positive raw integer")
		var damage: Dictionary = skill.damage
		if require_keys(damage,["stat_id","min_raw","max_raw","unit","scale","element"],skill.id+".damage",found):
			if not has_reference(damage.stat_id,"health",stat_units) or damage.unit != "health" or not integer(damage.scale,256,256): found.append(skill.id+" damage reference/unit mismatch")
			if not integer(damage.min_raw,0) or not integer(damage.max_raw,0): found.append(skill.id+" damage must be raw integers")
			elif damage.min_raw > damage.max_raw: found.append(skill.id+" inverted damage range")
			if not damage.element in ["fire","cold","lightning","physical"]: found.append(skill.id+" unsupported damage element")
		if not skill.provenance is Dictionary:
			found.append(skill.id+" missing provenance map")
		else:
			for field in ["mana_cost","damage","startup","cycle"]:
				if not provenance(skill.provenance.get(field)) or not skill.provenance[field].get("basis") is Array:
					found.append(skill.id+" invalid provenance: "+field)
					continue
				for basis in skill.provenance[field].basis:
					if not basis is String or not evidence_ids.has(basis): found.append(skill.id+" unresolved provenance basis")
	for enemy in d.enemies:
		if not require_keys(enemy,["health_stat_id","max_health_raw","move_speed_world_per_second","spawn_world","attack","hurt_seconds","death_threshold_raw","provenance"],enemy.id,found): continue
		if not has_reference(enemy.health_stat_id,"health",stat_units): found.append(enemy.id+" unresolved health stat")
		if not integer(enemy.max_health_raw,1) or not integer(enemy.death_threshold_raw,0): found.append(enemy.id+" invalid health/threshold")
		elif enemy.death_threshold_raw >= enemy.max_health_raw: found.append(enemy.id+" threshold exceeds health")
		if stat_definitions.has(enemy.health_stat_id):
			var stat: Dictionary = stat_definitions[enemy.health_stat_id]
			if not integer(enemy.max_health_raw,int(stat.get("minimum_raw",0)),int(stat.get("maximum_raw",2147483647))): found.append(enemy.id+" health outside stat bounds")
		if not number(enemy.move_speed_world_per_second,.001) or not vector_pair(enemy.spawn_world) or not number(enemy.hurt_seconds): found.append(enemy.id+" invalid movement/hurt")
		if not provenance(enemy.provenance): found.append(enemy.id+" invalid provenance")
		if enemy.has("defenses"):
			if not enemy.defenses is Dictionary: found.append(enemy.id+" defenses must be an object")
			else:
				for defense_id in enemy.defenses:
					if not defense_id in ["stat.flat_reduction","stat.resist.fire","stat.resist.cold","stat.resist.lightning","stat.resist.physical"] or not stat_definitions.has(defense_id):
						found.append(enemy.id+" invalid defense stat/value")
						continue
					var stat: Dictionary = stat_definitions[defense_id]
					if not integer(enemy.defenses[defense_id],int(stat.get("minimum_raw",0)),int(stat.get("maximum_raw",2147483647))): found.append(enemy.id+" defense outside stat bounds")
		if not enemy.attack is Dictionary:
			found.append(enemy.id+" attack must be an object")
			continue
		var a: Dictionary = enemy.attack
		if require_keys(a,["windup_seconds","recovery_seconds","start_range_world","hit_range_world","damage_raw"],enemy.id+".attack",found):
			for field in ["windup_seconds","recovery_seconds","start_range_world","hit_range_world"]:
				if not number(a[field],.001): found.append(enemy.id+" invalid attack "+field)
			if not integer(a.damage_raw,0): found.append(enemy.id+" invalid attack damage")
	var e: Dictionary = d.experiment
	if require_keys(e,["skill_id","enemy_id","world_bounds","rng_seed","mana_regen_per_second","damage_selection","charge_phase","atlas_playback_fps","proxy_cast_animation_speed","provenance"],"experiment",found):
		if not has_reference(e.skill_id,"skills",ids) or not has_reference(e.enemy_id,"enemies",ids): found.append("Unresolved experiment definition")
		if not vector_pair(e.world_bounds,true): found.append("Invalid world bounds")
		if not integer(e.rng_seed,0): found.append("Seed must be an exact supported integer")
		if not number(e.mana_regen_per_second,0,0): found.append("Phase1 supports no mana regeneration")
		if e.damage_selection != "seeded uniform raw integer, reconstruction choice not D2R RNG" or e.charge_phase != "cast request, reconstruction choice": found.append("Unsupported experiment rule")
		if not integer(e.atlas_playback_fps,1,120) or not number(e.proxy_cast_animation_speed,.001,20): found.append("Invalid visual timing")
		if not provenance(e.provenance): found.append("Invalid experiment provenance")
		if vector_pair(e.world_bounds,true):
			var bounds: Array = e.world_bounds
			var positions: Array = [p.get("spawn_world")]
			for enemy in d.enemies: positions.append(enemy.get("spawn_world"))
			for position in positions:
				if vector_pair(position) and (absf(position[0]) > bounds[0] or absf(position[1]) > bounds[1]): found.append("Spawn exceeds world bounds")
	return found

static func validate_research(candidate: Variant) -> Array[String]:
	var found: Array[String] = []
	if not candidate is Dictionary or not candidate.get("claims") is Array:
		found.append("Research claims must be an array in an object")
		return found
	if not integer(candidate.get("schema_version"),1,1): found.append("Unsupported research schema")
	var ids: Dictionary = {}
	for claim in candidate.claims:
		if not claim is Dictionary or not require_keys(claim,["id","method","status","raw","normalized","unit","meaning_status","locator","limitations"],"claim",found): continue
		if not claim.id is String or claim.id.is_empty() or ids.has(claim.id): found.append("Invalid/duplicate claim ID")
		else: ids[claim.id] = true
		if not claim.raw is String: found.append("Research raw must preserve source text")
		if not claim.status in STATUSES: found.append("Invalid claim status")
		if claim.method != "local_casc_extract": found.append("Unsupported research method in phase1")
		if claim.unit != null and not claim.unit is String: found.append("Invalid research unit")
		if claim.meaning_status != "unknown": found.append("Phase1 table meaning remains unknown")
		if claim.normalized != null: found.append("Phase1 raw table claims are not normalized runtime values")
		if not source_locator(claim.locator):
			found.append("Invalid research source locator")
		else:
			var locator: Dictionary = claim.locator
			if not integer(locator.get("line"),2) or not locator.get("column") is String or locator.column.is_empty() or not locator.get("selector") is Dictionary or locator.selector.is_empty(): found.append("Missing research row/column/selector")
		if not claim.limitations is Array or claim.limitations.is_empty():
			found.append("Missing research limitations")
		else:
			for limitation in claim.limitations:
				if not limitation is String or limitation.is_empty(): found.append("Invalid research limitation")
	return found

func legacy_profile() -> Dictionary:
	if _document.is_empty(): return {}
	var d: Dictionary = _document
	var e: Dictionary = d.experiment
	var skill: Dictionary = definition("skills",e.skill_id)
	# This compatibility profile keeps projectile defaults for old callers even
	# when a new non-projectile skill is the selected experiment skill.
	var fallback_projectile: String = d.projectiles[0].id
	var bolt: Dictionary = definition("projectiles",skill.get("projectile_id",fallback_projectile))
	var enemy: Dictionary = definition("enemies",e.enemy_id)
	var p: Dictionary = {
		"simulation_hz":int(d.simulation_hz),"repeat_seconds":float(skill.cycle_ticks)/float(d.simulation_hz),
		"projectile_world_speed":bolt.speed_world_per_second,"projectile_life_seconds":bolt.lifetime_seconds,
		"collision_radius":bolt.collision_radius_world,"enemy_hp":float(enemy.max_health_raw)/256.0,
		"enemy_speed":enemy.move_speed_world_per_second,"enemy_attack_windup_seconds":enemy.attack.windup_seconds,
		"enemy_attack_recovery_seconds":enemy.attack.recovery_seconds,"enemy_attack_start_range":enemy.attack.start_range_world,
		"enemy_attack_hit_range":enemy.attack.hit_range_world,"enemy_damage":float(enemy.attack.damage_raw)/256.0,
		"player_world_speed":d.player.move_speed_world_per_second,"mana_regen_per_second":e.mana_regen_per_second,
		"damage_selection":e.damage_selection,"charge_phase":e.charge_phase,"enemy_hurt_seconds":enemy.hurt_seconds,
		"death_threshold_raw":enemy.death_threshold_raw,"spawn_player_world":d.player.spawn_world.duplicate(),
		"spawn_enemy_world":enemy.spawn_world.duplicate(),"projectile_spawn_offset":bolt.spawn_offset_world,
		"rng_seed":e.rng_seed,"atlas_playback_fps":e.atlas_playback_fps,
		"proxy_cast_animation_speed":e.proxy_cast_animation_speed,"world_bounds":e.world_bounds.duplicate(),
		"status":"experiment assumptions; not original final values"
	}
	return {"player":{"life":float(d.player.max_health_raw)/256.0,"mana_raw":int(d.player.max_mana_raw),"raw_unit":256},"firebolt":{"mana_cost_raw":int(skill.cost.raw),"damage_raw":[int(skill.damage.min_raw),int(skill.damage.max_raw)],"visible_startup_seconds":float(skill.startup_ticks)/float(d.simulation_hz)},"provisional_parameters":p}

