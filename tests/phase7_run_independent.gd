extends SceneTree
## Independent expedition contract checks. Synthetic boundary fixtures are explicit.
const Run = preload("res://run/expedition_controller.gd")
const Sim = preload("res://baseline_sim.gd")
var checks := 0
var failures: Array[String] = []
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("PHASE7 RUN FAILED: "+message)
func fresh() -> RefCounted:
	var r = Run.new()
	r.sim.enemy_ai = false
	return r
func committed(r: RefCounted) -> Dictionary:
	return {"run":r.snapshot(),"profile":r.sim.progress_document(),"life":r.sim.life,"mana":r.sim.mana_raw,"sim_tick":r.sim.tick,"damage_rng":str(r.sim.rng.state),"spawn_rng":str(r.spawn_rng.state),"pending":r.sim.pending_context_snapshot(),"enemies":r.sim.enemies.duplicate(true),"history":r.history_snapshot(),"remainder":r._mana_remainder,"epoch":r.sim._loot_epoch}
func death(r: RefCounted, identity: Dictionary = {}) -> Dictionary:
	var h: Dictionary = identity if not identity.is_empty() else r.sim.spawn_enemy(Vector2(7,-5))
	var target: Dictionary = r.sim.entity(h)
	if target.is_empty(): return {}
	target.life_raw = 1
	var context: Dictionary = r.sim._make_context("skill.ember_bolt")
	context["shot"] = 1
	r.sim._apply_damage(target,context,target.p)
	return h

func clocks_and_resources() -> void:
	var r = fresh()
	check(r.state == "ready" and r.sim.paused and r.elapsed_ticks == 0,"menu starts with combat frozen")
	var before: Dictionary = committed(r)
	for i in range(120): r.step(true,Vector2.RIGHT)
	check(committed(r) == before,"menu ticks cannot progress combat/RNG/resources")
	check(r.start(73001) and r.state == "active" and not r.sim.paused,"start begins active expedition")
	check(r.sim.alive_count() == 1,"start produces one initial normal enemy")
	for e in r.sim.enemies.values():
		check(e.p.distance_to(r.sim.player) >= 5 and absf(e.p.x) <= 8 and absf(e.p.y) <= 6,"arrival spawn respects distance and arena bounds")
	r.sim.mana_raw = 0
	r.sim.life = 17
	for i in range(60): r.step()
	check(r.elapsed_ticks == 60 and r.sim.tick == 60 and r.sim.mana_raw == 768 and r._mana_remainder == 0,"60 active ticks restore exact768raw mana")
	check(r.sim.life == 17,"run resource regeneration cannot heal HP")
	r.sim.mana_raw = r.sim.mana_max_raw-1
	r.step()
	check(r.sim.mana_raw == r.sim.mana_max_raw,"run regen clamps to actual maximum")
	r.set_paused(true)
	before = committed(r)
	for i in range(300): r.step(true,Vector2.RIGHT)
	check(committed(r) == before and r.sim.paused,"pause freezes all clocks/resources/spawn/damage RNG")
	r.set_paused(false)
	r.sim.paused = true
	before = committed(r)
	r.step()
	check(committed(r) == before,"equipment modal sim pause also freezes controller clock")
	r.sim.paused = false
	for pair in [[0,"arrival",8],[899,"arrival",8],[900,"awakening",8],[3599,"awakening",8],[3600,"pressure",16],[8999,"pressure",16],[9000,"warning",12],[10799,"warning",12],[10800,"elite",20],[14399,"elite",20],[14400,"finale",20]]:
		r.elapsed_ticks = pair[0]
		check(r.phase() == pair[1] and r.alive_cap() == pair[2],"phase/cap boundary "+str(pair[0]))
	var base = Sim.new()
	base.reset(0)
	base.mana_raw = 0
	for i in range(120): base.step()
	check(base.mana_raw == 0,"baseline mode remains zero-regeneration")

