extends SceneTree
const Catalog = preload("res://data/game_catalog.gd")
const Sim = preload("res://baseline_sim.gd")
var checks := 0
var failures: Array[String] = []

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition: failures.append(message)

func reject(catalog: RefCounted, candidate: Variant, message: String) -> void:
	var previous: Dictionary = catalog.snapshot()
	check(not catalog.replace_document(candidate),message+" rejected")
	check(previous == catalog.snapshot(),message+" preserves active catalog")
	check(not catalog.errors.is_empty(),message+" exposes diagnostic")

func _initialize() -> void:
	var catalog = Catalog.new()
	check(catalog.load_file(),"canonical catalog loads")
	var original: Dictionary = catalog.snapshot()
	check(original.skills[0].id == "skill.ember_bolt","independent stable skill ID")
	check(Catalog.validate(original).is_empty(),"canonical schema is valid")
	check(not catalog.load_text('{bad'),"malformed JSON refused")
	check(not catalog.errors.is_empty() and original == catalog.snapshot(),"parse failure diagnostic and transaction")
	check(not catalog.load_file("res://missing-phase1-catalog.json"),"missing file refused")
	check(original == catalog.snapshot(),"read failure preserves catalog")
	reject(catalog,[],"wrong root")
	var candidate: Dictionary = original.duplicate(true)
	candidate.schema_version = 2
	reject(catalog,candidate,"schema version")
	candidate = original.duplicate(true)
	candidate.skills[0].cost.raw = 640.5
	reject(catalog,candidate,"fractional integer")
	candidate.skills[0].cost.raw = "640"
	reject(catalog,candidate,"string numeric")
	candidate.skills[0].cost.raw = -1
	reject(catalog,candidate,"negative cost")
	candidate = original.duplicate(true)
	candidate.projectiles[0].speed_world_per_second = INF
	reject(catalog,candidate,"nonfinite speed")
	candidate = original.duplicate(true)
	candidate.skills[0].projectile_id = "projectile.missing"
	reject(catalog,candidate,"missing reference")
	candidate.skills[0].projectile_id = []
	reject(catalog,candidate,"reference wrong type")
	candidate = original.duplicate(true)
	candidate.stats.append(candidate.stats[0].duplicate(true))
	reject(catalog,candidate,"duplicate ID")
	candidate = original.duplicate(true)
	candidate.skills[0].damage.max_raw = 1
	reject(catalog,candidate,"inverted range")
	candidate = original.duplicate(true)
	candidate.skills[0].cost.unit = "seconds"
	reject(catalog,candidate,"unknown/mismatched gameplay unit")
	candidate = original.duplicate(true)
	candidate.skills[0].provenance.mana_cost.status = "observed"
	reject(catalog,candidate,"design provenance falsely observed")
	candidate = original.duplicate(true)
	candidate.experiment.erase("world_bounds")
	reject(catalog,candidate,"required field")
	candidate = original.duplicate(true)
	candidate.skills[0].cycle_ticks = 18
	reject(catalog,candidate,"cycle/startup ordering")
	var detached: Dictionary = catalog.definition("skills","skill.ember_bolt")
	detached.cost.raw = 999
	check(catalog.definition("skills","skill.ember_bolt").cost.raw == 640,"definition copy cannot mutate catalog")
	var a = Sim.new(catalog)
	var b = Sim.new(catalog)
	a.enemy.life_raw = 0
	a.mana_raw = 0
	check(b.enemy.life_raw == 2304 and b.mana_raw == 8960,"two runtime states do not share HP or mana")
	check(catalog.definition("enemies","enemy.mire_walker").max_health_raw == 2304,"runtime mutation cannot alter definition")
	candidate = original.duplicate(true)
	candidate.skills[0].cost.raw = 512
	candidate.skills[0].damage.min_raw = 256
	candidate.skills[0].damage.max_raw = 256
	candidate.skills[0].startup_ticks = 12
	check(catalog.replace_document(candidate),"valid independent balance update accepted")
	var custom = Sim.new(catalog)
	custom.enemy_ai = false
	custom.enemy.p = custom.player+Vector2.RIGHT*1.1
	check(custom.cast_request(custom.enemy.p) and custom.mana_raw == 8448,"gameplay cost comes from catalog, not old alias")
	for i in range(11): custom.step()
	check(custom.shots == 0,"updated startup remains pending")
	custom.step()
	check(custom.shots == 1,"updated startup consumed by core")
	for i in range(20): custom.step()
	check(custom.enemy.life_raw == 2048,"updated raw damage consumed by core")
	var research: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://research/phase1-claims.json"))
	check(Catalog.validate_research(research).is_empty(),"selected original table claims validate")
	var blank := false
	var negative := false
	for claim in research.claims:
		if claim.raw == "": blank = true
		if String(claim.raw).begins_with("-"): negative = true
	check(blank and negative,"real blank and signed source values preserved")
	var fixture: Dictionary = research.duplicate(true)
	fixture.claims[0].raw = "0"
	check(Catalog.validate_research(fixture).is_empty() and fixture.claims[0].raw == "0","synthetic zero stays text, distinct from blank")
	fixture.claims[0].unit = null
	check(Catalog.validate_research(fixture).is_empty(),"unknown research unit remains null")
	fixture.claims[0].normalized = 0
	check(not Catalog.validate_research(fixture).is_empty(),"unknown source meaning cannot silently become runtime zero")
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional catalog harness failure")
	print("CATALOG_TEST_RESULT ",JSON.stringify({"checks":checks,"failures":failures}))
	quit(0 if failures.is_empty() else 1)
