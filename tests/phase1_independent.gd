extends SceneTree
## Independent phase1 contract tests. No original-game, OBS or native UI input.
const Catalog = preload("res://data/game_catalog.gd")
const Sim = preload("res://baseline_sim.gd")
var checks := 0
var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		printerr("PHASE1 REVIEW FAILED: "+message)

func mutate(document: Dictionary, path: Array, value: Variant) -> Dictionary:
	var changed: Dictionary = document.duplicate(true)
	var cursor: Variant = changed
	for index in range(path.size()-1): cursor = cursor[path[index]]
	cursor[path[-1]] = value
	return changed

func reject(catalog: RefCounted, candidate: Variant, reason: String) -> void:
	var previous: Dictionary = catalog.snapshot()
	var accepted: bool = catalog.replace_document(candidate)
	check(not accepted, reason+" is rejected")
	check(previous == catalog.snapshot(), reason+" preserves previously active catalog")
	check(not catalog.errors.is_empty(), reason+" exposes diagnostics")
	if accepted: catalog.replace_document(previous)

func run() -> void:
	var catalog = Catalog.new()
	check(catalog.load_file(), "default catalog loads")
	var baseline: Dictionary = catalog.snapshot()
	if baseline.is_empty():
		finish()
		return
	check(baseline.catalog_id == "catalog.combat_baseline.v1", "independent catalog has its own ID")
	check(Catalog.validate(baseline).is_empty(), "canonical document validates")
	check(not catalog.load_file("res://tests/definitely-not-a-catalog.json"), "missing file refuses publication")
	check(catalog.snapshot() == baseline and not catalog.errors.is_empty(), "read failure keeps catalog and diagnostic")
	check(not catalog.load_text("{\n bad json"), "JSON syntax failure is rejected")
	check(catalog.snapshot() == baseline and not catalog.errors.is_empty(), "parse failure is atomic")
	for bad_root in [null,true,1.0,"object",[],[baseline]]:
		reject(catalog,bad_root,"wrong root type")
	for field in ["schema_version","catalog_id","definition_version","numeric_scale","simulation_hz","stats","skills","projectiles","enemies","player","experiment","provenance"]:
		var missing: Dictionary = baseline.duplicate(true)
		missing.erase(field)
		reject(catalog,missing,"required top-level "+field)
	for path in [["player"],["experiment"],["skills",0,"cost"],["skills",0,"damage"],["enemies",0,"attack"],["skills",0,"provenance"]]:
		for bad_type in [null,true,0,"data",[]]:
			reject(catalog,mutate(baseline,path,bad_type),"nested object shape "+str(path))
	for bad_value in [true,"640",640.25,-1,INF,NAN]:
		reject(catalog,mutate(baseline,["skills",0,"cost","raw"],bad_value),"raw integer input "+str(bad_value))
	for bad_version in [0,2,1.001,"1"]:
		reject(catalog,mutate(baseline,["schema_version"],bad_version),"unsupported schema "+str(bad_version))
	for bad_ref in [null,[],{},7,"projectile.missing","skill.ember_bolt"]:
		reject(catalog,mutate(baseline,["skills",0,"projectile_id"],bad_ref),"unresolved/wrong-category reference")
	var duplicate: Dictionary = baseline.duplicate(true)
	duplicate.enemies.append(duplicate.enemies[0].duplicate(true))
	reject(catalog,duplicate,"duplicate stable ID")
	reject(catalog,mutate(baseline,["skills",0,"damage","min_raw"],1600),"inverted damage interval")
	reject(catalog,mutate(baseline,["skills",0,"cost","unit"],"health"),"wrong cost unit")
	reject(catalog,mutate(baseline,["stats",1,"scale"],1),"wrong unit scale")
	reject(catalog,mutate(baseline,["skills",0,"cycle_ticks"],18),"cycle not beyond startup")
	reject(catalog,mutate(baseline,["player","spawn_world"],[null,0]),"invalid vector entry")
	reject(catalog,mutate(baseline,["experiment","world_bounds"],[8,0]),"zero world extent")
	reject(catalog,mutate(baseline,["skills",0,"provenance","mana_cost","status"],"observed"),"independent rule falsely marked observation")
	reject(catalog,mutate(baseline,["skills",0,"provenance","mana_cost","basis"],[17]),"provenance basis uses non-string ID")
	reject(catalog,mutate(baseline,["skills",0,"provenance","mana_cost","basis"],[""]),"provenance basis uses empty ID")
	reject(catalog,mutate(baseline,["skills",0,"provenance","mana_cost","basis"],["unknown.claim"]),"provenance basis uses unresolved ID")
	reject(catalog,mutate(baseline,["evidence_index",0,"locator","sha256"],"invalid"),"evidence source locator has invalid digest")
	var duplicate_evidence: Dictionary = baseline.duplicate(true)
	duplicate_evidence.evidence_index.append(duplicate_evidence.evidence_index[0].duplicate(true))
	reject(catalog,duplicate_evidence,"duplicate evidence ID")
	reject(catalog,mutate(baseline,["player","spawn_world"],[100,0]),"player spawn exceeds world bounds")
	reject(catalog,mutate(baseline,["enemies",0,"spawn_world"],[0,-100]),"enemy spawn exceeds world bounds")
	var snapshot: Dictionary = catalog.snapshot()
	snapshot.skills[0].cost.raw = 777
	check(catalog.snapshot().skills[0].cost.raw == 640, "snapshot nested edits are detached")
	var returned: Dictionary = catalog.definition("enemies","enemy.mire_walker")
	returned.attack.damage_raw = 1
	check(catalog.definition("enemies","enemy.mire_walker").attack.damage_raw == 768, "definition nested edits are detached")
	var candidate: Dictionary = baseline.duplicate(true)
	check(catalog.replace_document(candidate), "valid candidate publishes")
	candidate.player.max_mana_raw = 0
	check(catalog.snapshot().player.max_mana_raw == 8960, "published catalog is detached from caller input")
	var a = Sim.new(catalog)
	var b = Sim.new(catalog)
	a.mana_raw = 0
	a.enemy.life_raw = 1
	a.params.world_bounds[0] = 999
	check(b.mana_raw == 8960 and b.enemy.life_raw == 2304, "instances have independent HP and mana")
	check(b.params.world_bounds[0] == 8 and catalog.snapshot().experiment.world_bounds[0] == 8, "runtime parameter arrays cannot mutate another instance or catalog")
	candidate = baseline.duplicate(true)
	candidate.player.max_mana_raw = 1600
	candidate.player.max_health_raw = 5120
	candidate.skills[0].cost.raw = 800
	candidate.skills[0].damage.min_raw = 512
	candidate.skills[0].damage.max_raw = 512
	candidate.skills[0].startup_ticks = 3
	candidate.skills[0].cycle_ticks = 5
	check(catalog.replace_document(candidate), "alternate independent balance validates")
	var custom = Sim.new(catalog)
	custom.enemy_ai = false
	custom.enemy.p = Vector2(100,100)
	check(custom.life == 20 and custom.mana_raw == 1600, "initial runtime maxima come from canonical definition")
	check(custom.cast_request(custom.player+Vector2.RIGHT*3) and custom.mana_raw == 800, "alternate cost overrides legacy alias")
	for tick in range(2): custom.step()
	check(custom.shots == 0, "alternate startup pending before boundary")
	custom.step()
	check(custom.shots == 1, "alternate startup emits at declared boundary")
	for tick in range(2): custom.step()
	check(custom.cast_request(custom.player+Vector2.RIGHT*3) and custom.mana_raw == 0, "alternate cycle and cost allow exactly second shot")
	for tick in range(5): custom.step()
	check(not custom.cast_request(custom.player+Vector2.RIGHT*3), "exhausted alternate mana refuses third shot")
	custom.enemy.p = Vector2.ZERO
	custom.enemy.life_raw = 2304
	custom.bolts = [{"p":Vector2.ZERO,"direction":Vector2.RIGHT,"age":0,"life":132,"id":200}]
	custom.step()
	check(custom.enemy.life_raw == 1792, "fixed alternate raw damage is actually applied")
	custom.reset()
	check(custom.life == 20 and custom.mana_raw == 1600 and custom.bolts.is_empty(), "reset uses active independent definition")
	var research: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://research/phase1-claims.json"))
	check(Catalog.validate_research(research).is_empty(), "real selected research claims validate")
	var blank_count := 0
	var signed_count := 0
	for claim in research.claims:
		if claim.raw == "": blank_count += 1
		if claim.raw.begins_with("-"): signed_count += 1
		check(claim.method == "local_casc_extract" and claim.status == "observed" and claim.meaning_status == "unknown", "source extraction is distinguished from runtime interpretation")
		var source_text: String = FileAccess.get_file_as_string(claim.locator.path)
		check(FileAccess.get_sha256(claim.locator.path) == claim.locator.sha256, "claim source digest matches actual file")
		var lines: PackedStringArray = source_text.split("\n",true)
		var header: PackedStringArray = lines[0].trim_suffix("\r").split("\t",true)
		var column: int = header.find(claim.locator.column)
		var row: PackedStringArray = lines[int(claim.locator.line)-1].trim_suffix("\r").split("\t",true)
		check(column >= 0 and row[column] == claim.raw, "claim raw text matches specified row and column")
	check(blank_count == 2 and signed_count == 1, "actual blank and signed examples are retained")
	for evidence in baseline.evidence_index:
		check(FileAccess.get_sha256(evidence.locator.path) == evidence.locator.sha256, "runtime rule basis points to currently matching evidence digest")
	var fixture: Dictionary = research.duplicate(true)
	fixture.claims[0].raw = "0"
	check(Catalog.validate_research(fixture).is_empty() and fixture.claims[0].raw != research.claims[5].raw, "synthetic zero remains text distinct from source blank")
	fixture.claims[0].unit = null
	check(Catalog.validate_research(fixture).is_empty(), "unknown research unit remains null")
	fixture.claims[0].normalized = 0
	check(not Catalog.validate_research(fixture).is_empty(), "unknown raw meaning cannot silently become runtime zero")
	fixture = research.duplicate(true)
	fixture.claims[0].locator = {}
	check(not Catalog.validate_research(fixture).is_empty(), "missing source locator fields are rejected")
	fixture = research.duplicate(true)
	fixture.claims[0].locator.line = 38.5
	check(not Catalog.validate_research(fixture).is_empty(), "fractional source line is rejected")
	fixture = research.duplicate(true)
	fixture.claims[0].locator.sha256 = "not-a-hash"
	check(not Catalog.validate_research(fixture).is_empty(), "malformed source digest is rejected")
	check(catalog.load_file(), "canonical baseline reloads after mutation fixtures")
	var unit = Sim.new(catalog)
	unit.enemy_ai = false
	unit.enemy.p = Vector2(100,100)
	for cast in range(14):
		check(unit.cast_request(unit.player+Vector2.RIGHT*8), "canonical exhaustion cast "+str(cast+1))
		for tick in range(33): unit.step()
	check(unit.shots == 14 and unit.mana_raw == 0, "14 canonical casts exhaust35 mana without raw loss")
	check(not unit.cast_request(Vector2.ZERO), "15th canonical request is refused")
	var ui_document: Dictionary = baseline.duplicate(true)
	ui_document.player.max_health_raw = 5120
	ui_document.player.max_mana_raw = 5120
	ui_document.skills[0].cost.raw = 512
	ui_document.skills[0].damage.min_raw = 256
	ui_document.skills[0].damage.max_raw = 512
	ui_document.enemies[0].max_health_raw = 1280
	ui_document.skills[0].cycle_ticks = 48
	ui_document.projectiles[0].speed_world_per_second = 8
	check(catalog.replace_document(ui_document), "alternate HUD fixture validates")
	var scene: PackedScene = load("res://Baseline.tscn")
	var view = scene.instantiate()
	view.sim = Sim.new(catalog)
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	view.sync_actors()
	check(view.life_bar.max_value == 20 and view.mana_bar.max_value == 20, "HUD maxima follow independent catalog")
	check(view.life_label.text == "생명 20 / 20" and view.mana_label.text == "마나 20 / 20", "HUD health/mana labels follow independent catalog")
	check(view.cast_status.text.contains("피해 1–2") and view.cast_status.text.contains("마나 2"), "HUD damage and cost follow independent catalog")
	check(view.stats_text.text.contains("적 체력 5") and view.stats_text.text.contains("재시전 0.8초") and view.stats_text.text.contains("비행속도 8"), "experiment panel follows independent catalog")
	check(view.quantity_text(3.125) == "3.125" and view.quantity_text(2.5) == "2.5", "display handles fractional unit values without modifying raw combat values")
	view.sim.mana_raw = 2560
	view.sim.life = 10
	view.sync_actors()
	check(view.life_label.text == "생명 10 / 20" and view.mana_label.text == "마나 10 / 20", "runtime changes retain catalog denominators")
	view.restart()
	check(view.sim.life == 20 and view.sim.mana_raw == 5120, "view restart uses canonical maxima")
	view.free()
	finish()

func finish() -> void:
	if OS.get_cmdline_user_args().has("--prove-failure"):
		check(false,"intentional independent phase1 harness failure")
	print("PHASE1_INDEPENDENT_RESULT ",JSON.stringify({"checks":checks,"failures":failures,"success":failures.is_empty(),"scope":"independent data contract and regression, not D2R equivalence"}))
	quit(0 if failures.is_empty() else 1)
