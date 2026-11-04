extends SceneTree
## Independent oracle and invalid-input tests for this project's declared rules.
## Python Fraction fixture never imports the product implementation.
const Stats = preload("res://combat/stat_block.gd")
const Resolver = preload("res://combat/combat_resolver.gd")
const FIXTURE := "res://tests/fixtures/phase4-math-oracle.json"
const FIXTURE_SHA := "56e84a015473786277ea51ab6093ef805a3e7d04575da5eb8ffad4ccc495539d"
var checks := 0
var failures: Array[String] = []

func _initialize() -> void: call_deferred("run")

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		printerr("PHASE4 MATH FAILED: "+message)

func definition(id_: String = "test", minimum: int = -2147483647, maximum: int = 2147483647, initial: int = 1001) -> Dictionary:
	return {"id":id_,"unit":"health","scale":256,"minimum_raw":minimum,"maximum_raw":maximum,"default_raw":initial}

func modifier(id_: String, operation: String, value: Variant, stat_id: Variant = "test", source: Variant = "item") -> Dictionary:
	return {"source_id":source,"id":id_,"stat_id":stat_id,"operation":operation,"value":value}

func integer_json(value: Variant) -> Variant:
	# Godot JSON parses JSON numbers as float. Fixture numbers are exact integers
	# below 2^53; converting only the expected side restores the declared schema.
	if value is float:
		assert(is_finite(value) and value == floor(value) and absf(value) < 9007199254740992.0)
		return int(value)
	if value is Dictionary:
		var result: Dictionary = {}
		for key_ in value: result[key_] = integer_json(value[key_])
		return result
	if value is Array:
		var result: Array = []
		for item in value: result.append(integer_json(item))
		return result
	return value

func math_oracle() -> void:
	check(FileAccess.get_sha256(FIXTURE) == FIXTURE_SHA,"immutable exact Fraction oracle hash")
	var fixture: Dictionary = integer_json(JSON.parse_string(FileAccess.get_file_as_string(FIXTURE)))
	for index in range(fixture.damage.size()):
		var row: Dictionary = fixture.damage[index]
		var a: Array = row.input
		check(Resolver.damage(int(a[0]),int(a[1]),int(a[2]),int(a[3]),int(a[4]),int(a[5])) == row.expected,"damage exact stages "+str(index))
	for index in range(fixture.cost.size()):
		var row: Dictionary = fixture.cost[index]
		check(Resolver.cost(int(row.input[0]),int(row.input[1])) == int(row.expected),"cost exact rounding "+str(index))
	for index in range(fixture.timing.size()):
		var row: Dictionary = fixture.timing[index]
		check(Resolver.timing(int(row.input[0]),int(row.input[1]),int(row.input[2])) == row.expected,"timing exact ceil "+str(index))
	check(Resolver.damage(1,256).hp_after_raw == 255 and not Resolver.damage(1,256).dead,"raw255 remains alive in default independent policy")
	check(Resolver.damage(1,256,0,0,0,255).dead,"explicit threshold policy distinguished from default")
	check(Resolver.damage(1001,10000,0,2500).total_raw == 750,"resistance before display truncation")
	check(Resolver.cost(640,-9000) == 64,"cost minimum factor ten percent")
	check(Resolver.pay_cost(639,640) == {"accepted":false,"mana_before_raw":639,"cost_raw":640,"mana_after_raw":639},"shortage atomic unchanged mana")
	check(Resolver.pay_cost(640,640).accepted and Resolver.pay_cost(640,640).mana_after_raw == 0,"exact cost accepted")
	for bad_cost in [0,-1,-9223372036854775807]:
		check(not Resolver.pay_cost(640,bad_cost).accepted and Resolver.pay_cost(640,bad_cost).mana_after_raw == 640,"nonpositive payment rejected "+str(bad_cost))
	for bad_mana in [-1,2147483648,9223372036854775807]:
		check(not Resolver.pay_cost(bad_mana,1).accepted and Resolver.pay_cost(bad_mana,1).mana_after_raw == bad_mana,"out-of-contract payment rejected atomically "+str(bad_mana))
	check(Resolver.damage(9223372036854775807,2147483647,0,-10000,100000).total_raw == 47244640234,"raw saturation prevents int64 product overflow")
	check(Resolver.cost(9223372036854775807,100000) == 23622320117,"cost raw saturation prevents overflow")
	check(Resolver.timing(9223372036854775807,9223372036854775807,-7500) == {"startup_ticks":8589934588,"cycle_ticks":8589934589},"timing saturation prevents overflow")

