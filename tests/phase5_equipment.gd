extends SceneTree
## Independent bounded-definition/inventory cases. Expected ranges, roll grid,
## UID and requirements are hand specified; no product helper supplies an oracle.
const Catalog = preload("res://data/equipment_catalog.gd")
const Inventory = preload("res://data/equipment_inventory.gd")
var checks := 0
var failures: Array[String] = []

func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("PHASE5 EQUIPMENT FAILED: "+message)

func definitions() -> Array:
	return [{"id":"stat.health"},{"id":"stat.mana"},{"id":"stat.skill.ember_level"},{"id":"stat.spell_power"},{"id":"stat.resist.physical"},{"id":"stat.cast_speed"}]

func catalog() -> RefCounted:
	var c = Catalog.new(definitions())
	check(c.load_file(),"independent equipment definitions load")
	return c

func reject_catalog(c: RefCounted, candidate: Variant, name_: String) -> void:
	var before: Dictionary = c.snapshot()
	check(not c.replace_document(candidate),"catalog rejects "+name_)
	check(c.snapshot() == before,"catalog atomic after "+name_)

func catalog_cases() -> void:
	var c = catalog()
	var original: Dictionary = c.snapshot()
	check(original.items.size() == 3 and original.affixes.size() == 3,"narrow three bases and three affixes")
	var detached: Dictionary = c.definition("items","item.ember_focus")
	detached.base_modifiers[0].value = 999
	check(c.definition("items","item.ember_focus").base_modifiers[0].value == 1,"definition nested modifier is detached")
	var copy: Dictionary = c.snapshot()
	copy.items[0].tags.append("changed")
	check(not "changed" in c.snapshot().items[0].tags,"catalog snapshot nested tags detached")
	for value in [null,[],1,"wrong",{}]: reject_catalog(c,value,"non-document "+str(value))
	for value in [true,0,2,1.5]:
		copy = original.duplicate(true)
		copy.schema_version = value
		reject_catalog(c,copy,"schema "+str(value))
	copy = original.duplicate(true)
	copy.catalog_id = "foreign.catalog"
	reject_catalog(c,copy,"catalog ID prefix")
	copy = original.duplicate(true)
	copy.items.append(copy.items[0].duplicate(true))
	reject_catalog(c,copy,"duplicate base ID")
	copy = original.duplicate(true)
	copy.affixes.append(copy.affixes[0].duplicate(true))
	reject_catalog(c,copy,"duplicate affix ID")
	for field in ["slot","actor_tag","minimum_level","tags","affix_ids","base_modifiers"]:
		copy = original.duplicate(true)
		copy.items[0].erase(field)
		reject_catalog(c,copy,"missing item "+field)
	for value in ["unknown",null,[]]:
		copy = original.duplicate(true)
		copy.items[0].slot = value
		reject_catalog(c,copy,"unsupported slot "+str(value))
	for value in [0,101,1.5,true]:
		copy = original.duplicate(true)
		copy.items[0].minimum_level = value
		reject_catalog(c,copy,"invalid required level "+str(value))
	for value in [[],["focus","focus"],[1],"focus"]:
		copy = original.duplicate(true)
		copy.items[0].tags = value
		reject_catalog(c,copy,"invalid tags "+str(value))
	copy = original.duplicate(true)
	copy.items[0].affix_ids = ["affix.missing"]
	reject_catalog(c,copy,"unresolved affix")
	copy = original.duplicate(true)
	copy.items[0].affix_ids = ["affix.shelter"]
	reject_catalog(c,copy,"base tag ineligible affix")
	copy = original.duplicate(true)
	copy.items[0].base_modifiers.append(copy.items[0].base_modifiers[0].duplicate(true))
	reject_catalog(c,copy,"duplicate base modifier ID")
	var bad_modifiers: Array = [
		{"stat_id":"stat.missing","operation":"add","minimum":0,"maximum":100,"step":1},
		{"stat_id":"stat.spell_power","operation":"multiply","minimum":0,"maximum":100,"step":1},
		{"stat_id":"stat.spell_power","operation":"add","minimum":2,"maximum":1,"step":1},
		{"stat_id":"stat.spell_power","operation":"add","minimum":0,"maximum":10,"step":3},
		{"stat_id":"stat.spell_power","operation":"add","minimum":0,"maximum":10,"step":0},
		{"stat_id":"stat.spell_power","operation":"add","minimum":0.5,"maximum":10,"step":1},
		{"stat_id":"stat.spell_power","operation":"add","minimum":0,"maximum":1000000001,"step":1},
		{"stat_id":"stat.spell_power","operation":"percent_bps","minimum":-10001,"maximum":0,"step":1},
		{"stat_id":"stat.spell_power","operation":"add","minimum":true,"maximum":10,"step":1},
	]
	for index in range(bad_modifiers.size()):
		copy = original.duplicate(true)
		copy.affixes[0].modifier = bad_modifiers[index]
		reject_catalog(c,copy,"roll modifier case "+str(index))
	var before: Dictionary = c.snapshot()
	check(not c.load_text("{broken") and c.snapshot() == before,"invalid JSON preserves definitions")

