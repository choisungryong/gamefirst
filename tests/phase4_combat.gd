extends SceneTree
## Independent scenario tests: expectations use hand-set geometry and integer
## stages, never call the product target sort or Resolver to produce expected data.
const Sim = preload("res://baseline_sim.gd")
const InputPolicy = preload("res://presentation/input_controller.gd")
var checks := 0
var failures: Array[String] = []

func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("PHASE4 COMBAT FAILED: "+message)

func fresh() -> RefCounted:
	var s = Sim.new()
	s.reset(0)
	s.enemy_ai = false
	s.player = Vector2.ZERO
	s.move_target = Vector2.ZERO
	return s

func spawn(s: RefCounted, p: Vector2, hp: int = 100000) -> Dictionary:
	var h: Dictionary = s.spawn_enemy(p)
	s.entity(h).life_raw = hp
	s.entity(h).max_raw = hp
	return h

func modifier(id_: String, stat: String, amount: int) -> Dictionary:
	return {"source_id":"test","id":id_,"stat_id":stat,"operation":"add","value":amount}

func cast(s: RefCounted, skill: String, aim: Vector2 = Vector2.RIGHT) -> Array:
	var trace: Array = []
	var ticks: int = int(s.skill_display(skill).startup_ticks)
	for index in range(ticks+1):
		s.step(index == 0,aim,skill)
		trace.append_array(s.events.duplicate(true))
	return trace

func hits(trace: Array) -> Array:
	return trace.filter(func(e): return e.kind == "hit")

func instant_targets() -> void:
	var s = fresh()
	var dead: Dictionary = spawn(s,Vector2(.1,0))
	s.entity(dead).state = "dead"
	s.entity(dead).corpse_until = 9999
	var a: Dictionary = spawn(s,Vector2(2,0))
	var b: Dictionary = spawn(s,Vector2(-2,0))
	var c: Dictionary = spawn(s,Vector2(4,0))
	spawn(s,Vector2(4.0001,0))
	var result: Array = hits(cast(s,"skill.frost_pulse"))
	check(result.map(func(e): return e.entity.id) == [a.id,b.id,c.id],"area exact radius, dead exclusion, distance and equal-ID order")
	check(result.size() == 3 and s.statuses.size() == 3,"area hits and chills each living target once")
	var s2 = fresh()
	var farther: Dictionary = spawn(s2,Vector2(2.000001,0))
	var nearer: Dictionary = spawn(s2,Vector2(2,0))
	var near_hits: Array = hits(cast(s2,"skill.frost_pulse"))
	check(near_hits[0].entity == nearer and near_hits[1].entity == farther,"new area distinct close distances retain exact nearest order")
	var cap = fresh()
	for i in range(16): spawn(cap,Vector2(.2+float(i)*.1,0))
	check(hits(cast(cap,"skill.frost_pulse")).size() == 12,"area max12 applies before excess targets")
	var chain = fresh()
	var first: Dictionary = spawn(chain,Vector2(8,0))
	spawn(chain,Vector2(8.01,0))
	var second: Dictionary = spawn(chain,Vector2(5,0))
	var third: Dictionary = spawn(chain,Vector2(2,0))
	var fourth: Dictionary = spawn(chain,Vector2(-1,0))
	spawn(chain,Vector2(-4,0))
	var chain_hits: Array = hits(cast(chain,"skill.arc_chain",Vector2(20,0)))
	check(chain_hits.map(func(e): return e.entity.id) == [first.id,second.id,third.id,fourth.id],"chain aims first then exact jumps, max4, excludes caster-range overflow")
	var unique: Dictionary = {}
	for event in chain_hits: unique[event.entity.id] = true
	check(unique.size() == chain_hits.size(),"chain never revisits target")
	var tie = fresh()
	var lower: Dictionary = spawn(tie,Vector2(4,1))
	var upper: Dictionary = spawn(tie,Vector2(4,-1))
	check(hits(cast(tie,"skill.arc_chain",Vector2.RIGHT))[0].entity == lower,"chain first aim equal-distance tie uses smaller ID")
	check(lower.id < upper.id,"tie fixture IDs ordered")

