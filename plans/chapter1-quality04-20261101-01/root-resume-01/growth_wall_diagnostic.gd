extends SceneTree
## Diagnostic normal inputs. No direct writes to HP, XP, entities, items or attack definitions.
const Run = preload("res://chapter1/core/combat_run.gd")
const Before = preload("res://plans/chapter1-quality04-20261101-01/core04/before_combat_run.gd")
var policy := "fixed-normal-driver"
var choices: Array[Dictionary] = []

func move_for(run: RefCounted) -> Vector2:
	var target: Vector2 = Vector2(cos(run.elapsed()*.4),sin(run.elapsed()*.4))*6.5
	var best := 1000000.0
	for orb in run.orbs:
		var d: float = orb.position.distance_squared_to(run.hero.position)
		if d < best:
			best = d
			target = orb.position
	for item in run.items:
		var d: float = item.position.distance_squared_to(run.hero.position)
		if d < minf(best+4.0,100.0): target = item.position
	var move: Vector2 = (target-run.hero.position).normalized()
	var nearest := 1000.0
	var avoidance := Vector2.ZERO
	for e in run.enemies.values():
		if e.hp_raw <= 0: continue
		var delta: Vector2 = run.hero.position-e.position
		var d := delta.length()
		nearest = minf(nearest,d)
		if d < 1.7 and d > .001: avoidance += delta/d*(1.7-d)*1.4
		if e.state == "windup" and e.kind == "charger" and d < 5.8:
			avoidance += Vector2(-e.attack_direction.y,e.attack_direction.x)*1.5
	move = (move+avoidance).limit_length(1.0)
	# Separate diagnostic policy: ordinary movement input must not keep steering
	# outward after the hero reaches the arena wall. No game state is granted.
	if policy == "primary-first-wall-aware":
		var at:Vector2=run.hero.position
		for axis in 2:
			if absf(at[axis])>16.0:
				if signf(move[axis])==signf(at[axis]):move[axis]=0.0
				move[axis]-=signf(at[axis])*.85
		move=move.limit_length(1.0)
	if nearest < 1.35 and move.length_squared() > .1: run.request_dash(move)
	return move

func select_growth(run: RefCounted) -> void:
	var offer: Dictionary = run.get_offer()
	if offer.is_empty(): return
	var selected: Dictionary = offer.cards[0]
	if run.growth.snapshot().ranks.size() < 3:
		for card in offer.cards:
			if card.kind == "unlock":
				selected = card
				break
	if policy.begins_with("primary-first"): selected = offer.cards[0]
	choices.append({"tick":run.tick,"elapsed":run.elapsed(),"xp":run.growth.snapshot().xp,"level":offer.level,"offered":offer.cards,"chosen":selected,"hero_hp_raw":run.hero.hp_raw,"kills":run.kills})
	run.choose(offer.token,selected.id)

func equip_owned(run: RefCounted) -> void:
	if run.inventory.is_empty(): return
	var did_open := false
	for item in run.inventory:
		if run.equipped.has(item.slot): continue
		if not did_open:
			run.open_inventory()
			did_open = true
		run.equip(item.uid)
	if did_open: run.close_inventory()


func exercise(type_: Script, core_id: String, policy_id: String) -> Dictionary:
	policy = policy_id
	choices = []
	var run = type_.new()
	run.start(71,"chapter1.skill.frost")
	var samples: Array[Dictionary] = []
	var casts: Array[Dictionary] = []
	var damage_events: Array[Dictionary] = []
	var pickups: Array[Dictionary] = []
	var frost_hits: Array[Dictionary] = []
	var next_sample := 0
	var calls := 0
	while run.mode not in ["victory","defeat"] and run.tick < 150*60 and calls < 20000:
		calls += 1
		if run.mode == "choice":
			select_growth(run)
			continue
		equip_owned(run)
		run.step(move_for(run))
		for event in run.events:
			if event.type == "hero_hit": damage_events.append(event.duplicate(true))
			if event.type == "xp_pickup": pickups.append(event.duplicate(true))
			if event.type == "hit" and event.skill_id == "chapter1.skill.frost": frost_hits.append(event.duplicate(true))
			if event.type == "cast" and event.skill_id == "chapter1.skill.frost" and casts.size() < 80:
				var near: Array[Dictionary] = []
				for id_ in run._near(run.hero.position,13.0).slice(0,5):
					var e: Dictionary = run.enemies[id_]
					near.append({"id":e.id,"kind":e.kind,"hp_raw":e.hp_raw,"position":e.position,"state":e.state,"distance":e.position.distance_to(run.hero.position)})
				casts.append({"tick":run.tick,"hero_position":run.hero.position,"direction":event.direction,"effects":event.effects,"nearest_after_step":near})
		if run.tick >= next_sample:
			next_sample = run.tick+60
			var orb_value := 0
			var nearest_orb := INF
			for orb in run.orbs:
				orb_value += int(orb.amount)
				nearest_orb = minf(nearest_orb,orb.position.distance_to(run.hero.position))
			var nearby := 0
			for e in run.enemies.values():
				if e.hp_raw > 0 and e.position.distance_to(run.hero.position) < 2: nearby += 1
			var g: Dictionary = run.growth.snapshot()
			samples.append({"tick":run.tick,"elapsed":run.elapsed(),"hp_raw":run.hero.hp_raw,"position":run.hero.position,"kills":run.kills,"level":g.level,"xp":g.xp,"ranks":g.ranks,"evolved":g.evolved,"orbs":run.orbs.size(),"orb_value":orb_value,"nearest_orb_m":nearest_orb if nearest_orb < INF else -1,"nearby_enemies2m":nearby,"alive":run.alive_count(),"inventory":run.inventory.size(),"metrics":run.metrics.duplicate(true)})
	var s: Dictionary = run.snapshot()
	return {"core_id":core_id,"driver_policy":policy,"seed":71,"primary":"chapter1.skill.frost","mode":run.mode,"elapsed":run.elapsed(),"kills":run.kills,"hp_raw":run.hero.hp_raw,"growth":s.growth,"metrics":s.metrics,"inventory_count":run.inventory.size(),"choices":choices.duplicate(true),"samples":samples,"frost_casts":casts,"frost_hits":frost_hits,"hero_damage_events":damage_events,"xp_pickups":pickups,"remaining_orbs":s.orbs,"scope":"Normal movement dash growth choice equip only. Explicit policy comparison; no injected game resources. No quality/GPU/player approval."}

func _initialize() -> void:
	var path := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output="): path = arg.trim_prefix("--output=")
	if path.is_empty() or FileAccess.file_exists(path):
		push_error("Missing fresh output path")
		quit(2)
		return
	var results: Array[Dictionary] = []
	for core in ["core03","core04"]:
		for driver in ["fixed-normal-driver","primary-first-normal-choices","primary-first-wall-aware"]:
			var row := exercise(Before if core == "core03" else Run,core,driver)
			results.append(row)
			print("CORE04_GROWTH_DIAGNOSTIC_CASE ",JSON.stringify({"core":core,"policy":driver,"mode":row.mode,"elapsed":row.elapsed,"kills":row.kills,"level":row.growth.level,"xp":row.growth.xp,"frost_rank":row.growth.ranks.get("chapter1.skill.frost",0)}))
	var file := FileAccess.open(path,FileAccess.WRITE)
	if file == null:
		push_error("Cannot create report")
		quit(2)
		return
	file.store_string(JSON.stringify({"cases":results,"scope":"Diagnostic outcomes retained regardless of victory. Engine exit0 means four cases completed; individual defeat remains defeat."},"\t"))
	quit(0)