func reject_inventory(inv: RefCounted, candidate: Variant, name_: String) -> void:
	var before: Dictionary = inv.snapshot()
	check(not inv.replace_document(candidate),"inventory rejects "+name_)
	check(inv.snapshot() == before,"inventory and RNG atomic after "+name_)

func reversed_object_keys(value: Variant) -> Variant:
	if value is Dictionary:
		var result: Dictionary = {}
		var keys_: Array = value.keys()
		keys_.reverse()
		for key_ in keys_: result[key_] = reversed_object_keys(value[key_])
		return result
	if value is Array:
		var result: Array = []
		for entry in value: result.append(reversed_object_keys(entry))
		return result
	return value

func inventory_cases() -> void:
	var c = catalog()
	var inv = Inventory.new(c)
	var a: Dictionary = inv.create_item("item.ember_focus")
	var b: Dictionary = inv.create_item("item.ember_focus")
	check(a.uid == 1 and b.uid == 2 and a.base_id == b.base_id,"same base has separate monotonic instance IDs")
	check(a.affixes[0].id == "affix.kindling" and a.affixes[0].value >= 500 and a.affixes[0].value <= 1000 and int(a.affixes[0].value)%100 == 0,"roll lies on independently specified 500..1000 step100 grid")
	var b_before: Dictionary = b.duplicate(true)
	a.affixes[0].value = -123
	check(inv.find_item(2) == b_before and inv.find_item(1).affixes[0].value != -123,"returned item mutation cannot modify either owned instance")
	var exposed: Array = inv.items_snapshot()
	exposed[0].affixes[0].value = -123
	check(inv.find_item(1).affixes[0].value != -123,"item list deep copy")
	var replay = Inventory.new(c)
	var first: Dictionary = replay.create_item("item.ember_focus")
	check(first == inv.find_item(1),"dedicated item seed replay yields same first instance")
	var next_expected: Dictionary = replay.create_item("item.ember_focus")
	check(next_expected == inv.find_item(2),"dedicated stream continues deterministically")
	check(inv.equip(1) and inv.equipped_snapshot() == {"focus":1},"equip owned correct-slot focus")
	var equipped: Dictionary = inv.equipped_snapshot()
	equipped.focus = 2
	check(inv.equipped_snapshot().focus == 1,"equipped getter detached")
	check(inv.equip(2) and inv.equipped_snapshot() == {"focus":2},"same-slot replacement has one reference")
	check(inv.unequip("focus") and inv.equipped_snapshot().is_empty(),"unequip removes only equipment reference")
	var charm: Dictionary = inv.create_item("item.well_charm")
	var before: Dictionary = inv.snapshot()
	check(not inv.equip(int(charm.uid)) and inv.snapshot() == before,"base level1 cannot equip level2 charm")
	check(not inv.equip(99999) and inv.snapshot() == before,"unowned UID rejected atomically")
	check(not inv.unequip("head") and inv.snapshot() == before,"unsupported slot rejected atomically")
	check(inv.create_item("item.missing").is_empty() and inv.snapshot() == before,"unknown creation consumes neither UID nor RNG")
	var c2 = catalog()
	var doc: Dictionary = c2.snapshot()
	doc.items[0].minimum_level = 2
	doc.items[0].base_modifiers.append({"id":"self-level","stat_id":"stat.skill.ember_level","operation":"add","value":20})
	check(c2.replace_document(doc),"self-bonus fixture definition accepted")
	var owner1 = Inventory.new(c2)
	var blocked: Dictionary = owner1.create_item("item.ember_focus")
	check(not owner1.equip(int(blocked.uid)),"equipment bonus cannot satisfy owner base level requirement")
	var owner2 = Inventory.new(c,Callable(),{"actor_tag":"caster","level":2})
	var allowed: Dictionary = owner2.create_item("item.well_charm")
	check(owner2.equip(int(allowed.uid)),"explicit eligible owner2 can equip level2 charm")
	var wrong_owner = Inventory.new(c,Callable(),{"actor_tag":"warrior","level":100})
	var wrong: Dictionary = wrong_owner.create_item("item.ember_focus")
	check(not wrong_owner.equip(int(wrong.uid)),"owner tag restriction independent of level")

	var valid: Dictionary = inv.snapshot()
	for value in [null,[],{},1]: reject_inventory(inv,value,"not a complete document "+str(value))
	for field in valid:
		var missing: Dictionary = valid.duplicate(true)
		missing.erase(field)
		reject_inventory(inv,missing,"missing "+str(field))
	var copy: Dictionary = valid.duplicate(true)
	copy["modifiers"] = [{"stat_id":"stat.spell_power","value":100000}]
	reject_inventory(inv,copy,"arbitrary serialized modifier injection")
	for value in [true,0,2,1.5]:
		copy = valid.duplicate(true)
		copy.schema_version = value
		reject_inventory(inv,copy,"schema "+str(value))
	copy = valid.duplicate(true)
	copy.catalog_id = "equipment.foreign"
	reject_inventory(inv,copy,"foreign catalog ID")
	copy = valid.duplicate(true)
	copy.definition_version += 1
	reject_inventory(inv,copy,"different definition version")
	copy = valid.duplicate(true)
	copy.items.append(copy.items[0].duplicate(true))
	reject_inventory(inv,copy,"duplicate owned UID")
	for value in [0,-1,true,1.5,2147483648]:
		copy = valid.duplicate(true)
		copy.items[0].uid = value
		reject_inventory(inv,copy,"unsupported UID "+str(value))
	for value in [1,0,2147483649,true,1.5]:
		copy = valid.duplicate(true)
		copy.next_uid = value
		reject_inventory(inv,copy,"counter reuse or invalid counter "+str(value))
	copy = valid.duplicate(true)
	copy.items[0].base_id = "item.missing"
	reject_inventory(inv,copy,"missing base definition")
	copy = valid.duplicate(true)
	copy.items[0].quality = "unique"
	reject_inventory(inv,copy,"unsupported quality")
	for value in [499,1001,550,true,500.5]:
		copy = valid.duplicate(true)
		copy.items[0].affixes[0].value = value
		reject_inventory(inv,copy,"range/grid/type roll "+str(value))
	copy = valid.duplicate(true)
	copy.items[0].affixes[0].id = "affix.shelter"
	reject_inventory(inv,copy,"foreign tagged affix")
	copy = valid.duplicate(true)
	copy.items[0].affixes.append(copy.items[0].affixes[0].duplicate(true))
	reject_inventory(inv,copy,"multiple or repeated affix group")
	copy = valid.duplicate(true)
	copy.items[0].affixes.clear()
	reject_inventory(inv,copy,"crafted instance cannot remove its committed affix")
	for value in [{"focus":99999},{"body":1},{"focus":1,"body":1},{"head":1},{"focus":true},{"charm":3}]:
		copy = valid.duplicate(true)
		copy.equipped = value
		reject_inventory(inv,copy,"slot/reference/requirement "+str(value))
	for value in [1,"", "+1","01","-0"," 1","1 ","1e3","NaN","9223372036854775808","-9223372036854775809"]:
		copy = valid.duplicate(true)
		copy.rng_state = value
		reject_inventory(inv,copy,"RNG exact canonical string "+str(value))
	for value in ["0","-1","9223372036854775807","-9223372036854775808"]:
		copy = valid.duplicate(true)
		copy.rng_state = value
		check(inv.replace_document(copy) and inv.snapshot().rng_state == value,"signed64 RNG state exact roundtrip "+value)

	var full = Inventory.new(c)
	for i in range(64): check(not full.create_item("item.ember_focus").is_empty(),"bounded inventory creates slot "+str(i))
	before = full.snapshot()
	check(full.create_item("item.ember_focus").is_empty() and full.snapshot() == before,"65th item fails without UID/RNG consumption")
	var exhausted = Inventory.new(c)
	copy = exhausted.snapshot()
	copy.next_uid = 2147483647
	check(exhausted.replace_document(copy),"last UID test candidate valid")
	var last: Dictionary = exhausted.create_item("item.ember_focus")
	check(last.uid == 2147483647 and exhausted.snapshot().next_uid == 2147483648,"last supported identity allocated then exhausted sentinel")
	before = exhausted.snapshot()
	check(exhausted.create_item("item.ember_focus").is_empty() and exhausted.snapshot() == before,"exhausted identity never wraps and consumes no RNG")
	var seen_callback := {"called":0,"modifiers":[]}
	var transactional = Inventory.new(c,func(modifiers: Array) -> bool:
		seen_callback.called += 1
		seen_callback.modifiers = modifiers.duplicate(true)
		return false)
	var owned: Dictionary = transactional.create_item("item.ember_focus")
	before = transactional.snapshot()
	check(not transactional.equip(int(owned.uid)) and transactional.snapshot() == before and seen_callback.called == 1,"failed downstream stat commit cannot publish equipment")
	check(seen_callback.modifiers.size() == 2 and seen_callback.modifiers[0].source_id == "equipment/1" and seen_callback.modifiers[0].value == 1,"callback receives definition and stored-roll derived namespaced effects")
	frozen_and_context_cases()

