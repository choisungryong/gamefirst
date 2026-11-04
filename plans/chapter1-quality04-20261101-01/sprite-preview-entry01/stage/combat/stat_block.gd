extends RefCounted
## Independent modifier rules; these are not recovered D2R stacking rules.
## All additions are exact integers. One signed floor follows aggregated percent.
const MAX_MODIFIERS := 64
const MAX_FLAT := 1000000000
const MIN_INT := -2147483647
const MAX_INT := 2147483647
var errors: Array[String] = []
var valid := false
var _definitions: Dictionary = {}
var _base: Dictionary = {}
var _values: Dictionary = {}
var _modifiers: Array = []

func _init(definitions: Array = [], base_values: Dictionary = {}) -> void:
	for definition in definitions:
		if not definition is Dictionary or not definition.get("id") is String or definition.id.is_empty() or definition.id.length() > 128 or _definitions.has(definition.id):
			errors.append("Invalid or duplicate stat definition")
			continue
		var d: Dictionary = definition.duplicate(true)
		if not d.get("unit") is String:
			errors.append("Invalid stat unit: "+str(d.id))
			continue
		var unit: String = d.unit
		var expected_scale: int = 10000 if unit == "basis_points" else (1 if unit == "count" else 256)
		if not unit in ["health","mana","basis_points","count"] or not whole(d.get("scale"),expected_scale,expected_scale):
			errors.append("Invalid stat unit/scale: "+str(d.id))
			continue
		d["minimum_raw"] = d.get("minimum_raw",0)
		d["maximum_raw"] = d.get("maximum_raw",MAX_INT)
		d["default_raw"] = d.get("default_raw",0)
		if not whole(d.minimum_raw,MIN_INT,MAX_INT) or not whole(d.maximum_raw,MIN_INT,MAX_INT) or not whole(d.default_raw,MIN_INT,MAX_INT) or d.minimum_raw > d.maximum_raw or d.default_raw < d.minimum_raw or d.default_raw > d.maximum_raw:
			errors.append("Invalid stat bounds/default: "+str(d.id))
			continue
		_definitions[d.id] = d
		_base[d.id] = int(d.default_raw)
	for id_ in base_values:
		if not _definitions.has(id_) or not whole(base_values[id_],MIN_INT,MAX_INT):
			errors.append("Invalid base stat: "+str(id_))
			continue
		var d: Dictionary = _definitions[id_]
		if base_values[id_] < d.minimum_raw or base_values[id_] > d.maximum_raw:
			errors.append("Base outside stat bounds: "+str(id_))
			continue
		_base[id_] = int(base_values[id_])
	if not errors.is_empty(): return
	valid = true
	replace_modifiers([])

static func whole(value: Variant, minimum: int, maximum: int) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and float(value) == floor(float(value)) and value >= minimum and value <= maximum

@warning_ignore("integer_division")
static func floor_ratio(numerator: int, denominator: int) -> int:
	assert(denominator > 0)
	# Division truncates toward zero. Correct only the negative remainder, so
	# INT64_MIN never needs to be negated and every positive divisor is safe.
	var quotient: int = numerator/denominator
	return quotient-1 if numerator < 0 and numerator%denominator != 0 else quotient

func replace_modifiers(candidate: Variant) -> bool:
	var found: Array[String] = []
	if not valid or not candidate is Array:
		errors.assign(["Modifiers require a valid stat block and an array"])
		return false
	if candidate.size() > MAX_MODIFIERS: found.append("Modifier capacity exceeded")
	var identities: Dictionary = {}
	var accepted: Array = []
	for item in candidate:
		if not item is Dictionary:
			found.append("Modifier must be an object")
			continue
		if item.size() != 5 or not item.has_all(["source_id","id","stat_id","operation","value"]):
			found.append("Unsupported modifier fields")
			continue
		if not item.source_id is String or item.source_id.is_empty() or item.source_id.length() > 128 or not item.id is String or item.id.is_empty() or item.id.length() > 128:
			found.append("Modifier source/id must be nonempty strings")
			continue
		var identity: String = JSON.stringify([item.source_id,item.id])
		if identities.has(identity): found.append("Duplicate modifier source/id")
		identities[identity] = true
		if not item.stat_id is String or not _definitions.has(item.stat_id): found.append("Unknown modifier stat")
		if item.operation == "add":
			if not whole(item.value,-MAX_FLAT,MAX_FLAT): found.append("Flat modifier outside supported integer range")
		elif item.operation == "percent_bps":
			if not whole(item.value,-10000,100000): found.append("Percent modifier outside supported integer range")
		else: found.append("Unsupported modifier operation")
		accepted.append(item.duplicate(true))
	if not found.is_empty():
		errors = found
		return false
	var sums: Dictionary = {}
	for id_ in _definitions: sums[id_] = {"flat":0,"bps":0}
	for item in accepted:
		if item.operation == "add": sums[item.stat_id].flat += int(item.value)
		else: sums[item.stat_id].bps += int(item.value)
	var derived: Dictionary = {}
	for id_ in _definitions:
		var d: Dictionary = _definitions[id_]
		# 64*1e9 flats and 64*100000 bps with signed31bit base stay <4.3e17.
		var numerator: int = (int(_base[id_])+int(sums[id_].flat))*maxi(0,10000+int(sums[id_].bps))
		derived[id_] = clampi(floor_ratio(numerator,10000),int(d.minimum_raw),int(d.maximum_raw))
	accepted.sort_custom(func(a: Dictionary,b: Dictionary) -> bool: return JSON.stringify([a.source_id,a.id]) < JSON.stringify([b.source_id,b.id]))
	_modifiers = accepted
	_values = derived
	errors.clear()
	return true

func value(id_: String) -> int:
	return int(_values.get(id_,0))

func snapshot() -> Dictionary:
	return _values.duplicate(true)

func modifiers_snapshot() -> Array:
	return _modifiers.duplicate(true)
