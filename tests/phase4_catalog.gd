extends SceneTree
const Catalog = preload("res://data/game_catalog.gd")
const Sim = preload("res://baseline_sim.gd")
var checks := 0
var failures: Array[String] = []
var original: Dictionary

func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("PHASE4 CATALOG FAILED: "+message)

func rejects(candidate: Variant, message: String) -> void:
	var c = Catalog.new()
	check(c.replace_document(original),"precondition valid catalog "+message)
	var before: Dictionary = c.snapshot()
	check(not c.replace_document(candidate) and not c.errors.is_empty() and c.snapshot() == before,"catalog invalid candidate atomic: "+message)

func stat(document: Dictionary, id_: String) -> Dictionary:
	for entry in document.stats:
		if entry.id == id_: return entry
	return {}

func run() -> void:
	var c = Catalog.new()
	check(c.load_file(),"current v2 catalog accepted")
	original = c.snapshot()
	check(original.skills.size() == 3 and original.stats.size() == 10,"three skill and ten stat definitions")
	for id_ in ["skill.frost_pulse","skill.arc_chain"]:
		var definition: Dictionary = c.definition("skills",id_)
		for key_ in ["mana_cost","damage","startup","cycle"]:
			check(definition.provenance[key_].method == "project_design" and definition.provenance[key_].status == "design_choice" and definition.provenance[key_].basis.is_empty(),"new skill provenance remains independent "+id_+"/"+key_)
	for path in [["effect","radius_world",0],["effect","radius_world",INF],["effect","radius_world",33],["effect","max_targets",0],["effect","max_targets",65],["effect","max_targets",true]]:
		var d: Dictionary = original.duplicate(true)
		d.skills[1][path[0]][path[1]] = path[2]
		rejects(d,"area "+str(path))
	for field in ["duration_ticks","slow_bps","kind"]:
		var d: Dictionary = original.duplicate(true)
		d.skills[1].effect.status[field] = 0 if field != "kind" else "freeze"
		rejects(d,"unsupported status "+field)
	for field in ["range_world","jump_range_world"]:
		var d: Dictionary = original.duplicate(true)
		d.skills[2].effect[field] = -1
		rejects(d,"chain negative "+field)
	var chain_status: Dictionary = original.duplicate(true)
	chain_status.skills[2].effect.status = original.skills[1].effect.status.duplicate(true)
	rejects(chain_status,"unsupported chain status")
	for bad in [null,1,"",true,"x".repeat(33)]:
		var d: Dictionary = original.duplicate(true)
		d.skills[1].display_name = bad
		rejects(d,"invalid name "+str(bad))
	for field in ["minimum_raw","maximum_raw","default_raw"]:
		var d: Dictionary = original.duplicate(true)
		stat(d,"stat.spell_power")[field] = 2147483648
		rejects(d,"unrepresentable stat "+field)
	var wrong_unit: Dictionary = original.duplicate(true)
	stat(wrong_unit,"stat.spell_power").unit = "health"
	stat(wrong_unit,"stat.spell_power").scale = 256
	rejects(wrong_unit,"semantic combat unit")
	var missing: Dictionary = original.duplicate(true)
	missing.stats.remove_at(2)
	rejects(missing,"required v2 combat stat")
	var narrow: Dictionary = original.duplicate(true)
	stat(narrow,"stat.resist.cold").maximum_raw = 5000
	narrow.enemies[0]["defenses"] = {"stat.resist.cold":6000}
	rejects(narrow,"enemy defense outside narrower definition")
	var hp: Dictionary = original.duplicate(true)
	stat(hp,"stat.health").maximum_raw = 5000
	rejects(hp,"player maximum outside definition")
	var enemy_hp: Dictionary = original.duplicate(true)
	enemy_hp.enemies[0].max_health_raw = 2147483648
	rejects(enemy_hp,"enemy maximum outside 31bit")
	var unnamed: Dictionary = original.duplicate(true)
	for entry in unnamed.skills: entry.erase("display_name")
	check(c.replace_document(unnamed),"optional names absent remains accepted")
	var s = Sim.new(c)
	check(s.valid_profile and s.skill_definition("skill.frost_pulse").get("display_name","") == "" and not s.skill_display("skill.frost_pulse").display_name.is_empty(),"name fallback exists without mutating source definition")
	var old = Catalog.new()
	check(old.load_file("res://evidence/phase4/reference-phase3/game_data/catalog.json"),"accepted historical v1 catalog remains valid")
	if not old.snapshot().is_empty(): check(Sim.new(old).valid_profile,"historical v1 catalog initializes valid current simulation")
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional catalog harness failure proof")
	print(JSON.stringify({"scope":"Phase4 extended catalog atomic validation; no D2R schema claim","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)

