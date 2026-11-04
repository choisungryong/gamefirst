extends RefCounted
## Independent, transactional equipment definitions. Not recovered D2R rolls.
const Rules = preload("res://data/game_catalog.gd")
const PATH := "res://game_data/equipment.json"
const SLOTS := ["focus","body","charm"]
var errors: Array[String] = []
var _document: Dictionary = {}
var _stats: Dictionary = {}
var _frozen := false
var _rules_fingerprint := ""

func _init(stat_definitions: Array = [], rules_fingerprint: String = "") -> void:
	# Internal constructor contract: stat_definitions came from a successfully
	# validated GameCatalog snapshot. JSON/user candidates enter replace_document.
	_rules_fingerprint = rules_fingerprint
	for stat in stat_definitions: _stats[stat.id] = stat.duplicate(true)

func load_file(path: String = PATH) -> bool:
	var file := FileAccess.open(path,FileAccess.READ)
	if file == null:
		errors.assign(["Cannot read equipment catalog"])
		return false
	return load_text(file.get_as_text())

func load_text(text: String) -> bool:
	var parser := JSON.new()
	if parser.parse(text) != OK:
		errors.assign(["Invalid equipment JSON"])
		return false
	return replace_document(parser.data)

static func identifier(value: Variant, prefix: String) -> bool:
	return value is String and value.begins_with(prefix) and value.length() > prefix.length() and value.length() <= 96

static func strings(value: Variant, maximum: int = 8) -> bool:
	if not value is Array or value.is_empty() or value.size() > maximum: return false
	var seen := {}
	for item in value:
		if not item is String or item.is_empty() or item.length() > 64 or seen.has(item): return false
		seen[item] = true
	return true

func modifier_valid(value: Variant, rolled: bool = false) -> bool:
	if not value is Dictionary: return false
	var required: Array = ["stat_id","operation","minimum","maximum","step"] if rolled else ["id","stat_id","operation","value"]
	if value.size() != required.size() or not value.has_all(required) or not _stats.has(value.stat_id): return false
	if not value.operation in ["add","percent_bps"]: return false
	var minimum: int = -1000000000 if value.operation == "add" else -10000
	var maximum: int = 1000000000 if value.operation == "add" else 100000
	if rolled:
		return Rules.integer(value.minimum,minimum,maximum) and Rules.integer(value.maximum,minimum,maximum) and Rules.integer(value.step,1,1000000000) and value.minimum <= value.maximum and (int(value.maximum)-int(value.minimum))%int(value.step) == 0
	return identifier(value.id,"") and Rules.integer(value.value,minimum,maximum)

func validate(candidate: Variant) -> Array[String]:
	var found: Array[String] = []
	if not candidate is Dictionary or not candidate.has_all(["schema_version","catalog_id","definition_version","items","affixes","provenance"]):
		found.append("Equipment document fields missing")
		return found
	if not Rules.integer(candidate.schema_version,1,1) or not identifier(candidate.catalog_id,"equipment.") or not Rules.integer(candidate.definition_version,1): found.append("Invalid equipment version/ID")
	if not Rules.provenance(candidate.provenance): found.append("Equipment must declare independent provenance")
	if not candidate.items is Array or candidate.items.is_empty() or candidate.items.size() > 32 or not candidate.affixes is Array or candidate.affixes.size() > 32:
		found.append("Invalid equipment definition capacity")
		return found
	var affixes := {}
	for affix in candidate.affixes:
		if not affix is Dictionary or not affix.has_all(["id","display_name","required_tag","group","modifier"]) or not identifier(affix.get("id"),"affix."):
			found.append("Invalid affix fields")
			continue
		if affixes.has(affix.id) or not identifier(affix.display_name,"") or not identifier(affix.required_tag,"") or not identifier(affix.group,"") or not modifier_valid(affix.modifier,true): found.append("Invalid affix definition: "+str(affix.id))
		affixes[affix.id] = affix
	var seen := {}
	for item in candidate.items:
		if not item is Dictionary or not item.has_all(["id","display_name","slot","tags","minimum_level","actor_tag","base_modifiers","affix_ids"]) or not identifier(item.get("id"),"item."):
			found.append("Invalid item fields")
			continue
		if seen.has(item.id) or not identifier(item.display_name,"") or not item.slot in SLOTS or not strings(item.tags) or not Rules.integer(item.minimum_level,1,100) or not identifier(item.actor_tag,""):
			found.append("Invalid item definition: "+str(item.id))
		seen[item.id] = true
		if not item.base_modifiers is Array or item.base_modifiers.size() > 4 or not strings(item.affix_ids,4):
			found.append("Invalid item modifier/affix list")
			continue
		var modifier_ids := {}
		for modifier in item.base_modifiers:
			if not modifier_valid(modifier) or modifier_ids.has(modifier.get("id")): found.append("Invalid/duplicate base modifier")
			else: modifier_ids[modifier.id] = true
		for id_ in item.affix_ids:
			if not affixes.has(id_): found.append("Unknown affix reference")
			elif not item.tags is Array or not affixes[id_].required_tag in item.tags: found.append("Ineligible affix reference")
	return found

func replace_document(candidate: Variant) -> bool:
	if _frozen:
		errors.assign(["Runtime equipment definitions are frozen"])
		return false
	errors = validate(candidate)
	if not errors.is_empty(): return false
	_document = candidate.duplicate(true)
	return true

func frozen_copy() -> RefCounted:
	var copy = get_script().new(_stats.values(),_rules_fingerprint)
	if not copy.replace_document(snapshot()): return copy
	copy._frozen = true
	return copy

func content_fingerprint() -> String:
	return JSON.stringify({"equipment":_document,"stats":_stats,"combat_rules":_rules_fingerprint},"",true,true).sha256_text()

func snapshot() -> Dictionary:
	return _document.duplicate(true)

func definition(group: String, id_: String) -> Dictionary:
	for value in _document.get(group,[]):
		if value.id == id_: return value.duplicate(true)
	return {}
