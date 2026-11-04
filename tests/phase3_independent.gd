extends SceneTree
## Headless correctness checks only. Actual GPU evidence is audited separately.
const Sim = preload("res://baseline_sim.gd")
const Registry = preload("res://presentation/actor_registry.gd")
const BASELINE = "res://tests/fixtures/phase3-phase2-baseline.json"
var checks := 0
var failures: Array[String] = []
var probe_owner: Node3D

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		printerr("PHASE3 INDEPENDENT FAILED: "+message)

func digest(s: RefCounted, trace: Array) -> String:
	var entities: Array = []
	var ids: Array = s.enemies.keys()
	ids.sort()
	for identity in ids: entities.append(s.enemies[identity])
	return JSON.stringify({"tick":s.tick,"player":s.player,"move_target":s.move_target,"life":s.life,"mana":s.mana_raw,"enemies":entities,"bolts":s.bolts,"pending":s.pending,"shots":s.shots,"hits":s.hits,"kills":s.kills,"rng":str(s.rng.state),"events":trace}).sha256_text()

func baseline_invariance() -> void:
	var fixture: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASELINE))
	check(fixture.source_sha256 == "9f56569c739a1523a6ff0b68456074dce48a4779cae1f3449e585895d5274dc0","golden fixture pins accepted phase2 source")
	check(fixture.catalog_sha256 == FileAccess.get_sha256("res://game_data/catalog.json"),"golden fixture uses the current unchanged catalog")
	check(fixture.engine == Engine.get_version_info().string,"golden snapshots use the same Godot engine version")
	for cache_enabled in [true,false]:
		for expected in fixture.cases:
			var count: int = int(expected.count)
			var s = Sim.new()
			s.reset(count)
			s.query_cache_enabled = cache_enabled
			s.life = 1000000.0
			s.mana_raw = 100000000
			var trace: Array = []
			var checkpoints: Array = []
			for frame in range(600):
				if frame % 120 == 0: s.set_destination(Vector2(cos(frame*.01),sin(frame*.01))*7)
				var target: Dictionary = s.nearest_enemy(s.player)
				var aim: Vector2 = target.get("p",s.player+Vector2.RIGHT)
				s.step(frame % 90 < 75 and not target.is_empty(),aim)
				trace.append_array(s.events.duplicate(true))
				if frame % 60 == 59: checkpoints.append(digest(s,trace))
			for index in range(expected.checkpoints.size()):
				check(checkpoints[index] == expected.checkpoints[index],"phase2 combat/RNG invariant cache=%s count=%d tick=%d" % [cache_enabled,count,(index+1)*60])
			check(s.tick == int(expected.final_tick) and s.shots == int(expected.shots) and s.hits == int(expected.hits) and s.kills == int(expected.kills) and trace.size() == int(expected.event_count),"phase2 final counts invariant cache=%s count=%d" % [cache_enabled,count])

func spatial_cache_invariants() -> void:
	var s = Sim.new()
	s.reset(0)
	s.enemy_ai = false
	var handle_: Dictionary = s.spawn_enemy(Vector2(2,0),.3)
	s.rebuild_grid()
	var first: Array = s.query_segment(Vector2.ZERO,Vector2(4,0))
	var second: Array = s.query_segment(Vector2(4,0),Vector2.ZERO)
	check(first == second and first.has(handle_.id) and s.query_cache_hits == 1 and s.query_cache_misses == 1,"cell-AABB cache reuses sorted candidates for reverse segment")
	first.clear()
	check(s.query_segment(Vector2.ZERO,Vector2(4,0)).has(handle_.id),"clearing a public query result cannot corrupt future cached candidates")
	s.entity(handle_).p = Vector2(10,0)
	s.rebuild_grid()
	check(s.query_cache.is_empty() and s.query_cache_hits == 0 and s.query_cache_misses == 0,"grid rebuild invalidates cached queries and measurements")
	check(not s.query_segment(Vector2.ZERO,Vector2(4,0)).has(handle_.id) and s.query_segment(Vector2(9,0),Vector2(11,0)).has(handle_.id),"moved entity appears only in rebuilt spatial cells")
	s.bolts.clear()
	s.step_bolts()
	check(s.spatial_grid.is_empty() and s.query_cache.is_empty() and s.query_cache_hits == 0 and s.query_cache_misses == 0,"zero-projectile grid skip also invalidates cache and counters")
	check(s.query_segment(Vector2(9,0),Vector2(11,0)).is_empty(),"empty spatial grid cannot return stale cached candidates")
	s.rebuild_grid()
	s.query_segment(Vector2(9,0),Vector2(11,0))
	s.query_segment(Vector2(9,0),Vector2(11,0))
	s.reset(0)
	check(s.query_cache.is_empty() and s.query_cache_hits == 0 and s.query_cache_misses == 0,"reset clears all previous-generation query cache state")
	s.spawn_enemy(Vector2.ZERO)
	s.rebuild_grid()
	s.query_cache_enabled = false
	var uncached: Array = s.query_segment(Vector2(-1,0),Vector2(1,0))
	s.query_segment(Vector2(-1,0),Vector2(1,0))
	check(uncached.size() == 1 and s.query_cache.is_empty() and s.query_cache_hits == 0 and s.query_cache_misses == 2,"cache bypass preserves candidates without storing or reusing entries")

