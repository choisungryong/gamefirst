extends SceneTree
## Synthetic geometry/state fixtures. These never claim normal gameplay or GPU quality.
const Run = preload("res://chapter1/core/combat_run.gd")
const Before = preload("res://plans/chapter1-quality04-20261101-01/core04/before_combat_run.gd")
var checks := 0
var failures: Array[String] = []
var comparisons: Array[Dictionary] = []

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures.append(label)

func sandbox(type_: Script = Run) -> RefCounted:
	var run = type_.new()
	run.start(71)
	run.enemies.clear()
	run._enemy_sequence = 0
	run.events.clear()
	run._next_spawn = 1000000
	return run

func geometry(run: RefCounted) -> Dictionary:
	var penetration := 0.0
	var overlaps := 0
	var inside_hero := 0
	var ids: Array = run.enemies.keys()
	for i in ids.size():
		var a: Dictionary = run.enemies[ids[i]]
		if a.position.distance_to(run.hero.position) < float(a.radius)+.28-.001: inside_hero += 1
		for j in range(i+1,ids.size()):
			var b: Dictionary = run.enemies[ids[j]]
			var amount: float = float(a.radius)+float(b.radius)-a.position.distance_to(b.position)
			if amount > .001:
				overlaps += 1
				penetration += amount
	return {"overlap_pairs":overlaps,"summed_penetration_m":penetration,"inside_hero":inside_hero}

func scenario(type_: Script, name_: String) -> Dictionary:
	var run = sandbox(type_)
	if name_ == "corner": run.hero.position = Vector2(19,19)
	var count := 48 if name_ == "ring" else 32
	for i in count:
		var p := Vector2.ZERO
		if name_ == "ring": p = Vector2.from_angle(TAU*float(i)/count)*3.2
		elif name_ == "funnel": p = Vector2(float(i%4)*.08-.12,-2.0-float(i/4)*.08)
		elif name_ == "coincident": p = Vector2(0,-2)
		else: p = Vector2(17.8+float(i%4)*.06,17.8+float(i/4)*.06)
		run._spawn("walker",p)
	var initial := geometry(run)
	var bounded := true
	var max_step := 0.0
	var max_checks_per_step := 0
	var rng_before: Array = [run._spawn_rng.state,run._loot_rng.state]
	var sum_penetration := 0.0
	var sum_inside_hero := 0
	for step in 240:
		var positions: Dictionary = {}
		for id_ in run.enemies: positions[id_] = run.enemies[id_].position
		var checks_before: int = int(run.metrics.get("crowd_neighbor_checks",0))
		run.tick += 1
		run._step_enemies()
		max_checks_per_step = maxi(max_checks_per_step,int(run.metrics.get("crowd_neighbor_checks",0))-checks_before)
		for id_ in run.enemies:
			var p: Vector2 = run.enemies[id_].position
			bounded = bounded and p.is_finite() and absf(p.x) <= 19.00001 and absf(p.y) <= 19.00001
			max_step = maxf(max_step,p.distance_to(positions[id_]))
		var g := geometry(run)
		sum_penetration += float(g.summed_penetration_m)
		sum_inside_hero += int(g.inside_hero)
	return {"scenario":name_,"initial":initial,"final":geometry(run),"penetration_tick_sum":sum_penetration,"hero_inside_tick_sum":sum_inside_hero,"all_positions_bounded":bounded,"max_step_m":max_step,"max_neighbor_checks_per_step":max_checks_per_step,"rng_unchanged":rng_before==[run._spawn_rng.state,run._loot_rng.state],"hp_raw":run.hero.hp_raw,"kills":run.kills,"xp":run.growth.snapshot().xp,"inventory":run.inventory.size()}