func schedules_and_rng() -> void:
	var a = fresh()
	var b = fresh()
	a.start(891)
	b.start(891)
	for tick_value in [900,1260,1620,3600,3840,4080,9000,9360,10800]:
		for e in a.sim.enemies.values(): a.sim.despawn_enemy(a.sim.handle(e))
		for e in b.sim.enemies.values(): b.sim.despawn_enemy(b.sim.handle(e))
		for i in range(3): b.sim.rng.randi()
		a.elapsed_ticks = tick_value-1
		b.elapsed_ticks = tick_value-1
		a.step()
		b.step()
		var positions_a: Array = []
		var positions_b: Array = []
		for e in a.sim.enemies.values(): positions_a.append(e.p)
		for e in b.sim.enemies.values(): positions_b.append(e.p)
		check(positions_a == positions_b and a.spawn_rng.state == b.spawn_rng.state,"spawn stream reproducible independent of damage RNG tick "+str(tick_value))
		check(a.sim.loot_rng.state == b.sim.loot_rng.state and a.sim.equipment_snapshot() == b.sim.equipment_snapshot(),"scheduling consumes no loot/item randomness tick "+str(tick_value))
		for e in a.sim.enemies.values(): check(e.p.distance_to(a.sim.player) >= 5 and absf(e.p.x) <= 8 and absf(e.p.y) <= 6,"scheduled spawn in bounds and remote")
	check(a.elite_reserved and a.elite_spawned and not a.elite_identity.is_empty(),"180s schedules one elite")
	check(a.sim.entity(a.elite_identity).max_raw == 54*256,"elite uses specified54HP")
	var elite: Dictionary = a.elite_identity.duplicate(true)
	for i in range(20): a.step()
	check(a.elite_identity == elite,"elite identity stays one-shot across subsequent ticks")
	var r = fresh()
	r.start()
	r.backlog.clear()
	for i in range(20): r._enqueue("normal")
	check(r.backlog.size() == 8 and r.dropped_requests == 12,"FIFO backlog bounded8 and excess counted")
	while r.sim.alive_count() < 20: r.sim.spawn_enemy(Vector2(7,-5))
	r.elapsed_ticks = 10800-1
	r.step()
	check(r.elite_reserved and not r.elite_spawned and r.backlog.size() <= 8,"elite reservation survives full backlog and alive cap")
	for i in range(20):
		if r.elite_spawned: break
		var id_: Variant = r.sim.enemies.keys()[0]
		r.sim.despawn_enemy(r.sim.handle(r.sim.enemies[id_]))
		r.step()
	check(r.elite_spawned and r.sim.alive_count() <= 20,"deferred elite eventually spawns once when capacity opens")
	var count := 0
	for e in r.history_snapshot():
		if e.kind == "run_spawned" and e.elite: count += 1
	check(count == 1,"deferred elite creates exactly one spawn event")
	# No feasible coordinate: bounded attempts, normal request discarded, elite retained.
	r = fresh()
	r.start()
	for e in r.sim.enemies.values(): r.sim.despawn_enemy(r.sim.handle(e))
	r.sim.player = Vector2(1000,1000)
	r.sim.move_target = r.sim.player
	r.backlog.clear()
	r._enqueue("normal")
	r._drain_backlog()
	check(r.backlog.is_empty() and r.failed_positions == 1,"infeasible normal spawn is bounded and counted")
	r._enqueue("elite")
	r._drain_backlog()
	check(r.backlog.size() == 1 and r.failed_positions == 2,"infeasible elite stays reserved after bounded attempts")