func pending_snapshot() -> void:
	var s = fresh()
	var target: Dictionary = spawn(s,Vector2(1,0))
	check(s.replace_player_modifiers([modifier("power","stat.spell_power",5000),modifier("cost","stat.mana_cost",2500),modifier("speed","stat.cast_speed",10000)]),"attacker modifiers accepted")
	s.step(true,Vector2.RIGHT,"skill.frost_pulse")
	check(s.mana_raw == 8960-1280 and s.pending.release == 10 and s.next_cast_tick == 39,"committed cost and ceil timing use request modifiers")
	var committed: Dictionary = s.pending_context_snapshot()
	check(committed.skill_id == "skill.frost_pulse" and committed.power_bps == 5000,"pending has committed identity and power")
	committed.power_bps = -10000
	check(s.pending_context_snapshot().power_bps == 5000,"pending context getter isolated")
	check(s.select_skill("skill.arc_chain") and s.replace_player_modifiers([]),"selection and stats can change during paid startup")
	check(s.replace_enemy_modifiers(target,[modifier("res","stat.resist.cold",2500),modifier("flat","stat.flat_reduction",256)]),"impact defenses changed after request")
	var hit_events: Array = []
	for i in range(9):
		s.step()
		hit_events.append_array(hits(s.events))
	check(hit_events.size() == 1 and hit_events[0].skill_id == "skill.frost_pulse" and s.bolts.is_empty(),"paid pending cannot morph into newly selected chain")
	var detail: Dictionary = s.combat_trace.back()
	@warning_ignore("integer_division")
	var powered: int = int(detail.base_raw)*15000/10000
	@warning_ignore("integer_division")
	var expected: int = maxi(0,powered-256)*7500/10000
	check(detail.power_bps == 5000 and detail.flat_reduction_raw == 256 and detail.resistance_bps == 2500 and detail.total_raw == expected,"committed attacker then current defender exact raw stages")
	check(s.mana_raw == 7680 and s.next_cast_tick == 39,"release never repays or recomputes committed cooldown")
	var shortage = fresh()
	shortage.mana_raw = 1023
	shortage.step(true,Vector2.RIGHT,"skill.frost_pulse")
	check(shortage.pending.is_empty() and shortage.mana_raw == 1023 and shortage.events.size() == 1 and shortage.events[0].kind == "no_mana","new skill shortage is atomic")
	var frozen = fresh()
	frozen.step(true,Vector2.RIGHT,"skill.arc_chain")
	frozen.paused = true
	var before: Dictionary = frozen.pending.duplicate(true)
	for i in range(100): frozen.step(true,Vector2.RIGHT,"skill.frost_pulse")
	check(frozen.tick == 1 and frozen.pending == before and frozen.shots == 0,"pause freezes pending logical clock and no duplicate charge")
	frozen.paused = false
	for i in range(12): frozen.step()
	check(frozen.shots == 1 and frozen.pending.is_empty(),"paused paid cast releases once after resume")

func statuses_lifecycle() -> void:
	var s = fresh()
	var h: Dictionary = spawn(s,Vector2(3,0))
	cast(s,"skill.frost_pulse")
	var state: Dictionary = s.status_snapshot(h)
	check(state.kind == "chill" and state.slow_bps == 4000 and state.until_tick == s.tick+120,"chill declared exact duration and strength")
	var end: int = int(state.until_tick)
	state.slow_bps = 9999
	check(s.status_snapshot(h).slow_bps == 4000,"status getter isolates dictionary")
	s.tick = end-1
	s.paused = true
	s.step()
	check(not s.status_snapshot(h).is_empty(),"paused status does not expire")
	s.paused = false
	s.step()
	check(s.tick == end and s.status_snapshot(h).is_empty() and s.events[0].kind == "status_expired","status expires at exact logical tick")
	var slowed = fresh()
	var sh: Dictionary = spawn(slowed,Vector2(3,0))
	cast(slowed,"skill.frost_pulse")
	slowed.entity(sh).state = "approach"
	slowed.entity(sh).timer = 0
	slowed.enemy_ai = true
	var x: float = slowed.entity(sh).p.x
	slowed.step()
	check(is_equal_approx(x-slowed.entity(sh).p.x,1.05/60.0*.6),"chill speed authority in core")
	slowed.enemy_ai = false
	slowed.tick = slowed.next_cast_tick
	slowed.mana_raw = 8960
	var prior: int = int(slowed.status_snapshot(sh).until_tick)
	cast(slowed,"skill.frost_pulse")
	check(slowed.statuses.size() == 1 and slowed.status_snapshot(sh).until_tick > prior,"reapply refreshes single status instead of stacking duplicates")
	check(slowed.replace_enemy_modifiers(sh,[modifier("def","stat.resist.cold",5000)]),"per-target defense accepted")
	var defense_before: Dictionary = slowed.enemy_stats_snapshot(sh)
	check(not slowed.replace_enemy_modifiers(sh,[modifier("hp","stat.health",256)]) and slowed.enemy_stats_snapshot(sh) == defense_before,"enemy unsupported health modifier rejected atomically")
	check(not slowed.replace_enemy_modifiers(sh,[modifier("power","stat.spell_power",5000)]) and slowed.enemy_stats_snapshot(sh) == defense_before,"enemy unsupported offensive modifier rejected atomically")
	slowed.despawn_enemy(sh)
	var replacement: Dictionary = spawn(slowed,Vector2(3,0))
	check(replacement.id == sh.id and replacement.generation > sh.generation and slowed.status_snapshot(replacement).is_empty() and slowed.enemy_stats_snapshot(replacement)["stat.resist.cold"] == 0,"ID generation reuse inherits neither chill nor defenses")
	check(slowed.status_snapshot(sh).is_empty() and slowed.enemy_stats_snapshot(sh).is_empty(),"stale handles cannot inspect replacement stats/status")
	var mortal = fresh()
	var mh: Dictionary = spawn(mortal,Vector2(1,0),20000)
	cast(mortal,"skill.frost_pulse")
	mortal.entity(mh).life_raw = 1
	mortal.tick = mortal.next_cast_tick
	mortal.mana_raw = 8960
	cast(mortal,"skill.frost_pulse")
	check(mortal.entity(mh).state == "dead" and mortal.status_snapshot(mh).is_empty() and mortal.kills == 1,"death removes status and emits one kill")
	mortal.reset(0)
	check(mortal.statuses.is_empty() and mortal._enemy_stats.is_empty() and mortal._pending_context.is_empty() and mortal._shot_contexts.is_empty() and mortal._issued_projectiles.is_empty() and mortal._instant_releases.is_empty(),"reset clears all combat lifecycle maps")

