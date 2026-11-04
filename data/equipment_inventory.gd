extends RefCounted
## Pure bounded inventory. Transaction callback commits stats before publishing
## the validated candidate, with no failure points after that callback.
const Rules = preload("res://data/game_catalog.gd")
const MAX_ITEMS := 64
const MAX_UID := 2147483647
const SOURCE_PREFIX := "equipment/"
var catalog: RefCounted
var errors: Array[String] = []
var _items: Array = []
var _equipped: Dictionary = {}
var _next_uid := 1
var _rng := RandomNumberGenerator.new()
var _context := {"actor_tag":"caster","level":1}
var _apply: Callable
var valid := false

func _init(definitions: RefCounted, apply_modifiers: Callable = Callable(), context: Dictionary = {"actor_tag":"caster","level":1}, seed_value: int = 9361) -> void:
	# The supplied catalog must have been validated against the combat catalog.
	# Keep a private frozen copy so later editor replacements cannot change rolls.
	catalog = definitions.frozen_copy()
	_apply = apply_modifiers
	if not context_valid(context) or catalog.snapshot().is_empty():
		errors.assign(["Invalid inventory owner context or definitions"])
		return
	_context = {"actor_tag":context.actor_tag,"level":int(context.level)}
	_rng.seed = seed_value
	valid = true

static func context_valid(value: Variant) -> bool:
	return value is Dictionary and value.size() == 2 and value.has_all(["actor_tag","level"]) and value.actor_tag is String and not value.actor_tag.is_empty() and value.actor_tag.length() <= 64 and Rules.integer(value.level,1,100)

static func state_integer(value: Variant) -> bool:
	if not value is String or value.is_empty() or value.length() > 20 or not value.is_valid_int(): return false
	return str(value.to_int()) == value

func context_snapshot() -> Dictionary:
	return _context.duplicate(true)

func eligible(definition: Dictionary) -> bool:
	return not definition.is_empty() and _context.actor_tag == definition.actor_tag and int(_context.level) >= int(definition.minimum_level)

func items_snapshot() -> Array:
	return _items.duplicate(true)

func equipped_snapshot() -> Dictionary:
	return _equipped.duplicate(true)

func snapshot() -> Dictionary:
	if not valid: return {}
	var definitions: Dictionary = catalog.snapshot()
	return {"schema_version":1,"catalog_id":definitions.catalog_id,"definition_version":int(definitions.definition_version),"catalog_sha256":catalog.content_fingerprint(),"items":items_snapshot(),"equipped":equipped_snapshot(),"next_uid":_next_uid,"rng_state":str(_rng.state)}

func find_item(uid: int, source: Variant = null) -> Dictionary:
	for item in (_items if source == null else source):
		if int(item.uid) == uid: return item.duplicate(true)
	return {}

func create_item(base_id: String) -> Dictionary:
	if _items.size() >= MAX_ITEMS:
		errors.assign(["Inventory full"])
		return {}
	var item := reserve_item(base_id,"crafted")
	if not item.is_empty(): _items.append(item.duplicate(true))
	return item

func reserve_item(base_id: String, quality: String) -> Dictionary:
	# Reservation advances shared UID/roll RNG but does not grant ownership.
	errors.clear()
	var definition: Dictionary = catalog.definition("items",base_id)
	if not valid or definition.is_empty() or not quality in ["common","crafted"] or _next_uid > MAX_UID:
		errors.assign(["Unknown item/quality or UID exhausted"])
		return {}
	var trial := RandomNumberGenerator.new()
	trial.state = _rng.state
	var affixes: Array = []
	if quality == "common": trial.randi()
	if quality == "crafted":
		var affix_id: String = definition.affix_ids[trial.randi_range(0,definition.affix_ids.size()-1)]
		var roll: Dictionary = catalog.definition("affixes",affix_id).modifier
		var value: int = int(roll.minimum)+trial.randi_range(0,(int(roll.maximum)-int(roll.minimum))/int(roll.step))*int(roll.step)
		affixes.append({"id":affix_id,"value":value})
	var item := {"uid":_next_uid,"base_id":base_id,"quality":quality,"affixes":affixes}
	_next_uid += 1
	_rng.state = trial.state
	return item

func acquire_reserved(item: Dictionary) -> bool:
	var proposed := snapshot()
	proposed.items.append(item.duplicate(true))
	errors = validate(proposed)
	if not errors.is_empty(): return false
	# Ownership alone changes no equipped modifier. Do not recompute/clamp current
	# vitals (including explicit synthetic QA overrides) on ground pickup.
	var affixes: Array = []
	for affix in item.affixes: affixes.append({"id":affix.id,"value":int(affix.value)})
	_items.append({"uid":int(item.uid),"base_id":item.base_id,"quality":item.quality,"affixes":affixes})
	return true