func ending_cases() -> void:
	for specification in [[14398,true,40.0,"active"],[14399,true,40.0,"victory"],[17999,false,40.0,"timeout"],[17999,true,40.0,"victory"],[17999,true,0.0,"defeat"],[14399,true,0.0,"defeat"]]:
		var r = fresh()
		r.start(173)
		r.elapsed_ticks = specification[0]
		r.elite_spawned = true
		r.elite_defeated = specification[1]
		r.sim.life = specification[2]
		r.step()
		check(r.state == specification[3],"same-tick outcome priority "+str(specification))
		if r.state == "active": continue
		var ends := 0
		for e in r.history_snapshot():
			if e.kind == "run_ended": ends += 1
		check(ends == 1 and r.sim.paused,"terminal state emits once and freezes combat")
		var before: Dictionary = committed(r)
		for i in range(120): r.step(true,Vector2.RIGHT)
		check(committed(r) == before,"terminal clocks/RNG/rewards/resources stay frozen")
		check(r.snapshot().summary.outcome == r.state and r.snapshot().summary.seed == 173,"terminal summary carries authoritative result/seed")
	var r = fresh()
	r.start()
	r.sim.enemy_ai = false
	for i in range(18000): r.step()
	check(r.elapsed_ticks == 18000 and r.state == "timeout","full18000tick expedition reaches real300s timeout")
	check(r.backlog.size() <= 8 and r.history_snapshot().size() <= 256 and r.sim.alive_count() <= 20,"full run respects backlog/history/alive bounds")

func profiles_pending_and_restart() -> void:
	var r = fresh()
	r.start()
	death(r)
	death(r)
	check(r.sim.progression_snapshot().xp == 6,"run uses existing one-death reward path")
	var doc: Dictionary = r.sim.progress_document()
	r.sim.life = 11
	r.sim.mana_raw = 333
	for i in range(80): r.step()
	r.sim.life = 11
	r.sim.mana_raw = 333
	check(r.replace_profile_document(doc) and r.elapsed_ticks == 0 and r.state == "active" and r.sim.tick == 0,"profile load starts fresh expedition clock")
	check(r.sim.life == 11 and r.sim.mana_raw == 333 and r.sim.progression_snapshot().xp == 6,"profile load does not add implicit second reset recovery")
	var before: Dictionary = committed(r)
	check(not r.replace_profile_document({}) and committed(r) == before,"failed profile leaves controller and sim fully unchanged")
	var items: Dictionary = r.sim.equipment_snapshot()
	check(r.restart() and r.elapsed_ticks == 0 and r.sim.life == 40 and r.sim.mana_raw == 8960,"explicit restart intentionally restores baseline maxima")
	check(r.sim.equipment_snapshot() == items and r.sim.progression_snapshot().xp == 6,"restart keeps metaXP/inventory/UID/itemRNG")
	r.sim.player = Vector2.ZERO
	r.sim.move_target = Vector2.ZERO
	var target: Dictionary = r.sim.spawn_enemy(Vector2(1,0))
	r.sim.entity(target).life_raw = 100000
	check(r.sim.equip_item(1),"paid cast fixture equips focus")
	r.step(true,Vector2.RIGHT,"skill.ember_bolt")
	var pending: Dictionary = r.sim.pending_context_snapshot()
	var paid_mana: int = r.sim.mana_raw
	check(not pending.is_empty() and pending.bonus_level == 1,"run request preserves authoritative paid snapshot")
	r.set_paused(true)
	for i in range(20): r.step(true,Vector2.RIGHT)
	check(r.sim.pending_context_snapshot() == pending and r.sim.mana_raw == paid_mana,"pause preserves paid pending and mana exactly")
	r.sim.unequip_item("focus")
	r.set_paused(false)
	for i in range(18): r.step()
	check(r.sim.shots == 1 and r.sim.combat_trace.size() == 1 and r.sim.combat_trace[0].base_raw >= 1024,"release uses paid level despite live unequip")
	r.return_to_menu()
	before = committed(r)
	for i in range(30): r.step()
	check(r.state == "ready" and r.sim.paused and committed(r) == before,"return-to-menu freezes gameplay")

func run() -> void:
	clocks_and_resources()
	schedules_and_rng()
	ending_cases()
	profiles_pending_and_restart()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional phase7 run harness failure proof")
	print(JSON.stringify({"scope":"Independent pure expedition tick/controller contracts; synthetic boundaries explicit; no GPU/OS/fun claim","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
