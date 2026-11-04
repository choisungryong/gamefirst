extends RefCounted
## Independent chapter1 definitions. Not recovered SACRATA/D2R rules.
## JSON/FileAccess transaction pattern follows data/game_catalog.gd.
const DEFAULT_PATH := "res://chapter1/data/growth.json"
const LIMITS := {
	"damage_raw":[1,1000000], "cooldown_ticks":[1,3600], "projectiles":[0,16],
	"chain_targets":[0,32], "branches":[1,4], "pierce":[0,32], "radius_cm":[0,2000],
	"slow_bps":[0,10000], "freeze_stacks":[0,20], "shatter_count":[0,16],
	"death_burst":[0,1], "proc_depth":[0,1], "hit_budget":[1,128]
}
var errors: Array[String] = []
var _document: Dictionary = {}

static func integer(v: Variant, low: int, high: int) -> bool:
	return (v is int or v is float) and is_finite(float(v)) and float(v) == floor(float(v)) and v >= low and v <= high

static func keys_match(v: Dictionary, names: Array) -> bool:
	if v.size() != names.size(): return false
	for key in names:
		if not v.has(key): return false
	return true

static func effects_valid(v: Variant) -> bool:
	if not v is Dictionary or not keys_match(v, LIMITS.keys()): return false
	for key in LIMITS:
		if not integer(v[key], LIMITS[key][0], LIMITS[key][1]): return false
	return v.projectiles > 0 or v.chain_targets > 0

static func validate(v: Variant) -> Array[String]:
	var issues: Array[String] = []
	if not v is Dictionary or not keys_match(v, ["schema_version","provenance","max_active_skills","max_passives","xp_thresholds","passives","skills"]):
		return ["growth root fields"]
	if not integer(v.schema_version,1,1) or v.provenance != "independent_design": issues.append("version/provenance")
	if not integer(v.max_active_skills,3,3) or not integer(v.max_passives,3,3): issues.append("chapter1 slot limits")
	if not v.xp_thresholds is Array or v.xp_thresholds.size() != 12: return ["12 XP thresholds required"]
	var previous := -1
	for amount in v.xp_thresholds:
		if not integer(amount,0,1000000) or amount <= previous: return ["XP thresholds must strictly increase"]
		previous = int(amount)
	if v.xp_thresholds[0] != 0: issues.append("level1 begins at zero")
	if not v.passives is Array or v.passives.size() != 3: return ["three passive definitions required"]
	var passive_ids: Array[String] = []
	for p in v.passives:
		if not p is Dictionary or not keys_match(p,["id","name","weight"]): return ["passive fields"]
		if not p.id is String or not p.id.begins_with("chapter1.passive.") or p.id in passive_ids: return ["passive id"]
		if not p.name is String or p.name.is_empty() or not integer(p.weight,1,10000): return ["passive name/weight"]
		passive_ids.append(p.id)
	if not v.skills is Array or v.skills.size() != 3: return ["three skills required"]
	var skill_ids: Array[String] = []
	var linked_passives: Array[String] = []
	for s in v.skills:
		if not s is Dictionary or not keys_match(s,["id","name","weight","passive_id","evolution_name","ranks","evolution"]): return ["skill fields"]
		if not s.id is String or not s.id.begins_with("chapter1.skill.") or s.id in skill_ids: return ["skill id"]
		if not s.name is String or s.name.is_empty() or not s.evolution_name is String or s.evolution_name.is_empty(): return ["skill names"]
		if not integer(s.weight,1,10000) or not s.passive_id is String or not s.passive_id in passive_ids or s.passive_id in linked_passives: return ["skill passive/weight"]
		if not s.ranks is Array or s.ranks.size() != 4: return ["four ranks per skill required"]
		for effect in s.ranks:
			if not effects_valid(effect): return ["rank effects outside chapter1 budget"]
		if not effects_valid(s.evolution): return ["evolution effects outside chapter1 budget"]
		skill_ids.append(s.id)
		linked_passives.append(s.passive_id)
	return issues

func load_file(path: String = DEFAULT_PATH) -> bool:
	var file := FileAccess.open(path,FileAccess.READ)
	if file == null:
		errors.assign(["Cannot read growth definitions: "+path])
		return false
	var parser := JSON.new()
	if parser.parse(file.get_as_text()) != OK:
		errors.assign(["Growth JSON line %d: %s" % [parser.get_error_line(),parser.get_error_message()]])
		return false
	return replace_document(parser.data)

func replace_document(candidate: Variant) -> bool:
	errors = validate(candidate)
	if not errors.is_empty(): return false
	_document = candidate.duplicate(true)
	return true

func snapshot() -> Dictionary:
	return _document.duplicate(true)