func benchmark_statistics() -> void:
	var harness: Node = load("res://benchmark/crowd_benchmark.gd").new()
	var values: Array = []
	for number in range(100,0,-1): values.append(float(number))
	var actual: Dictionary = harness.summary(values)
	check(actual.min == 1.0 and actual.max == 100.0,"benchmark reports the real minimum and worst frame")
	check(actual.p50 == 50.0 and actual.p95 == 95.0 and actual.p99 == 99.0,"benchmark uses nearest-rank percentiles on unsorted samples")
	check(values[0] == 100.0 and values[-1] == 1.0,"benchmark statistics do not reorder the raw input")
	check(harness.summary([]).is_empty(),"empty measurement cannot invent frame statistics")
	var single: Dictionary = harness.summary([8.0])
	check(single.p50 == 8 and single.p95 == 8 and single.p99 == 8,"single-sample percentiles stay within the sample")
	for token in ["nan","inf","oops","-1","4000"]:
		harness.bad_arguments.clear()
		harness.numeric("--bench-seconds="+token,"--bench-seconds=",.05,3600)
		check(not harness.bad_arguments.is_empty(),"benchmark rejects non-finite or out-of-range duration "+token)
	harness.bad_arguments.clear()
	check(harness.numeric("--bench-seconds=60","--bench-seconds=",.05,3600) == 60 and harness.bad_arguments.is_empty(),"benchmark accepts the intended finite measurement duration")
	var escape := InputEventKey.new()
	escape.pressed = true
	escape.keycode = KEY_ESCAPE
	harness._unhandled_input(escape)
	check(not harness.sim.paused,"benchmark ignores gameplay pause input")
	harness.free()

func bounded_history() -> void:
	var s = Sim.new()
	s.reset(0)
	var total: int = Sim.HISTORY_CAPACITY*3+17
	for index in range(total):
		s.events.clear()
		s.emit("probe",{"ordinal":index})
		if index % 997 == 0: check(s.history_count() <= Sim.HISTORY_CAPACITY,"history remains bounded during repeated wrap "+str(index))
	var history: Array = s.history_snapshot()
	check(history.size() == Sim.HISTORY_CAPACITY and s.history_count() == Sim.HISTORY_CAPACITY,"history retains exactly the configured capacity")
	check(s.history_dropped == total-Sim.HISTORY_CAPACITY,"history accurately counts overwritten entries")
	var ordered := true
	for index in range(history.size()): ordered = ordered and int(history[index].ordinal) == total-Sim.HISTORY_CAPACITY+index
	check(ordered,"wrapped history exposes the real chronological suffix")
	history.clear()
	check(s.history_count() == Sim.HISTORY_CAPACITY,"history snapshot array cannot clear internal ring storage")
	s.reset(0)
	check(s.history.is_empty() and s.history_count() == 0 and s.history_dropped == 0,"reset empties wrapped history and dropped count")
	s.emit("after_reset",{"ordinal":1})
	check(s.history_count() == 1 and s.history[0].kind == "after_reset","history starts cleanly after a wrapped reset")

	var fixture: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(BASELINE))
	var expected: Dictionary = fixture.cases[3]
	s = Sim.new()
	s.reset(300)
	s.life = 1000000.0
	s.mana_raw = 100000000
	s.profiling_enabled = true
	var trace: Array = []
	for frame in range(600):
		if frame % 120 == 0: s.set_destination(Vector2(cos(frame*.01),sin(frame*.01))*7)
		var target: Dictionary = s.nearest_enemy(s.player)
		var aim: Vector2 = target.get("p",s.player+Vector2.RIGHT)
		s.step(frame % 90 < 75 and not target.is_empty(),aim)
		trace.append_array(s.events.duplicate(true))
		if frame % 60 == 59: check(digest(s,trace) == expected.checkpoints[frame/60],"profiling does not change combat/RNG tick "+str(frame+1))
	var nonnegative := true
	for value in s.profile_us.values(): nonnegative = nonnegative and value >= 0
	check(nonnegative,"profiling durations are nonnegative microseconds")
	s.reset(1)
	s.step()
	check(s.profile_us.grid == 0 and s.profile_us.query == 0 and s.profile_us.narrowphase == 0 and s.spatial_grid.is_empty(),"zero-projectile step skips spatial rebuild and query work")

