extends SceneTree
## New definition/count/curve cases with explicit expected raw formula.
const Catalog = preload("res://data/game_catalog.gd")
const Sim = preload("res://baseline_sim.gd")
var checks := 0
var failures: Array[String] = []

func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("PHASE5 SKILL CATALOG FAILED: "+message)

func stat(document: Dictionary, id_: String) -> Dictionary:
	for entry in document.stats:
		if entry.id == id_: return entry
	return {}

func reject(c: RefCounted, candidate: Dictionary, message: String) -> void:
	var before: Dictionary = c.snapshot()
	check(not c.replace_document(candidate) and not c.errors.is_empty(),"reject "+message)
	check(c.snapshot() == before,"atomic definition after "+message)

func run() -> void:
	var c = Catalog.new()
	check(c.load_file(),"current independent combat catalog loads")
	var original: Dictionary = c.snapshot()
	check(original.schema_version == 1 and original.definition_version == 3 and original.stats.size() == 11 and original.skills.size() == 3,"explicit schema1 definition3 eleven stats/three skills")
	var level: Dictionary = stat(original,"stat.skill.ember_level")
	check(level.unit == "count" and level.scale == 1 and level.minimum_raw == 0 and level.maximum_raw == 20 and level.default_raw == 0,"count is independent integral bonus unit with0..20 bounds")
	var explicit_curve: Dictionary = original.skills[0].bonus_curve
	check(explicit_curve.size() == 3 and explicit_curve.stat_id == "stat.skill.ember_level" and explicit_curve.min_per_bonus_raw == 256 and explicit_curve.max_per_bonus_raw == 512,"explicit independent bonus slope values")
	for pair in [["unit","health"],["scale",256],["minimum_raw",-1],["minimum_raw",1],["maximum_raw",21],["maximum_raw",19],["default_raw",1],["default_raw",true]]:
		var candidate: Dictionary = original.duplicate(true)
		stat(candidate,"stat.skill.ember_level")[pair[0]] = pair[1]
		reject(c,candidate,"bonus semantic "+str(pair))
	var missing: Dictionary = original.duplicate(true)
	for index in range(missing.stats.size()):
		if missing.stats[index].id == "stat.skill.ember_level":
			missing.stats.remove_at(index)
			break
	reject(c,missing,"definition3 missing required bonus stat")
	var curves: Array = [null,[],{},
		{"stat_id":"stat.mana","min_per_bonus_raw":256,"max_per_bonus_raw":512},
		{"stat_id":"stat.missing","min_per_bonus_raw":256,"max_per_bonus_raw":512},
		{"stat_id":"stat.skill.ember_level","min_per_bonus_raw":-1,"max_per_bonus_raw":512},
		{"stat_id":"stat.skill.ember_level","min_per_bonus_raw":1.5,"max_per_bonus_raw":512},
		{"stat_id":"stat.skill.ember_level","min_per_bonus_raw":true,"max_per_bonus_raw":512},
		{"stat_id":"stat.skill.ember_level","min_per_bonus_raw":513,"max_per_bonus_raw":512},
		{"stat_id":"stat.skill.ember_level","min_per_bonus_raw":256,"max_per_bonus_raw":1000001},
		{"stat_id":"stat.skill.ember_level","min_per_bonus_raw":256,"max_per_bonus_raw":512,"injected":"code"}]
	for index in range(curves.size()):
		var candidate: Dictionary = original.duplicate(true)
		candidate.skills[0].bonus_curve = curves[index]
		reject(c,candidate,"unsupported bonus curve "+str(index))
	var s = Sim.new()
	s.reset(0)
	for bonus in range(21):
		check(s.replace_player_modifiers([{"source_id":"independent-test","id":"bonus","stat_id":"stat.skill.ember_level","operation":"add","value":bonus}]),"supported bonus input "+str(bonus))
		var display: Dictionary = s.skill_display("skill.ember_bolt")
		check(display.bonus_level == bonus and display.effective_level == bonus+1 and display.damage_min_raw == 768+256*bonus and display.damage_max_raw == 1536+512*bonus and display.cost_raw == 640 and display.startup_ticks == 18 and display.cycle_ticks == 33,"exact independent raw curve, unchanged cost/timing at bonus "+str(bonus))
	check(s.replace_player_modifiers([{"source_id":"independent-test","id":"negative","stat_id":"stat.skill.ember_level","operation":"add","value":-1}]) and s.skill_display().effective_level == 1,"negative stat addition clamps bonus0")
	check(s.replace_player_modifiers([{"source_id":"independent-test","id":"large","stat_id":"stat.skill.ember_level","operation":"add","value":1000}]) and s.skill_display().effective_level == 21,"large addition clamps bonus20 and reports effective21")
	var frozen: String = "res://evidence/phase4/builds/phase4-candidate-20261029-02/source/game_data/catalog.json"
	var old = Catalog.new()
	check(old.load_file(frozen) and old.snapshot().definition_version == 2 and old.snapshot().stats.size() == 10,"unchanged accepted definition2 remains supported")
	var old_sim = Sim.new(old)
	check(old_sim.valid_profile and not old_sim.equipment_valid and old_sim.skill_display().damage_min_raw == 768,"old definition2 combat keeps original raw values without equipment")
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional skill catalog harness failure proof")
	print(JSON.stringify({"scope":"Independent count/curve/definition3 contracts, not D2R level formula", "checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
