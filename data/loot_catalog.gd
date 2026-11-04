extends RefCounted
## Independent flat weighted selection. Nested tables/references are rejected.
const Rules = preload("res://data/game_catalog.gd")
const PATH := "res://game_data/loot.json"
var errors: Array[String] = []
var _document: Dictionary = {}
var _equipment: RefCounted
var _frozen := false
func _init(equipment: RefCounted) -> void:
	_equipment = equipment.frozen_copy()
func load_file(path: String = PATH) -> bool:
	var parser := JSON.new()
	if parser.parse(FileAccess.get_file_as_string(path)) != OK:
		errors.assign(["Invalid loot JSON"])
		return false
	return replace_document(parser.data)
func validate(candidate: Variant) -> Array[String]:
	var found: Array[String] = []
	if not candidate is Dictionary or candidate.size() != 5 or not candidate.has_all(["schema_version","catalog_id","definition_version","entries","provenance"]):
		found.append("Invalid flat loot document")
		return found
	if not Rules.integer(candidate.schema_version,1,1) or candidate.catalog_id != "loot.prototype" or not Rules.integer(candidate.definition_version,1,2147483647) or not Rules.provenance(candidate.provenance): found.append("Invalid loot version/provenance")
	if not candidate.entries is Array or candidate.entries.is_empty() or candidate.entries.size() > 32:
		found.append("Invalid loot entry capacity")
		return found
	var total := 0
	for entry in candidate.entries:
		if not entry is Dictionary or not entry.has_all(["kind","weight"]) or not Rules.integer(entry.weight,0,1000000):
			found.append("Invalid loot weight/fields")
			continue
		total += int(entry.weight)
		if entry.kind == "no-drop":
			if entry.size() != 2: found.append("No-drop accepts no reference")
		elif entry.kind == "item":
			if entry.size() != 4 or not entry.has_all(["base_id","quality"]) or not entry.base_id is String or _equipment.definition("items",entry.base_id).is_empty() or not entry.quality in ["common","crafted"]: found.append("Invalid item/quality reference")
		else: found.append("Nested/unknown loot kind unsupported")
	if total <= 0: found.append("Loot total weight must be positive")
	return found
func replace_document(candidate: Variant) -> bool:
	if _frozen:
		errors.assign(["Runtime loot definitions frozen"])
		return false
	errors = validate(candidate)
	if not errors.is_empty(): return false
	_document = candidate.duplicate(true)
	return true
func freeze() -> void:
	_frozen = true
func snapshot() -> Dictionary:
	return _document.duplicate(true)
func content_fingerprint() -> String:
	return JSON.stringify({"loot":_document,"equipment":_equipment.content_fingerprint()},"",true,true).sha256_text()
func roll(rng: RandomNumberGenerator) -> Dictionary:
	if _document.is_empty(): return {}
	var total := 0
	for entry in _document.entries: total += int(entry.weight)
	var selected: int = rng.randi_range(1,total)
	for entry in _document.entries:
		selected -= int(entry.weight)
		if selected <= 0: return entry.duplicate(true)
	return {}
