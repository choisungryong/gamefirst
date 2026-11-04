extends SceneTree
# Independent synthetic adversarial fixtures. Never used as the normal-input pilot.
const Run = preload("res://chapter1/core/combat_run.gd")
var checks := 0
var failures: Array[String] = []
var observations: Array[Dictionary] = []

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures.append(label)

func fresh(primary: String = "chapter1.skill.ember") -> RefCounted:
	var r = Run.new()
	r.start(71, primary)
	r.enemies.clear()
	r.events.clear()
	r._next_spawn = 999999
	r._rebuild_grid()
	return r

func context(r: RefCounted, skill: String, effect: Dictionary = {}) -> Dictionary:
	var fx: Dictionary = r.effective_skill(skill).effects if effect.is_empty() else effect.duplicate(true)
	return {"uid":777,"skill_id":skill,"effects":fx,"remaining_hits":int(fx.hit_budget),"hit_ids":[],"evolved":false}

func spawn(r: RefCounted, kind: String, pos: Vector2) -> Dictionary:
	r._spawn(kind,pos)
	r._rebuild_grid()
	return r.enemies[r._enemy_sequence]

func charger_damage(pos: Vector2) -> int:
	var r = fresh()
	var e := spawn(r,"charger",Vector2.ZERO)
	r.hero.position = pos
	e.state = "dash"
	e.state_until = 32
	e.attack_direction = Vector2.RIGHT
	for t in range(1,33):
		r.tick = t
		r._step_enemies()
	return 120*256-int(r.hero.hp_raw)

func fan_damage(pos: Vector2, elite: bool = false) -> int:
	var r = fresh()
	var e := spawn(r,"elite" if elite else "ranged",Vector2.ZERO)
	e.attack_direction = Vector2.RIGHT
	r.hero.position = pos
	r._enemy_projectiles(e)
	for t in range(1,212):
		r.tick = t
		r._step_projectiles()
	return 120*256-int(r.hero.hp_raw)