func validate(candidate: Variant) -> Array[String]:
	var found: Array[String] = []
	if not valid:
		found.append("Inventory is unavailable")
		return found
	var definitions: Dictionary = catalog.snapshot()
	if not candidate is Dictionary or candidate.size() != 8 or not candidate.has_all(["schema_version","catalog_id","definition_version","catalog_sha256","items","equipped","next_uid","rng_state"]):
		found.append("Invalid inventory document fields")
		return found
	if not Rules.integer(candidate.schema_version,1,1) or candidate.catalog_id != definitions.catalog_id or not Rules.integer(candidate.definition_version,int(definitions.definition_version),int(definitions.definition_version)):
		found.append("Unsupported inventory/catalog version")
	if candidate.catalog_sha256 != catalog.content_fingerprint(): found.append("Equipment definitions changed; migration is unsupported")
	if not candidate.items is Array or candidate.items.size() > MAX_ITEMS or not candidate.equipped is Dictionary or candidate.equipped.size() > 3:
		found.append("Invalid inventory capacity/slots")
		return found
	if not Rules.integer(candidate.next_uid,1,MAX_UID+1) or not state_integer(candidate.rng_state): found.append("Invalid UID counter or exact RNG state")
	var owned := {}
	var largest := 0
	for item in candidate.items:
		if not item is Dictionary or item.size() != 4 or not item.has_all(["uid","base_id","quality","affixes"]) or not Rules.integer(item.get("uid"),1,MAX_UID):
			found.append("Invalid item instance fields")
			continue
		if owned.has(int(item.uid)): found.append("Duplicate item UID")
		owned[int(item.uid)] = item
		largest = maxi(largest,int(item.uid))
		var definition: Dictionary = catalog.definition("items",str(item.base_id))
		if definition.is_empty() or not item.quality in ["common","crafted"] or not item.affixes is Array or item.affixes.size() != (1 if item.quality == "crafted" else 0):
			found.append("Unsupported item definition/quality/affix count")
			continue
		var groups := {}
		for affix in item.affixes:
			if not affix is Dictionary or affix.size() != 2 or not affix.has_all(["id","value"]) or not affix.id in definition.affix_ids:
				found.append("Unknown or ineligible affix")
				continue
			var affix_definition: Dictionary = catalog.definition("affixes",str(affix.id))
			var roll: Dictionary = affix_definition.modifier
			if not affix_definition.required_tag in definition.tags or groups.has(affix_definition.group) or not Rules.integer(affix.value,int(roll.minimum),int(roll.maximum)) or (int(affix.value)-int(roll.minimum))%int(roll.step) != 0: found.append("Invalid affix tag/group/roll")
			groups[affix_definition.group] = true
	if Rules.integer(candidate.next_uid,1,MAX_UID+1) and int(candidate.next_uid) <= largest: found.append("UID counter would reuse an owned identity")
	var used := {}
	for slot in candidate.equipped:
		var uid: Variant = candidate.equipped[slot]
		if not slot in ["focus","body","charm"] or not Rules.integer(uid,1,MAX_UID) or not owned.has(int(uid)) or used.has(int(uid)):
			found.append("Invalid or duplicate equipped reference")
			continue
		used[int(uid)] = true
		var definition: Dictionary = catalog.definition("items",str(owned[int(uid)].base_id))
		if definition.is_empty() or definition.slot != slot or not eligible(definition): found.append("Equipment slot or owner requirements mismatch")
	return found

func _modifiers_for(candidate: Dictionary) -> Array:
	var modifiers: Array = []
	var slots: Array = candidate.equipped.keys()
	slots.sort()
	for slot in slots:
		var item: Dictionary = find_item(int(candidate.equipped[slot]),candidate.items)
		var definition: Dictionary = catalog.definition("items",item.base_id)
		var source: String = SOURCE_PREFIX+str(int(item.uid))
		for modifier in definition.base_modifiers:
			modifiers.append({"source_id":source,"id":"base/"+modifier.id,"stat_id":modifier.stat_id,"operation":modifier.operation,"value":int(modifier.value)})
		for affix in item.affixes:
			var modifier: Dictionary = catalog.definition("affixes",affix.id).modifier
			modifiers.append({"source_id":source,"id":"affix/"+affix.id,"stat_id":modifier.stat_id,"operation":modifier.operation,"value":int(affix.value)})
	return modifiers

func replace_document(candidate: Variant) -> bool:
	errors = validate(candidate)
	if not errors.is_empty(): return false
	var proposed: Dictionary = candidate.duplicate(true)
	var modifiers: Array = _modifiers_for(proposed)
	if _apply.is_valid() and not bool(_apply.call(modifiers)):
		errors.assign(["Combined modifiers rejected; inventory preserved"])
		return false
	_items = []
	for item in proposed.items:
		var affixes: Array = []
		for affix in item.affixes: affixes.append({"id":affix.id,"value":int(affix.value)})
		_items.append({"uid":int(item.uid),"base_id":item.base_id,"quality":item.quality,"affixes":affixes})
	_equipped = {}
	for slot in proposed.equipped: _equipped[slot] = int(proposed.equipped[slot])
	_next_uid = int(proposed.next_uid)
	_rng.state = String(proposed.rng_state).to_int()
	return true

func replace_context(candidate: Variant) -> bool:
	if not valid or not context_valid(candidate):
		errors.assign(["Invalid owner context"])
		return false
	var previous: Dictionary = _context
	_context = {"actor_tag":candidate.actor_tag,"level":int(candidate.level)}
	var issues: Array[String] = validate(snapshot())
	if not issues.is_empty():
		_context = previous
		errors = issues
		return false
	errors.clear()
	return true

func equip(uid: int) -> bool:
	var item: Dictionary = find_item(uid)
	if item.is_empty():
		errors.assign(["Item is not owned"])
		return false
	var proposed: Dictionary = snapshot()
	var definition: Dictionary = catalog.definition("items",item.base_id)
	proposed.equipped[definition.slot] = uid
	return replace_document(proposed)

func unequip(slot: String) -> bool:
	if not valid or not slot in ["focus","body","charm"]:
		errors.assign(["Unknown equipment slot"])
		return false
	var proposed: Dictionary = snapshot()
	proposed.equipped.erase(slot)
	return replace_document(proposed)