func probe_load(_path: String, at: Vector3) -> Node3D:
	var node := Node3D.new()
	node.position = at
	var player := AnimationPlayer.new()
	node.add_child(player)
	node.set_meta("player",player)
	probe_owner.add_child(node)
	return node

func probe_animate(_node: Node3D, _clip: String, _speed: float = 1.0, _force: bool = false, _blend: float = .06) -> void:
	pass

func probe_tint(_node: Node3D, _color: Color) -> void:
	pass

func bounded_actor_pool() -> void:
	# Lightweight nodes test pool-capacity bookkeeping. Actual rig poses are
	# independently exercised by phase2_scene_independent.gd and new FX checks.
	probe_owner = Node3D.new()
	root.add_child(probe_owner)
	var registry = Registry.new()
	var primary: Node3D = probe_load("",Vector3.ZERO)
	registry.setup(primary,probe_load,probe_animate,probe_tint)
	var s = Sim.new()
	s.reset(Registry.POOL_CAPACITY+3)
	registry.sync(s)
	var first_ids: Dictionary = {}
	for node in registry.actors.values(): first_ids[node.get_instance_id()] = true
	check(first_ids.size() == Registry.POOL_CAPACITY+3,"pool-capacity probe gives each live entity a unique node")
	var created_before: int = registry.created_count
	var old_handles: Array = s.enemies.values().map(func(state): return s.handle(state))
	s.reset(Registry.POOL_CAPACITY+3)
	registry.sync(s)
	# Two excess nodes are deliberately discarded because inactive retention is
	# capped; the next frame may recreate only those bounded excess nodes.
	check(registry.pool.size() <= Registry.POOL_CAPACITY,"pool remains bounded while replacing all generations")
	check(registry.created_count <= created_before+2,"release-before-acquire avoids doubling the entire actor population")
	var stale_ok := true
	for handle_ in old_handles: stale_ok = stale_ok and registry.actor_for(handle_) == null
	check(stale_ok,"all pre-reset actor handles remain invalid after complete generation replacement")
	s.reset(0)
	registry.sync(s)
	check(registry.actors.is_empty() and registry.states.is_empty() and registry.pool.size() == Registry.POOL_CAPACITY,"retired actor pool honors exact inactive capacity")
	var hidden := not primary.visible
	var stopped := true
	var live_pool_ids: Dictionary = {}
	for node in registry.pool:
		hidden = hidden and not node.visible
		var player: AnimationPlayer = node.get_meta("player")
		stopped = stopped and not player.is_playing()
		live_pool_ids[node.get_instance_id()] = true
	check(hidden and stopped and live_pool_ids.size() == registry.pool.size(),"retained actor pool is unique, hidden and stopped")
	created_before = registry.created_count
	for cycle in range(4):
		s.reset(100)
		registry.sync(s)
		s.reset(0)
		registry.sync(s)
	check(registry.created_count == created_before and registry.pool.size() == Registry.POOL_CAPACITY,"repeated in-budget actor reuse does not create additional nodes")
	check(registry.reused_count > 0 and registry.released_count > 0,"actor counters prove actual reuse and release")
	registry.reset()
	probe_owner.free()

func run() -> void:
	baseline_invariance()
	spatial_cache_invariants()
	benchmark_statistics()
	bounded_history()
	bounded_actor_pool()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional independent phase3 failure proof")
	print(JSON.stringify({"scope":"phase3 independent headless correctness; not GPU performance, D2R equivalence or SACRATA quality","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