func projectile_snapshot() -> void:
	var s = fresh()
	spawn(s,Vector2(6,0))
	s.replace_player_modifiers([modifier("power","stat.spell_power",5000)])
	cast(s,"skill.ember_bolt")
	check(s._shot_contexts.size() == 1 and s._issued_projectiles.size() == 1,"released projectile owns paid context")
	s.replace_player_modifiers([])
	s.select_skill("skill.frost_pulse")
	for i in range(40): s.step()
	check(s.hits == 1 and s.combat_trace.back().power_bps == 5000 and s.combat_trace.back().skill_id == "skill.ember_bolt","in-flight attack snapshot survives modifier and selection changes")
	check(s._shot_contexts.is_empty() and s._issued_projectiles.is_empty() and s.bolts.is_empty(),"impact cleans projectile context")
	var expiry = fresh()
	cast(expiry,"skill.ember_bolt")
	for i in range(140): expiry.step()
	check(expiry._shot_contexts.is_empty() and expiry._issued_projectiles.is_empty() and expiry.bolts.is_empty(),"projectile lifetime cleans context without hit")
	var broken = fresh()
	cast(broken,"skill.ember_bolt")
	broken._shot_contexts.clear()
	broken.step()
	check(broken.bolts.is_empty() and broken.combat_errors.size() == 1 and broken._issued_projectiles.is_empty(),"missing committed context fails closed rather than recalculate attack")
	var manual = fresh()
	spawn(manual,Vector2(1,0))
	manual.bolts.append({"p":Vector2(1,0),"direction":Vector2.RIGHT,"age":0,"life":2,"id":900})
	manual.step_bolts()
	check(manual.hits == 1 and manual.combat_trace[0].source == "uncommitted_fixture","legacy injected projectile fallback explicitly marked")
	var pending_broken = fresh()
	pending_broken.step(true,Vector2.RIGHT,"skill.frost_pulse")
	pending_broken._pending_context.clear()
	for i in range(18): pending_broken.step()
	check(pending_broken.shots == 0 and pending_broken.pending.is_empty() and pending_broken.combat_errors.size() == 1 and pending_broken.mana_raw == 7936,"paid pending context loss fails closed with charge record retained")

func policies() -> void:
	var s = fresh()
	s.select_skill("skill.arc_chain")
	spawn(s,Vector2(5,0))
	var p = InputPolicy.new()
	p.toggle_auto()
	var request: Dictionary = p.consume_request(s,Vector2.LEFT)
	check(request.cast and request.policy == "auto" and request.aim == Vector2(5,0),"auto finds nearest in skill range")
	p.queued_cast = true
	request = p.consume_request(s,Vector2.LEFT)
	check(request.cast and request.policy == "manual" and request.aim == Vector2.LEFT,"manual request overrides auto aim")
	s.entity(s.handle(s.nearest_enemy(s.player))).p = Vector2(9,0)
	check(not p.consume_request(s,Vector2.LEFT).cast,"auto respects current skill range")
	p.clear()
	check(not p.auto_cast and not p.held and not p.queued_cast,"clear resets both policies")
	var manual = fresh()
	var automatic = fresh()
	spawn(manual,Vector2(5,0))
	spawn(automatic,Vector2(5,0))
	manual.select_skill("skill.arc_chain")
	automatic.select_skill("skill.arc_chain")
	var auto_input = InputPolicy.new()
	auto_input.toggle_auto()
	for i in range(30):
		manual.step(i == 0,Vector2(5,0))
		var req: Dictionary = auto_input.consume_request(automatic,Vector2.ZERO)
		automatic.step(req.cast,req.aim)
	check(manual.history == automatic.history and manual.rng.state == automatic.rng.state and manual.mana_raw == automatic.mana_raw,"manual and auto identical resolved trace for same accepted request")

func run() -> void:
	instant_targets()
	pending_snapshot()
	statuses_lifecycle()
	projectile_snapshot()
	policies()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional combat harness failure proof")
	print(JSON.stringify({"scope":"Independent phase4 scenario contracts, not recovered D2R combat","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
