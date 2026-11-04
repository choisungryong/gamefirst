extends SceneTree
## Independent phase2 checks. Core is synthetic game logic, not D2R equivalence.
const Sim = preload("res://baseline_sim.gd")
var checks := 0
var failures: Array[String] = []

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		printerr("PHASE2 INDEPENDENT FAILED: "+message)

func fresh(count: int = 0) -> RefCounted:
	var s = Sim.new()
	s.reset(count)
	s.enemy_ai = false
	return s

func bolt(point: Vector2, direction: Vector2 = Vector2.RIGHT, id_: int = 1) -> Dictionary:
	return {"p":point,"direction":direction,"age":0,"life":132,"id":id_}

func close(a: float, b: float, epsilon: float = .00002) -> bool:
	return absf(a-b) <= epsilon

## Independent geometric oracle: project on a unit ray and use the circle chord.
## Production uses quadratic segment roots; this intentionally takes another path.
func oracle_entry(start: Vector2, finish_: Vector2, center: Vector2, radius: float) -> float:
	var toward: Vector2 = center-start
	if toward.length_squared() <= radius*radius: return 0.0
	var length_: float = start.distance_to(finish_)
	if length_ <= .0000001: return -1.0
	var direction: Vector2 = (finish_-start)/length_
	var along: float = toward.dot(direction)
	var perpendicular_sq: float = maxf(0.0,toward.length_squared()-along*along)
	if perpendicular_sq > radius*radius: return -1.0
	var distance: float = along-sqrt(maxf(0.0,radius*radius-perpendicular_sq))
	if distance < 0 or distance > length_: return -1.0
	return distance/length_

func hit_events(s: RefCounted) -> Array:
	return s.history.filter(func(e): return e.kind == "hit")

