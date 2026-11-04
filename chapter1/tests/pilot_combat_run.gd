extends SceneTree
## Normal-rule automatic input pilot. It never changes HP, spawns, items, XP or definitions.
## Actual user play, final visual quality and GPU performance remain separate checks.
const Run = preload("res://chapter1/core/combat_run.gd")
var results: Array[Dictionary] = []

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

func exercise(primary: String, seed_: int) -> Dictionary:
	var run = Run.new()
	if not run.start(seed_,primary): return {"primary":primary,"seed":seed_,"error":run.errors}
	var samples: Array[Dictionary] = []
	var next_sample := 0
	var calls := 0
	var begin := Time.get_ticks_usec()
	while run.mode not in ["victory","defeat"] and run.tick < 150*60 and calls < 20000:
		calls += 1
		if run.mode == "choice":
			select_growth(run)
			continue
		equip_owned(run)
		run.step(move_for(run))
		if run.tick >= next_sample:
			next_sample = run.tick+300
			var state: Dictionary = run.growth.snapshot()
			samples.append({"tick":run.tick,"kills":run.kills,"alive":run.alive_count(),"hp_raw":run.hero.hp_raw,"position":[run.hero.position.x,run.hero.position.y],"level":state.level,"xp":state.xp,"ranks":state.ranks,"evolved":state.evolved,"equipped":run.equipped.duplicate()})
	var elapsed_cpu: int = Time.get_ticks_usec()-begin
	var state: Dictionary = run.snapshot()
	return {"primary":primary,"seed":seed_,"mode":run.mode,"tick":run.tick,"elapsed":run.elapsed(),"kills":run.kills,"hp_raw":run.hero.hp_raw,
		"growth":state.growth,"inventory_count":run.inventory.size(),"equipped":state.equipped,"elite_spawned":state.elite_spawned,"elite_killed":state.elite_killed,
		"metrics":state.metrics,"samples":samples,"cpu_wall_us":elapsed_cpu,"scope":"Normal movement/dash/choice/equip inputs; no invulnerability, pre-awarded XP, item gifts or forced kills. Automatic pilot is not actual user play or GPU QA."}

func _initialize() -> void:
	var path := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--output="): path = arg.trim_prefix("--output=")
	if not path.is_empty() and FileAccess.file_exists(path):
		push_error("Refusing to overwrite existing pilot evidence: "+path)
		quit(1)
		return
	for primary in Run.SKILL_IDS:
		for seed_ in [71,907]: results.append(exercise(primary,seed_))
	var passed := true
	for row in results:
		if row.get("mode","") != "victory": passed = false
	var report := {"success":passed,"cases":results,"scope":"C2 core normal-rule pilot only. Does not approve art, sound, fun, whole chapter or GPU performance."}
	if not path.is_empty():
		var file := FileAccess.open(path,FileAccess.WRITE)
		if file == null:
			push_error("Cannot write requested pilot evidence "+path)
			quit(1)
			return
		file.store_string(JSON.stringify(report,"\t"))
	var summary: Array[Dictionary] = []
	for row in results: summary.append({"primary":row.primary,"seed":row.seed,"mode":row.get("mode","error"),"elapsed":row.get("elapsed",0),"kills":row.get("kills",0),"max_alive":row.get("metrics",{}).get("max_alive",0),"equipped":row.get("equipped",{})})
	print("CHAPTER1_NORMAL_PILOT ",JSON.stringify({"success":passed,"cases":summary,"evidence":path}))
	quit(0 if passed else 1)
