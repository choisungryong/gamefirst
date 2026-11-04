extends SceneTree
## One-time reference generation from the preserved, accepted phase2 source.
## Not a production performance measurement or an original-game rules oracle.
const SOURCE = "C:/Project/game-research/implementation-backups/phase2-final-source-20261027/baseline_sim.gd"
const OUTPUT = "res://tests/fixtures/phase3-phase2-baseline.json"

func _initialize() -> void:
	call_deferred("run")

func digest(s: RefCounted, trace: Array) -> String:
	var entities: Array = []
	var ids: Array = s.enemies.keys()
	ids.sort()
	for identity in ids: entities.append(s.enemies[identity])
	return JSON.stringify({"tick":s.tick,"player":s.player,"move_target":s.move_target,"life":s.life,"mana":s.mana_raw,"enemies":entities,"bolts":s.bolts,"pending":s.pending,"shots":s.shots,"hits":s.hits,"kills":s.kills,"rng":str(s.rng.state),"events":trace}).sha256_text()

func run() -> void:
	var reference: GDScript = load(SOURCE)
	if reference == null:
		printerr("Cannot load preserved phase2 source")
		quit(1)
		return
	var cases: Array = []
	for count in [1,10,100,300,500]:
		var s = reference.new()
		s.reset(count)
		# Explicit fixed high-health stress, not normal gameplay balance.
		s.life = 1000000.0
		s.mana_raw = 100000000
		var trace: Array = []
		var checkpoints: Array = []
		for frame in range(600):
			if frame % 120 == 0:
				s.set_destination(Vector2(cos(frame*.01),sin(frame*.01))*7)
			var target: Dictionary = s.nearest_enemy(s.player)
			var aim: Vector2 = target.get("p",s.player+Vector2.RIGHT)
			s.step(frame % 90 < 75 and not target.is_empty(),aim)
			trace.append_array(s.events.duplicate(true))
			if frame % 60 == 59: checkpoints.append(digest(s,trace))
		cases.append({"count":count,"checkpoints":checkpoints,"final_tick":s.tick,"shots":s.shots,"hits":s.hits,"kills":s.kills,"event_count":trace.size()})
	var output := FileAccess.open(OUTPUT,FileAccess.WRITE)
	if output == null:
		quit(1)
		return
	output.store_string(JSON.stringify({"scope":"accepted phase2 local deterministic stress snapshots; independent design, not D2R rules","engine":Engine.get_version_info().string,"source":SOURCE,"source_sha256":FileAccess.get_sha256(SOURCE),"catalog_sha256":FileAccess.get_sha256("res://game_data/catalog.json"),"cases":cases},"  "))
	output.flush()
	var ok: bool = output.get_error() == OK
	print("PHASE3_BASELINE_GENERATED ",ok)
	quit(0 if ok else 1)