func _initialize() -> void:
	for name_ in ["ring","funnel","coincident","corner"]:
		var old := scenario(Before,name_)
		var now := scenario(Run,name_)
		comparisons.append({"scenario":name_,"before_core03":old,"after_core04":now})
		check(now.all_positions_bounded,name_+": positions finite and within19m")
		check(now.max_step_m <= 1.6/60.0+.045+.00001,name_+": crowd correction respects displacement bound")
		check(now.max_neighbor_checks_per_step <= 48*32,name_+": grid work bounded at32 bodies per approach")
		check(now.rng_unchanged,name_+": steering consumes no spawn or loot RNG")
		check(now.kills == 0 and now.xp == 0 and now.inventory == 0,name_+": movement grants no kills XP or gear")
		check(now.hp_raw <= 120*256,name_+": movement cannot grant hero HP")
		check(now.penetration_tick_sum < old.penetration_tick_sum*.8,name_+": measured cumulative overlap reduced at least20pct")
		check(now.hero_inside_tick_sum <= old.hero_inside_tick_sum,name_+": hero overlap does not increase")
		if name_ == "corner": check(now.hp_raw < 120*256,"compressed corner queue still permits real telegraphed attacks")
	var inside = sandbox()
	inside._spawn("walker",Vector2(0,-.5))
	inside._step_enemies()
	check(inside.enemies[1].state == "move" and inside.enemies[1].telegraph.is_empty(),"inside clearance queues without creating unpaid windup")
	check(inside.enemies[1].position.y < -.5 and inside.enemies[1].position.y >= -.5-.045-.00001,"inside clearance moves outward gradually")
	for i in 12:
		inside.tick += 1
		inside._step_enemies()
	check(inside.enemies[1].state == "windup" and inside.enemies[1].position.length() >= .685,"inside clearance eventually finds legal melee stance")
	var single = sandbox()
	single._spawn("walker",Vector2(0,-.75))
	single._step_enemies()
	check(single.enemies[1].state == "windup" and single.enemies[1].telegraph.radius == 1.15,"legal melee stance starts actual windup")
	var anchor: Vector2 = single.enemies[1].position
	var attack_direction: Vector2 = single.enemies[1].attack_direction
	for i in 12: single._spawn("walker",anchor+Vector2(.01,0))
	for i in 10:
		single.tick += 1
		single._step_enemies()
	check(single.enemies[1].position == anchor and single.enemies[1].attack_direction == attack_direction,"crowd cannot drift paid windup origin or direction")
	var protected_stance := true
	for id_ in single.enemies:
		if id_ == 1: continue
		var e: Dictionary = single.enemies[id_]
		if e.state == "windup" and e.position.distance_to(anchor) < .6*.92: protected_stance = false
	check(protected_stance,"queued bodies cannot claim overlapping paid windup anchor")
	check(single.enemies[1].telegraph.remaining_ticks == 15,"windup countdown remains attached to original deadline")
	single.enemies[1].frozen_until = 20
	var deadline: int = single.enemies[1].state_until
	for i in 9:
		single.tick += 1
		single._step_enemies()
	check(single.enemies[1].position == anchor and single.enemies[1].state_until == deadline+9,"freeze anchors and preserves full unspent windup time")
	single.tick = int(single.enemies[1].state_until)
	single._step_enemies()
	check(single.enemies[1].state == "recover" and single.enemies[1].position == anchor,"actual windup expiry enters anchored recovery")
	for i in 10:
		single.tick += 1
		single._step_enemies()
	check(single.enemies[1].position == anchor,"recovery cannot be pushed by queued bodies")
	var charge = sandbox()
	charge._spawn("charger",Vector2(0,-4))
	charge._step_enemies()
	var charge_origin: Vector2 = charge.enemies[1].position
	charge.tick = charge.enemies[1].state_until
	charge._step_enemies()
	for i in 12: charge._spawn("walker",charge_origin)
	var charge_direction: Vector2 = charge.enemies[1].attack_direction
	charge.tick += 1
	charge._step_enemies()
	check(charge.enemies[1].position.is_equal_approx(charge_origin+charge_direction*9.0/60.0),"active dash follows paid trajectory despite coincident peers")
	var a = sandbox()
	for i in 100: a._spawn("walker",Vector2(0,-2))
	var b = sandbox()
	b.enemies = a.enemies.duplicate(true)
	var keys: Array = b.enemies.keys()
	keys.reverse()
	var reverse: Dictionary = {}
	for id_ in keys: reverse[id_] = b.enemies[id_]
	b.enemies = reverse
	for i in 10:
		a.tick += 1
		b.tick += 1
		a._step_enemies()
		b._step_enemies()
	var same := true
	for id_ in a.enemies:
		if a.enemies[id_] != b.enemies[id_]: same = false
	check(same,"explicit UID order makes crowd state independent of Dictionary insertion order")
	check(a.metrics.crowd_peak_neighbors <= 32 and b.metrics.crowd_peak_neighbors <= 32,"pathological100 coincident bodies cannot exceed32 neighbor checks")
	check(a._enemy_sequence == 100 and a.enemies.size() == 100,"steering preserves unique identity and entity count")
	var modal = sandbox()
	modal._spawn("walker",Vector2(0,-.5))
	modal.set_paused(true)
	var before: Dictionary = modal.snapshot()
	modal.step(Vector2.RIGHT)
	check(modal.snapshot() == before,"paused step cannot perform crowd correction or alter metrics")
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional crowd harness failure")
	print("CORE04_CROWD_RESULT ",JSON.stringify({"checks":checks,"failures":failures,"comparisons":comparisons,"scope":"synthetic geometry and state fixtures; no normal-play or GPU quality approval"}))
	quit(0 if failures.is_empty() else 1)