func _initialize() -> void:
	# Reserve a rank1 shot; legal rank + gear changes affect only future releases.
	var r = fresh()
	var target := spawn(r,"elite",Vector2(10,0))
	target.hp_raw = 10000000
	target.frozen_until = 99999
	r.step()
	var paid: Dictionary = r._contexts.values()[0]
	var paid_before := paid.duplicate(true)
	var due: int = r._next_cast[Run.SKILL_IDS[0]]
	r.growth.award_xp(6)
	r._refresh_mode()
	var offer: Dictionary = r.get_offer()
	var waiting: Dictionary = r.snapshot()
	for i in 300: r.step(Vector2.RIGHT)
	check(r.snapshot() == waiting,"chooser pauses all exposed simulation state for 300 requested steps")
	check(r.choose(offer.token,offer.cards[0].id),"rank change uses an actual offered card")
	var gear: Dictionary = Run.ITEM_TEMPLATES[2].duplicate(true)
	gear.uid = 6001
	r.inventory.append(gear)
	r.open_inventory()
	check(r.equip(6001),"cooldown gear equipped through inventory API")
	r.close_inventory()
	check(paid == paid_before,"rank and cooldown gear do not mutate paid release snapshot")
	check(r._next_cast[Run.SKILL_IDS[0]] == due and due == 73,"rank and cooldown gear do not advance reserved cooldown")
	check(r.effective_skill(Run.SKILL_IDS[0]).effects.projectiles == 3,"future release uses paid rank2 shape")
	while r.tick < 48: r.step()
	check(int(target.hp_raw) == 10000000-3072,"rank1 in-flight shot deals rank1 damage after rank2 choice")
	while r.tick < due: r.step()
	check(r.metrics.casts[Run.SKILL_IDS[0]] == 2,"next shot fires at original reserved due tick")
	check(r._next_cast[Run.SKILL_IDS[0]] == due+61,"next cooldown reserves rank2 plus charm period")
	var exposed: Dictionary = r.effective_skill(Run.SKILL_IDS[0])
	exposed.effects.damage_raw = 1
	check(r.effective_skill(Run.SKILL_IDS[0]).effects.damage_raw == 3584,"effective skill result is detached")

	# Learn all skills with actual cards, then verify exact independent schedules.
	r = fresh()
	r.growth.award_xp(18)
	r._refresh_mode()
	for desired in [Run.SKILL_IDS[1],Run.SKILL_IDS[2]]:
		offer = r.get_offer()
		var picked := false
		for card in offer.cards:
			if card.kind == "unlock" and card.skill_id == desired:
				picked = r.choose(offer.token,card.id)
				break
		check(picked,"legal unlock "+desired)
	target = spawn(r,"elite",Vector2(5,0))
	target.hp_raw = 100000000
	target.frozen_until = 999999
	var cast_ticks := {}
	for id_ in Run.SKILL_IDS: cast_ticks[id_] = []
	for t in 200:
		r.step()
		for e in r.events:
			if e.type == "cast": cast_ticks[e.skill_id].append(e.tick)
	check(cast_ticks[Run.SKILL_IDS[0]] == [1,73,145],"ember independent72 tick schedule")
	check(cast_ticks[Run.SKILL_IDS[1]] == [1,85,169],"frost independent84 tick schedule")
	check(cast_ticks[Run.SKILL_IDS[2]] == [1,91,181],"arc independent90 tick schedule")

	for state in ["windup","recover","dash"]:
		r = fresh()
		var e := spawn(r,"charger",Vector2(0,.3))
		e.state = state
		e.state_until = 30
		e.frozen_until = 11
		e.attack_direction = Vector2.RIGHT
		e.telegraph = {"remaining_ticks":30}
		for t in range(1,11):
			r.tick = t
			r._step_enemies()
		check(e.state_until == 40 and e.position == Vector2(0,.3),"freeze suspends "+state+" deadline and motion")
		r.tick = 11
		r._step_enemies()
		check(e.state == state and r.metrics.enemy_attacks == 0,"thaw preserves unfinished "+state+" state")

	check(charger_damage(Vector2(2,.70)) == 8*256,"charger damages inside displayed swept capsule")
	check(charger_damage(Vector2(2,.712)) == 0,"charger cannot damage outside capsule side")
	check(charger_damage(Vector2(-.712,0)) == 0,"charger cannot damage behind capsule start cap")
	check(charger_damage(Vector2(5.512,0)) == 0,"charger cannot damage beyond capsule end cap")
	check(fan_damage(Vector2(14.0,0)) == 5*256,"ranged central ray reaches inside declared travel")
	check(fan_damage(Vector2(15.15,0)) == 0,"ranged ray cannot damage beyond length plus radius")
	check(fan_damage(Vector2(10,.7)) == 0,"ranged fan gaps outside individual rays remain safe")
	check(fan_damage(Vector2(17,0),true) == 12*256,"elite fan central ray reaches17m")
	check(fan_damage(Vector2(17.95,0),true) == 0,"elite fan cannot damage beyond declared length plus radius")

	# Arc proc and direct branches share one cast budget and one dedup set.
	r = fresh(Run.SKILL_IDS[2])
	var fx: Dictionary = r.effective_skill(Run.SKILL_IDS[2]).effects
	fx.damage_raw = 99999
	fx.death_burst = 1
	fx.proc_depth = 1
	fx.branches = 2
	fx.chain_targets = 7
	fx.hit_budget = 6
	var first := spawn(r,"walker",Vector2(2,0))
	for i in 10: spawn(r,"walker",Vector2(2+float(i)*.2,.3))
	var c := context(r,Run.SKILL_IDS[2],fx)
	r.events.clear()
	r._chain(first,c)
	var ids := {}
	var duplicate := false
	for e in r.events:
		if e.type == "hit":
			if ids.has(e.target_id): duplicate = true
			ids[e.target_id] = true
	check(not duplicate and ids.size() == 6 and c.remaining_hits == 0,"arc death procs and direct branches dedup globally within exact6 budget")
	var kills_before: int = r.kills
	var orb_before: int = r.orbs.size()
	r._damage_enemy(first.id,context(r,Run.SKILL_IDS[2],fx),0)
	check(r.kills == kills_before and r.orbs.size() == orb_before,"dead identity gives no repeat kill or XP even with fresh cast")
	r = fresh(Run.SKILL_IDS[2])
	first = spawn(r,"walker",Vector2.ZERO)
	var far := spawn(r,"walker",Vector2(3.01,0))
	c = context(r,Run.SKILL_IDS[2],fx)
	r.events.clear()
	r._damage_enemy(first.id,c,0)
	check(far.hp_raw > 0,"arc residual pulse excludes3.01m target despite7m chain reach")
	var cues := 0
	for e in r.events:
		if e.type == "explosion":
			cues += 1
			check(e.radius_cm == 300,"arc residual pulse declares actual300cm extent")
	check(cues == 1,"one arc death creates one proc cue")

	# Bounded allocations and generation safeguards, separate from normal pilot.
	r = fresh()
	for i in 450: r._drop_orb(Vector2(10,0),i+1)
	var total := 0
	for orb in r.orbs: total += int(orb.amount)
	check(r.orbs.size() == 400 and total == 450*451/2 and r.metrics.orbs_merged == 50,"XP cap merges amount without loss")
	for i in 1100: r._emit("probe",Vector2.ZERO)
	check(r.events.size() == 1024 and r.metrics.events_dropped == 76,"event capacity sheds only overflow")
	var last := -1
	var ordered := true
	for e in r.events:
		if e.seq <= last: ordered = false
		last = e.seq
	check(ordered,"bounded events preserve monotonic identity")
	first = spawn(r,"walker",Vector2.ZERO)
	first.generation -= 1
	var old_hp: int = first.hp_raw
	r._damage_enemy(first.id,context(r,Run.SKILL_IDS[0]),0)
	check(first.hp_raw == old_hp and r.kills == 0,"stale-generation entity cannot be hit or rewarded")
	var old_id: int = first.id
	r.enemies.erase(old_id)
	var replacement := spawn(r,"walker",Vector2.ZERO)
	check(replacement.id > old_id,"erased entity ID is never recycled within run")
	r._damage_enemy(old_id,context(r,Run.SKILL_IDS[0]),0)
	check(replacement.hp_raw == 12*256,"missing stale ID cannot hit replacement")
	for i in 600: r._spawn("walker",Vector2.ZERO)
	check(r.enemies.size() == 512,"entity allocation hard cap512")
	r.tick = Run.ELITE_TICK
	r._spawn_wave()
	check(not r._elite_spawned,"failed elite allocation does not consume spawn entitlement")
	r.enemies.clear()
	r._spawn_wave()
	check(r._elite_spawned,"elite allocation retries after capacity is available")

	# Counterexample: ground item cap currently blocks even directly-owned elite loot.
	r = fresh()
	for i in Run.MAX_GROUND_ITEMS:
		r.items.append({"uid":1000+i,"position":Vector2(18,18),"drop_tick":0})
	target = spawn(r,"elite",Vector2(10,0))
	fx = r.effective_skill(Run.SKILL_IDS[0]).effects
	fx.damage_raw = 1000000
	r._damage_enemy(target.id,context(r,Run.SKILL_IDS[0],fx),0)
	observations.append({"case":"elite_reward_with_ground_cap","mode":r.mode,"ground_count":r.items.size(),"inventory_count":r.inventory.size(),"picked_items":r.metrics.picked_items,"dropped_items":r.metrics.dropped_items,"expected_if_reward_guaranteed":"elite reward owned despite unrelated ground cap"})
	check(r.mode == "victory" and r.inventory.is_empty(),"confirmed limitation: full ground list suppresses elite reward despite empty inventory")
	print("INDEPENDENT_CORE_RESULT ",JSON.stringify({"checks":checks,"failures":failures,"observations":observations,"scope":"Synthetic adversarial fixtures only; issue observations are recorded separately from harness failures."}))
	quit(0 if failures.is_empty() else 1)
