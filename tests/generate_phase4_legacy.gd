extends SceneTree
## One-time legacy fixture from the accepted phase3 source in a separate test-only
## reference directory. This script is run with --path evidence/phase4/reference-phase3.
## It never executes the mutable phase4 source or changes preserved backups.
const Sim = preload("res://baseline_sim.gd")
const OUTPUT := "C:/Project/d2r-combat-baseline/tests/fixtures/phase4-phase3-legacy-bitwise.json"

func _initialize() -> void:
	call_deferred("run")

func canonical(value: Variant) -> Variant:
	if value is Vector2: return [canonical(value.x),canonical(value.y)]
	# Decimal JSON parsing can differ by one ULP even with full_precision in the
	# installed engine. The fixture uses exact engine-version-pinned float bytes.
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

func run() -> void:
	if FileAccess.file_exists(OUTPUT):
		printerr("Refusing to overwrite an existing independent legacy fixture")
		quit(1)
		return
	var cases: Array = []
	var definitions: Array = []
	for count in [1,10,100,300,500]:
		definitions.append({"name":"phase3_stress_%d" % count,"count":count,"frames":600,"high_health":true,"ai":true,"cast_policy":"75of90","move_policy":"orbit120"})
	definitions.append({"name":"stationary_firebolt","count":1,"frames":180,"high_health":false,"ai":false,"cast_policy":"held","move_policy":"none"})
	definitions.append({"name":"insufficient_mana","count":1,"frames":120,"high_health":false,"ai":false,"cast_policy":"held","move_policy":"none","initial_mana":639})
	for definition in definitions:
		var s = Sim.new()
		s.reset(int(definition.count))
		s.enemy_ai = definition.ai
		if definition.high_health:
			s.life = 1000000.0
			s.mana_raw = 100000000
		if definition.has("initial_mana"): s.mana_raw = int(definition.initial_mana)
		var checkpoints: Array = []
		var trace: Array = []
		for frame in range(int(definition.frames)):
			if definition.move_policy == "orbit120" and frame % 120 == 0:
				s.set_destination(Vector2(cos(frame*.01),sin(frame*.01))*7)
			var target: Dictionary = s.nearest_enemy(s.player)
			var aim: Vector2 = target.get("p",s.player+Vector2.RIGHT)
			var held: bool = definition.cast_policy == "held" or frame % 90 < 75
			s.step(held and not target.is_empty(),aim)
			trace.append_array(s.events.duplicate(true))
			if frame % 60 == 59:
				checkpoints.append({"frame":frame+1,"state":snapshot(s,trace)})
				trace.clear()
		cases.append({"input":definition,"checkpoints":checkpoints})
	var fixture: Dictionary = {"scope":"Accepted phase3 legacy FireBolt state/event/RNG projections; not D2R equivalence or GPU performance",
		"float_encoding":"var_to_bytes(float64).hex_encode(), pinned Godot engine/platform",
		"engine":Engine.get_version_info().string,
		"source_sha256":FileAccess.get_sha256("res://baseline_sim.gd"),
		"catalog_loader_sha256":FileAccess.get_sha256("res://data/game_catalog.gd"),
		"catalog_sha256":FileAccess.get_sha256("res://game_data/catalog.json"),
		"generator_sha256":FileAccess.get_sha256(get_script().resource_path),"cases":cases}
	var output := FileAccess.open(OUTPUT,FileAccess.WRITE)
	if output == null:
		quit(1)
		return
	# Exact float round-trip is essential for an old-field equality oracle.
	# https://docs.godotengine.org/en/4.5/classes/class_json.html#class-json-method-stringify
	output.store_string(JSON.stringify(fixture,"  ",true,true))
	output.flush()
	var ok: bool = output.get_error() == OK
	print(JSON.stringify({"success":ok,"cases":cases.size(),"source_sha256":fixture.source_sha256,"catalog_sha256":fixture.catalog_sha256}))
	quit(0 if ok else 1)