func frozen_and_context_cases() -> void:
	var c = catalog()
	var key_order = Catalog.new(reversed_object_keys(definitions()))
	check(key_order.replace_document(reversed_object_keys(c.snapshot())) and key_order.content_fingerprint() == c.content_fingerprint(),"object key order does not change strict content fingerprint")
	var array_order = Catalog.new(definitions())
	var reversed_arrays: Dictionary = c.snapshot()
	reversed_arrays.items.reverse()
	check(array_order.replace_document(reversed_arrays) and array_order.content_fingerprint() != c.content_fingerprint(),"definition array order remains fingerprint sensitive")
	var inv = Inventory.new(c)
	inv.create_item("item.ember_focus")
	var original: Dictionary = inv.snapshot()
	var copy: Dictionary = c.snapshot()
	copy.items[0].base_modifiers[0].value = 2
	check(c.replace_document(copy),"editor-side catalog can replace valid definition")
	check(inv.snapshot() == original and inv.catalog.definition("items","item.ember_focus").base_modifiers[0].value == 1,"existing inventory pins a private definition copy")
	check(not inv.catalog.replace_document(copy) and inv.snapshot() == original,"runtime catalog refuses definition replacement")
	var changed = Inventory.new(c)
	check(changed.valid and not changed.replace_document(original),"same ID/version with different base effects rejects old save fingerprint")
	var c_rules = Catalog.new(definitions(),"different-combat-rules")
	check(c_rules.load_file(),"changed combat rules fixture loads")
	var different_rules = Inventory.new(c_rules)
	check(not different_rules.replace_document(original),"changed combat rule fingerprint rejects save")
	var altered_stats: Array = definitions()
	altered_stats[0]["test_validated_bound"] = 123
	var c_stats = Catalog.new(altered_stats)
	check(c_stats.load_file(),"changed stat definition fixture loads")
	var different_stats = Inventory.new(c_stats)
	check(not different_stats.replace_document(original),"changed stat definitions reject save despite equal item catalog")
	var counterfeit: Dictionary = original.duplicate(true)
	counterfeit.catalog_sha256 = "0".repeat(64)
	reject_inventory(inv,counterfeit,"forged definition fingerprint")
	for value in [{},{"actor_tag":"caster"},{"actor_tag":"caster","level":true},{"actor_tag":"caster","level":1.5},{"actor_tag":"caster","level":0},{"actor_tag":"caster","level":101},{"actor_tag":1,"level":1},{"actor_tag":"caster","level":1,"extra":1}]:
		var invalid = Inventory.new(c,Callable(),value)
		check(not invalid.valid and invalid.snapshot().is_empty() and invalid.create_item("item.ember_focus").is_empty(),"invalid owner constructor fail closed "+str(value))
		check(not invalid.unequip("focus") and invalid.snapshot().is_empty(),"invalid owner unequip fails without runtime access "+str(value))
		var prior: Dictionary = inv.context_snapshot()
		check(not inv.replace_context(value) and inv.context_snapshot() == prior and inv.snapshot() == original,"invalid context replacement atomic "+str(value))
	check(inv.replace_context({"actor_tag":"caster","level":2}),"valid explicit context promotion")
	var charm: Dictionary = inv.create_item("item.well_charm")
	check(inv.equip(int(charm.uid)),"valid promoted owner equips charm")
	var before: Dictionary = inv.snapshot()
	check(not inv.replace_context({"actor_tag":"caster","level":1}) and inv.context_snapshot().level == 2 and inv.snapshot() == before,"context cannot invalidate already equipped item")
	check(inv.unequip("charm") and inv.replace_context({"actor_tag":"caster","level":1}),"removing requirement item permits context reduction")

func run() -> void:
	catalog_cases()
	inventory_cases()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional equipment harness failure proof")
	print(JSON.stringify({"scope":"Independent equipment/catalog/inventory contracts; no D2R roll equivalence", "checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
