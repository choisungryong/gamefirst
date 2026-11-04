extends SceneTree
## Independent old-field comparison against pinned phase3 source, not new-code
## generated expected values. Extra phase4 metadata keys are checked separately.
const Sim = preload("res://baseline_sim.gd")
const FIXTURE := "res://tests/fixtures/phase4-phase3-legacy-bitwise.json"
const FIXTURE_SHA := "b0bc934896a560b3886e514129d39de261bde72ae8d9ebea9be5d286561d6213"
const SOURCE_SHA := "2169fcdf514552026251a0d88dde1728ef7750fb1c93e59ece1971de0e672753"
const CATALOG_SHA := "dbf793a87b339d29db3012476dfe7afe7b24782a73f87e5ca517b3aedfeb6a26"
var checks := 0
var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		printerr("PHASE4 LEGACY FAILED: "+message)

func canonical(value: Variant) -> Variant:
	if value is Vector2: return [canonical(value.x),canonical(value.y)]
	if value is float: return {"__godot_float64_bytes":var_to_bytes(value).hex_encode()}
	if value is Dictionary:
		var result: Dictionary = {}
		var keys_: Array = value.keys()
		keys_.sort()
		for key_ in keys_: result[key_] = canonical(value[key_])
		return result
	if value is Array:
		var result: Array = []
		for entry in value: result.append(canonical(entry))
		return result
	return value

func snapshot(s: RefCounted, trace: Array) -> Dictionary:
	var entities: Array = []
	var ids: Array = s.enemies.keys()
	ids.sort()
	for identity in ids: entities.append(s.enemies[identity])
	return canonical({"tick":s.tick,"player":s.player,"move_target":s.move_target,
		"life":s.life,"mana_raw":s.mana_raw,"mana_max_raw":s.mana_max_raw,
		"mana_cost_raw":s.mana_cost_raw,"damage_min_raw":s.damage_min_raw,
		"damage_max_raw":s.damage_max_raw,"startup_ticks":s.startup_ticks,
		"cycle_ticks":s.cycle_ticks,"bolt_speed":s.bolt_speed,
		"enemies":entities,"bolts":s.bolts,"pending":s.pending,
		"shots":s.shots,"hits":s.hits,"kills":s.kills,
		"rng_state":str(s.rng.state),"events":trace})

## Compare every legacy key/array item, permitting only additional Dictionary
## keys. Added events, changed lengths/order, numbers and missing keys fail.
func first_difference(expected: Variant, actual: Variant, path: String) -> String:
	if expected is Dictionary:
		if not actual is Dictionary: return path+" expected Dictionary"
		for key_ in expected:
			if not actual.has(key_): return path+" missing "+str(key_)
			var difference: String = first_difference(expected[key_],actual[key_],path+"."+str(key_))
			if difference != "": return difference
		return ""
	if expected is Array:
		if not actual is Array: return path+" expected Array"
		if expected.size() != actual.size(): return path+" array length %d != %d" % [expected.size(),actual.size()]
		for index in range(expected.size()):
			var difference: String = first_difference(expected[index],actual[index],path+"["+str(index)+"]")
			if difference != "": return difference
		return ""
	if expected != actual: return path+" expected="+str(expected)+" actual="+str(actual)
	return ""

func run() -> void:
	check(FileAccess.get_sha256(FIXTURE) == FIXTURE_SHA,"immutable phase3 fixture hash")
	var fixture: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(FIXTURE))
	check(fixture.source_sha256 == SOURCE_SHA and fixture.catalog_sha256 == CATALOG_SHA,"fixture source/catalog pins are accepted phase3")
	check(fixture.engine == Engine.get_version_info().string,"same engine for legacy comparison")
	check(fixture.cases.size() == 7,"all seven original cases retained")
	for expected in fixture.cases:
		var definition: Dictionary = expected.input
		var s = Sim.new()
		s.reset(int(definition.count))
		s.enemy_ai = definition.ai
		if definition.high_health:
			s.life = 1000000.0
			s.mana_raw = 100000000
		if definition.has("initial_mana"): s.mana_raw = int(definition.initial_mana)
		var trace: Array = []
		var checkpoint := 0
		for frame in range(int(definition.frames)):
			if definition.move_policy == "orbit120" and frame % 120 == 0:
				s.set_destination(Vector2(cos(frame*.01),sin(frame*.01))*7)
			var target: Dictionary = s.nearest_enemy(s.player)
			var aim: Vector2 = target.get("p",s.player+Vector2.RIGHT)
			var held: bool = definition.cast_policy == "held" or frame % 90 < 75
			s.step(held and not target.is_empty(),aim)
			trace.append_array(s.events.duplicate(true))
			if frame % 60 == 59:
				var difference: String = first_difference(expected.checkpoints[checkpoint].state,snapshot(s,trace),definition.name+"@"+str(frame+1))
				check(difference == "",difference if difference != "" else definition.name+"@"+str(frame+1))
				checkpoint += 1
				trace.clear()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional legacy harness failure proof")
	print(JSON.stringify({"scope":"phase4 legacy no-modifier FireBolt old-field/event/RNG comparison; not original D2R equivalence","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
