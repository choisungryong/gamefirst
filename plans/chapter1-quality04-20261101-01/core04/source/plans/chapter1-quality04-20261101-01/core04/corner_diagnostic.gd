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
	var run = sandbox()
	run.hero.position = Vector2(19,19)
	for i in 32: run._spawn("walker",Vector2(17.8+float(i%4)*.06,17.8+float(i/4)*.06))
	var samples: Array = []
	for i in 1200:
		run.tick += 1
		run._step_enemies()
		if i % 120 == 119:
			var nearest: Array = []
			for e in run.enemies.values(): nearest.append({"id":e.id,"distance":e.position.distance_to(run.hero.position),"state":e.state,"position":[e.position.x,e.position.y]})
			nearest.sort_custom(func(a,b): return a.distance < b.distance)
			samples.append({"tick":run.tick,"hp_raw":run.hero.hp_raw,"nearest":nearest.slice(0,6),"geometry":geometry(run)})
	print("CORE04_CORNER_DIAGNOSTIC ",JSON.stringify(samples))
	check(run.hero.hp_raw < 120*256 and run.metrics.enemy_attacks > 0,"corner queue eventually allows real telegraphed melee attacks")
	print("CORE04_CORNER_CHECK ",JSON.stringify({"checks":checks,"failures":failures}))
	quit(0 if failures.is_empty() else 1)