func stat_contract() -> void:
	check(Stats.floor_ratio(-9223372036854775807-1,10000) == -922337203685478,"floor helper supports exact int64 minimum without negate overflow")
	check(Stats.floor_ratio(-9223372036854775807-1,1) == -9223372036854775807-1,"floor helper minimum quotient divisor one")
	var s = Stats.new([definition()])
	check(s.valid and s.value("test") == 1001,"valid signed stat default")
	var mods: Array = [modifier("flat","add",1),modifier("pct","percent_bps",3333)]
	check(s.replace_modifiers(mods) and s.value("test") == 1335,"aggregate add then percent one floor")
	var forward: Dictionary = s.snapshot()
	mods.reverse()
	check(s.replace_modifiers(mods) and s.snapshot() == forward,"modifier order independence")
	var copy: Dictionary = s.snapshot()
	copy.test = 0
	var mod_copy: Array = s.modifiers_snapshot()
	mod_copy[0].value = 777
	check(s.snapshot() == forward and s.modifiers_snapshot()[0].value != 777,"stat/modifier snapshots deeply isolated")
	mods[0].value = 999
	check(s.snapshot() == forward,"caller modifier mutation does not alias state")
	var bad_candidates: Array = [null,{},1,true,[null],[1],[{}],
		[modifier("a","multiply",3)],[modifier("a","add",true)],
		[modifier("a","add",1.5)],[modifier("a","add",NAN)],
		[modifier("a","add",INF)],[modifier("a","add",1000000001)],
		[modifier("a","add",-1000000001)],[modifier("a","percent_bps",100001)],
		[modifier("a","percent_bps",-10001)],[modifier("a","add",1,"missing")],
		[modifier("a","add",1,"test","")],[modifier("","add",1)],
		[modifier("a","add",1,"test",123)],[modifier("a","add",1,"test","x".repeat(129))],
		[modifier("same","add",1),modifier("same","percent_bps",1)]]
	var extra: Dictionary = modifier("extra","add",1)
	extra.unrecognized = 1
	bad_candidates.append([extra])
	var oversized: Array = []
	for i in range(65): oversized.append(modifier(str(i),"add",1))
	bad_candidates.append(oversized)
	for index in range(bad_candidates.size()):
		var before: Dictionary = s.snapshot()
		var before_mods: Array = s.modifiers_snapshot()
		check(not s.replace_modifiers(bad_candidates[index]) and s.snapshot() == before and s.modifiers_snapshot() == before_mods and not s.errors.is_empty(),"invalid replacement atomic "+str(index))
	check(s.replace_modifiers([modifier("same","add",1,"test","a"),modifier("same","add",1,"test","b")]) and s.value("test") == 1003,"identity is source/id pair")
	check(s.replace_modifiers([modifier("b:c","add",1,"test","a"),modifier("c","add",1,"test","a:b")]) and s.value("test") == 1003,"pair identity separator ambiguity avoided")
	check(s.replace_modifiers([modifier("minus","add",-1002),modifier("pct","percent_bps",3333)]) and s.value("test") == -2,"negative exact floor toward minus infinity")
	check(s.replace_modifiers([modifier("a","percent_bps",-10000),modifier("b","percent_bps",-10000)]) and s.value("test") == 0,"aggregate factor lower bounded zero")
	var upper = Stats.new([definition("test",-2147483647,2147483647,2147483647)])
	var extremes: Array = []
	for i in range(32): extremes.append(modifier("f"+str(i),"add",1000000000))
	for i in range(32): extremes.append(modifier("p"+str(i),"percent_bps",100000))
	check(upper.replace_modifiers(extremes) and upper.value("test") == 2147483647,"maximum supported intermediate safely clamps upper")
	for i in range(32): extremes[i].value = -1000000000
	check(upper.replace_modifiers(extremes) and upper.value("test") == -2147483647,"minimum supported intermediate safely clamps lower")
	check(s.replace_modifiers([]) and s.errors.is_empty() and s.value("test") == 1001,"valid replacement clears errors and restores base")
	var invalid_definitions: Array = [[],[definition(),definition()], [null],
		[{"id":"bad","unit":"health","scale":1}],
		[{"id":"bad","unit":"damage","scale":256}],
		[definition("test",20,10,15)], [definition("test",0,100,101)],
		[definition("test",-2147483647,2147483648,1)]]
	# Empty definitions are a valid empty block; no implicit game stats appear.
	check(Stats.new([]).valid and Stats.new([]).snapshot().is_empty(),"explicit empty definitions stay empty")
	for i in range(1,invalid_definitions.size()): check(not Stats.new(invalid_definitions[i]).valid,"invalid definitions rejected "+str(i))
	for invalid_base in [{"missing":1},{"test":true},{"test":1.25},{"test":INF},{"test":2147483648}]:
		check(not Stats.new([definition()],invalid_base).valid,"invalid base rejected "+str(invalid_base))
	var defs: Array = [definition()]
	var independent = Stats.new(defs)
	defs[0].default_raw = 7
	check(independent.value("test") == 1001,"definition snapshot isolation")

func run() -> void:
	math_oracle()
	stat_contract()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional math harness failure proof")
	print(JSON.stringify({"scope":"Independent project arithmetic and modifier contracts; no D2R equivalence claim","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