func core_checks() -> void:
	var s = fresh()
	check(s.enemies.is_empty() and s.enemy.is_empty() and s.alive_count() == 0,"reset0 is an empty world")
	for count in [2,10,100]:
		s.reset(count)
		check(s.enemies.size() == count and s.alive_count() == count,"requested live entity count "+str(count))
		var unique: Dictionary = {}
		var references_valid := true
		for state in s.enemies.values():
			var identity: Dictionary = s.handle(state)
			unique[str(identity.id)+":"+str(identity.generation)] = true
			if s.entity(identity) != state: references_valid = false
		check(unique.size() == count and references_valid,"all handles uniquely resolve for count "+str(count))
		var state: Dictionary = s.enemies.values()[0]
		state.life_raw = 321
		check(s.entity(s.handle(state)).life_raw == 321,"entity collection exposes the actual per-instance state")
		check(s.enemies.values()[1].life_raw != 321,"separate entities do not share current HP")
		s.reset()
		check(s.enemies.size() == count and s.history.is_empty(),"reset without count keeps configured count and clears history")
		check(s.enemies.values()[0].life_raw == 2304,"reset restores catalog-defined HP")
		# Exercise death/despawn/reuse for each required population, not only N=1.
		s.enemy_ai = false
		s.corpse_ticks = 2
		var old_population: Array = []
		var shots: Array = []
		var index := 0
		for current in s.enemies.values():
			current.p = Vector2(index*4.0,0)
			current.life_raw = 1
			old_population.append(s.handle(current))
			shots.append(bolt(current.p,Vector2.RIGHT,index+1))
			index += 1
		s.bolts = shots
		s.step_bolts()
		check(s.kills == count and s.alive_count() == 0,"all entities die once for count "+str(count))
		s.rebuild_grid()
		check(s.query_segment(Vector2(-2,0),Vector2(count*4,0)).is_empty(),"dead population is excluded from spatial grid "+str(count))
		s.step()
		s.step()
		check(s.enemies.is_empty(),"all corpses expire for count "+str(count))
		var reused_valid := true
		for old_identity in old_population:
			var reused: Dictionary = s.spawn_enemy(Vector2.ZERO)
			reused_valid = reused_valid and reused.id == old_identity.id and reused.generation > old_identity.generation and s.entity(old_identity).is_empty()
		check(reused_valid and s.enemies.size() == count,"entire population reuses IDs without stale handles "+str(count))

	s = fresh(2)
	var ids: Array = s.enemies.keys()
	ids.sort()
	var first: Dictionary = s.enemies[ids[0]]
	var first_handle: Dictionary = s.handle(first)
	var second_handle: Dictionary = s.handle(s.enemies[ids[1]])
	check(s.despawn_enemy(first_handle),"despawn current first handle succeeds")
	check(s.entity(first_handle).is_empty(),"despawn invalidates the old handle")
	check(s.enemy == s.entity(second_handle),"legacy alias follows the first remaining active entity")
	var replacement: Dictionary = s.spawn_enemy(Vector2(9,9))
	check(replacement.id == first_handle.id and replacement.generation > first_handle.generation,"pool ID reuse increments generation")
	check(not s.despawn_enemy(first_handle) and not s.entity(replacement).is_empty(),"stale handle cannot despawn replacement")
	check(not first.is_same_typed(s.entity(replacement)) or first.generation != replacement.generation,"old Dictionary state remains a different generation")
	var live_handles: Array = s.enemies.values().map(func(e): return s.handle(e))
	s.reset(2)
	var stale_count := 0
	for identity in live_handles:
		if s.entity(identity).is_empty(): stale_count += 1
	check(stale_count == live_handles.size(),"reset invalidates every pre-reset handle")
	check(s.entity({"id":1.0,"generation":1}).is_empty() and s.entity({"id":1,"generation":null}).is_empty(),"malformed handles cannot resolve")
	for identity in s.enemies.values().map(func(e): return s.handle(e)): s.despawn_enemy(identity)
	check(s.enemy.is_empty() and s.enemies.is_empty(),"removing all entities clears the legacy alias")

	s = fresh()
	var event_count: int = s.history.size()
	for radius in [0.0,-2.0,65.0,INF,NAN]:
		check(s.spawn_enemy(Vector2.ZERO,radius).is_empty(),"invalid radius is rejected "+str(radius))
	check(s.spawn_enemy(Vector2(NAN,0)).is_empty() and s.enemies.is_empty() and s.history.size() == event_count,"invalid position/radius does not publish state or events")
	check(not s.spawn_enemy(Vector2(100,100)).is_empty(),"finite out-of-world fixture coordinates are explicitly permitted")
	check(s.enemies.values()[0].radius == s.params.collision_radius,"default radius uses catalog effective collision radius")
	s.reset(2001)
	check(s.enemies.size() == Sim.MAX_ENTITIES and s.spawn_enemy(Vector2.ZERO).is_empty(),"entity allocation cap is enforced")

	s = fresh()
	check(close(s.swept_fraction(Vector2(-5,0),Vector2(5,0),Vector2.ZERO,1),.4),"collision returns the first entry, not closest point")
	check(close(s.swept_fraction(Vector2(-2,1),Vector2(2,1),Vector2.ZERO,1),.5),"tangent segment has one entry")
	check(s.swept_fraction(Vector2(-2,1.01),Vector2(2,1.01),Vector2.ZERO,1) < 0,"parallel near miss stays a miss")
	check(s.swept_fraction(Vector2.ZERO,Vector2(5,0),Vector2.ZERO,1) == 0,"starting inside hits at time0")
	check(s.swept_fraction(Vector2.ZERO,Vector2.ZERO,Vector2.ZERO,1) == 0,"zero-length overlap hits at time0")
	check(s.swept_fraction(Vector2(2,0),Vector2(2,0),Vector2.ZERO,1) < 0,"zero-length outside does not hit")
	check(close(s.swept_fraction(Vector2(-2,0),Vector2(-1,0),Vector2.ZERO,1),1),"endpoint-only contact is included")
	check(s.swept_fraction(Vector2(2,0),Vector2(3,0),Vector2.ZERO,1) < 0,"circle behind movement cannot hit")

	# Farther center can have the earlier boundary when radii differ.
	var small: Dictionary = s.spawn_enemy(Vector2(2,0),.2)
	var large: Dictionary = s.spawn_enemy(Vector2(3,0),2)
	s.bolts = [bolt(Vector2.ZERO)]
	s.bolt_speed = 360
	s.step_bolts()
	var events: Array = hit_events(s)
	check(events.size() == 1 and events[0].entity == large,"heterogeneous radius chooses first boundary, not nearest center")
	check(close(events[0].p[0],1.0) and close(events[0].p[1],0),"impact point is at large-circle entry")
	check(s.entity(small).life_raw == 2304,"later target is not damaged by nonpiercing bolt")

	s = fresh()
	var lower: Dictionary = s.spawn_enemy(Vector2(2,0),1)
	var higher: Dictionary = s.spawn_enemy(Vector2(2,0),1)
	var low_state: Dictionary = s.entity(lower)
	s.enemies.erase(lower.id)
	s.enemies[lower.id] = low_state
	s.bolts = [bolt(Vector2.ZERO)]
	s.bolt_speed = 240
	s.step_bolts()
	events = hit_events(s)
	check(events.size() == 1 and events[0].entity == lower,"equal collision times choose lower ID despite reversed dictionary insertion")
	low_state.p = Vector2(2,0)
	s.entity(higher).p = Vector2(-2,0)
	check(s.nearest_enemy(Vector2.ZERO).id == lower.id,"nearest target distance ties use ID order")

	# Radius reaches the segment from another center cell; fast paths cross many cells.
	s = fresh()
	var edge: Dictionary = s.spawn_enemy(Vector2(2.01,2.01),2.02)
	s.rebuild_grid()
	check(s.query_segment(Vector2(-10,0),Vector2(10,0)).has(edge.id),"entity circle AABB indexes radius outside its center cell")
	s.bolts = [bolt(Vector2(-10,0))]
	s.bolt_speed = 1200
	s.step_bolts()
	check(s.hits == 1 and hit_events(s)[0].entity == edge,"high-speed segment crosses multiple cells without missing a radius-only hit")
	check(s.bolts.is_empty(),"one hit consumes the projectile")
	var previous_life: int = s.entity(edge).life_raw
	for i in range(10): s.step()
	check(s.hits == 1 and s.entity(edge).life_raw == previous_life,"consumed projectile cannot apply damage again")

	# Brute-force chord oracle must be a subset of grid candidates for each query.
	s = fresh()
	var random := RandomNumberGenerator.new()
	random.seed = 71913
	for i in range(40): s.spawn_enemy(Vector2(random.randf_range(-30,30),random.randf_range(-30,30)),random.randf_range(.05,3.5))
	s.rebuild_grid()
	for query in range(48):
		# Each geometric query gets the same live snapshot. Earlier bolts must not
		# turn later expected targets into corpses (which the live-only grid excludes).
		for state in s.enemies.values():
			state.state = "approach"
			state.life_raw = state.max_raw
		s.rebuild_grid()
		var start := Vector2(random.randf_range(-40,40),random.randf_range(-40,40))
		var end := Vector2(random.randf_range(-40,40),random.randf_range(-40,40))
		var candidates: Array = s.query_segment(start,end)
		var misses: Array = []
		for state in s.enemies.values():
			var oracle: float = oracle_entry(start,end,state.p,state.radius)
			if oracle >= 0 and not candidates.has(state.id): misses.append(state.id)
		check(misses.is_empty(),"grid query covers brute-force true hits for randomized query "+str(query))
		# Check selected hit independently of candidate construction.
		var expected: Dictionary = {}
		var best: float = INF
		for state in s.enemies.values():
			var fraction: float = oracle_entry(start,end,state.p,state.radius)
			if fraction >= 0 and (fraction < best-.000001 or (absf(fraction-best) <= .000001 and (expected.is_empty() or state.id < expected.id))):
				best = fraction
				expected = state
		var offset: int = hit_events(s).size()
		s.bolt_speed = start.distance_to(end)*60.0
		s.bolts = [bolt(start,(end-start).normalized(),query+1)]
		s.step_bolts()
		var actual: Array = hit_events(s)
		check(actual.size() == offset+(0 if expected.is_empty() else 1),"oracle hit presence matches narrowphase "+str(query))
		if not expected.is_empty(): check(actual[-1].entity.id == expected.id,"oracle first target matches query "+str(query))

	s = fresh()
	var dead: Dictionary = s.spawn_enemy(Vector2.ZERO)
	s.entity(dead).life_raw = 1
	s.bolts = [bolt(Vector2.ZERO),bolt(Vector2.ZERO,Vector2.RIGHT,2)]
	s.step_bolts()
	check(s.hits == 1 and s.kills == 1 and s.alive_count() == 0,"same-tick projectiles cannot damage newly dead entity twice")
	check(s.history.filter(func(e): return e.kind == "enemy_dead").size() == 1,"single death event is emitted")
	s.bolts = [bolt(Vector2.ZERO,Vector2.RIGHT,3)]
	s.step_bolts()
	check(s.hits == 1 and s.entity(dead).life_raw == 0,"dead entity is not hittable afterward")
	s.paused = true
	for i in range(10): s.step()
	check(s.tick == 0 and not s.entity(dead).is_empty(),"pause freezes corpse lifetime")
	s.paused = false
	for i in range(s.corpse_ticks-1): s.step()
	check(not s.entity(dead).is_empty(),"corpse remains before exact expiry tick")
	s.step()
	check(s.entity(dead).is_empty() and s.enemies.is_empty() and s.enemy.is_empty(),"corpse expires and alias clears at its deadline")
	check(s.history.filter(func(e): return e.kind == "enemy_despawn").size() == 1,"corpse expires only once")
	s.rebuild_grid()
	check(s.query_segment(Vector2(-2,0),Vector2(2,0)).is_empty(),"despawned corpse cannot remain in spatial candidates")

	var traces: Array = []
	for repetition in range(2):
		s = fresh(10)
		for i in range(180): s.step(i < 150,Vector2(3.4,-2.5))
		traces.append(s.history.duplicate(true))
	check(traces[0] == traces[1],"fixed multi-entity seed and input reproduce event trace")
	s = fresh(10)
	s.cast_request(Vector2(3.4,-2.5))
	for i in range(4): s.step()
	s.paused = true
	var frozen := [s.tick,s.player,s.mana_raw,s.pending.duplicate(true),s.enemies.duplicate(true),s.history.duplicate(true)]
	for i in range(20): s.step(true,Vector2.ZERO)
	check(frozen == [s.tick,s.player,s.mana_raw,s.pending,s.enemies,s.history],"pause freezes every entity and pending cast")
	s.reset()
	check(s.enemies.size() == 10 and s.pending.is_empty() and s.bolts.is_empty() and s.history.is_empty(),"multi reset clears pending projectiles and log")
	for i in range(30): s.step()
	check(s.shots == 0,"pre-reset cast cannot leak into new entities")

func run() -> void:
	core_checks()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional independent harness failure proof")
	print(JSON.stringify({"scope":"phase2 independent core checks; not crowd performance or original D2R validation","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
