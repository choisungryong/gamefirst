extends SceneTree
## Behavioral fixtures are deliberately separate from pilot_combat_run.gd normal rules.
const Run = preload("res://chapter1/core/combat_run.gd")
var checks := 0
var failures: Array[String] = []

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures.append(label)

func sandbox(primary: String = "chapter1.skill.ember") -> RefCounted:
	var run = Run.new()
	run.start(17,primary)
	run.enemies.clear()
	run._enemy_sequence = 0
	run.events.clear()
	run._next_spawn = 1000000
	run._rebuild_grid()
	return run

func context_for(run: RefCounted, skill: String, effects: Dictionary = {}) -> Dictionary:
	var fx: Dictionary = run.effective_skill(skill).effects if effects.is_empty() else effects.duplicate(true)
	return {"uid":100,"skill_id":skill,"effects":fx,"remaining_hits":int(fx.hit_budget),"hit_ids":[],"evolved":false}

func follow_primary(run: RefCounted) -> void:
	run.growth.award_xp(396)
	run._refresh_mode()
	for i in 5:
		var offer: Dictionary = run.get_offer()
		run.choose(offer.token,offer.cards[0].id)
	# Consume remaining cards by valid choices for deterministic fixture setup.
	while run.mode == "choice":
		var offer: Dictionary = run.get_offer()
		run.choose(offer.token,offer.cards[0].id)

func _initialize() -> void:
	var run = sandbox()
	check(run.mode == "playing" and run.hero.hp_raw == 120*256,"new run starts without touching any saved profile")
	var start: Dictionary = run.snapshot()
	run.set_paused(true)
	run.step(Vector2.RIGHT)
	check(run.tick == start.tick and run.hero.position == start.hero.position,"pause freezes world clock and movement")
	run.open_inventory()
	run.set_paused(false)
	check(run.mode == "inventory","clearing external pause does not close inventory")
	run.set_paused(true)
	run.close_inventory()
	check(run.mode == "paused","closing inventory preserves external focus pause")
	run.set_paused(false)
	check(run.mode == "playing","pause release restores active run")
	run.growth.award_xp(6)
	run._refresh_mode()
	var offer: Dictionary = run.get_offer()
	var paused_tick: int = run.tick
	for i in 100: run.step(Vector2.RIGHT)
	check(run.tick == paused_tick and run.get_offer() == offer,"growth modal freezes attacks/spawns and offer does not reroll")
	run.open_inventory()
	run.close_inventory()
	check(run.mode == "choice","inventory close restores pending growth choice")
	check(run.choose(offer.token,offer.cards[0].id) and run.mode == "playing","valid growth choice resumes play")
	check(not run.choose(offer.token,offer.cards[0].id),"spent offer cannot apply twice")
	run.step(Vector2(100,100))
	check(run.hero.position.length() <= 5.8/60.0+.0001,"diagonal input cannot increase speed")
	var before_bad: Vector2 = run.hero.position
	run.step(Vector2(INF,NAN))
	check(run.hero.position == before_bad,"nonfinite movement rejected")
	check(run.request_dash(Vector2.RIGHT),"dash request reserves cooldown")
	check(not run.request_dash(Vector2.RIGHT),"second dash cannot bypass cooldown")

	# Each unlocked skill schedules independently; these XP fixtures do not claim normal pacing.
	var multi = sandbox()
	multi.growth.award_xp(18)
	multi._refresh_mode()
	for desired in ["chapter1.skill.frost","chapter1.skill.arc"]:
		var choices: Dictionary = multi.get_offer()
		var selected := ""
		for card in choices.cards:
			if card.kind == "unlock" and card.skill_id == desired: selected = card.id
		check(not selected.is_empty() and multi.choose(choices.token,selected),"second and third auto skills can be learned")
	multi._spawn("elite",Vector2(0,-4))
	multi.enemies[1].hp_raw = 10000000
	multi.enemies[1].max_hp_raw = 10000000
	multi.enemies[1].frozen_until = 1000
	multi._rebuild_grid()
	for i in 220: multi.step()
	for skill in Run.SKILL_IDS:
		check(int(multi.metrics.casts.get(skill,0)) >= 2,"independent autocast executes "+skill)
		check(int(multi.metrics.hits.get(skill,0)) >= 1,"autocast deals actual damage "+skill)
	check(multi.metrics.peak_projectiles > 0,"friendly projectiles exist in world state")

	# Item effects alter future attacks, never a paid projectile snapshot or current HP.
	var paid = sandbox()
	paid._spawn("walker",Vector2(0,-4))
	paid.enemies[1].frozen_until = 1000
	paid._rebuild_grid()
	paid.step()
	var released: Dictionary = paid._contexts.values()[0].duplicate(true)
	var item: Dictionary = Run.ITEM_TEMPLATES[0].duplicate(true)
	item.uid = 999
	item.quality = "magic"
	paid.inventory.append(item)
	paid.open_inventory()
	check(paid.equip(999),"owned item equips while inventory open")
	check(paid.effective_skill("chapter1.skill.ember").effects.projectiles == 2,"weapon adds actual projectile count")
	check(paid._contexts.values()[0] == released,"equipping cannot mutate a released cast snapshot")
	var damage_before: int = paid.hero.hp_raw
	var armor: Dictionary = Run.ITEM_TEMPLATES[1].duplicate(true)
	armor.uid = 1000
	paid.inventory.append(armor)
	check(paid.equip(1000) and paid.hero.max_hp_raw == 150*256 and paid.hero.hp_raw == damage_before,"maxHP gear does not heal current HP")
	check(paid.compare_item(1000).equipped.uid == 1000,"item comparison reflects actual equipped identity")
	paid.close_inventory()
	var hit_raw := 0
	for i in 25:
		paid.step()
		for event in paid.events:
			if event.type == "hit": hit_raw = int(event.damage_raw)
	check(hit_raw == int(released.effects.damage_raw),"in-flight damage retains release-time value")
	var detached: Dictionary = paid.snapshot()
	detached.hero.hp_raw = 1
	detached.equipped.clear()
	check(paid.hero.hp_raw != 1 and not paid.equipped.is_empty(),"inspection snapshots are detached")

	# Death, reward and pickup are actual transitions, with no reward for another hit on a corpse.
	var loot = sandbox()
	loot._spawn("walker",Vector2(.3,0))
	loot._rebuild_grid()
	var ctx := context_for(loot,"chapter1.skill.ember")
	ctx.remaining_hits = 10
	loot._damage_enemy(1,ctx,0)
	loot._damage_enemy(1,ctx,0)
	check(loot.kills == 1 and loot.orbs.size() == 1,"death and XP source happen once")
	loot._collect_pickups()
	check(loot.growth.snapshot().xp == 1 and loot.orbs.is_empty(),"XP only enters growth after physical pickup")
	loot.kills = 5
	loot._spawn("walker",Vector2(.3,0))
	loot._rebuild_grid()
	loot._damage_enemy(2,ctx,0)
	check(loot.items.size() == 1 and loot.metrics.dropped_items == 1,"sixth kill offers a normal-rule shape-changing item")
	loot._collect_pickups()
	check(loot.inventory.size() == 1 and loot.items.is_empty(),"ground gear ownership transfers once on pickup")
	loot._collect_pickups()
	check(loot.inventory.size() == 1,"pickup cannot duplicate inventory")

	# Advertised hazards and actual geometric damage share one hero-center boundary.
	var hazard = sandbox()
	hazard._spawn("walker",Vector2(0,-.5))
	hazard._step_enemies()
	check(is_equal_approx(hazard.enemies[1].telegraph.radius,1.15),"melee telegraph matches hit radius")
	hazard.hero.position = Vector2(0,.66) # distance1.16, outside the advertised circle.
	hazard.tick = int(hazard.enemies[1].state_until)
	var hp: int = hazard.hero.hp_raw
	hazard._step_enemies()
	check(hazard.hero.hp_raw == hp,"outside melee hazard receives no damage")
	var elite = sandbox()
	elite._spawn("elite",Vector2(0,-2.5))
	elite._step_enemies()
	check(elite.enemies[1].telegraph.shape == "circle" and is_equal_approx(elite.enemies[1].telegraph.radius,3.4),"elite circle radius matches actual hit")
	elite.hero.position = Vector2(0,.91)
	elite.tick = int(elite.enemies[1].state_until)
	elite._step_enemies()
	check(elite.hero.hp_raw == 120*256,"outside elite circle receives no hit")
	var charger = sandbox()
	charger._spawn("charger",Vector2(0,-4.0))
	charger._step_enemies()
	var tele: Dictionary = charger.enemies[1].telegraph
	check(tele.shape == "line" and is_equal_approx(tele.length,4.8) and is_equal_approx(tele.radius,.71) and is_equal_approx(tele.width,1.42),"charger advertises swept capsule length and width")
	var frozen = sandbox()
	frozen._spawn("walker",Vector2(0,-.5))
	frozen._step_enemies()
	var original_deadline: int = frozen.enemies[1].state_until
	frozen.enemies[1].frozen_until = 50
	for i in 49:
		frozen.tick += 1
		frozen._step_enemies()
	check(frozen.enemies[1].state_until == original_deadline+49 and frozen.hero.hp_raw == 120*256,"freeze preserves unfinished windup time instead of attacking on thaw")
	frozen.tick = 50
	frozen._step_enemies()
	check(frozen.enemies[1].state == "windup" and frozen.hero.hp_raw == 120*256,"thaw keeps visible windup remainder")

	# Frost control/shatter and arc global cast budget use actual damage operations.
	var cold = sandbox("chapter1.skill.frost")
	follow_primary(cold)
	cold._spawn("elite",Vector2(0,-2))
	cold._spawn("walker",Vector2(.5,-2))
	cold.enemies[1].hp_raw = 170*256
	cold._rebuild_grid()
	var cold_context := context_for(cold,"chapter1.skill.frost")
	for i in 2: cold._damage_enemy(1,cold_context,0)
	check(cold.enemies[1].frozen_until > cold.tick,"cold accumulation applies real control")
	for i in 5: cold._damage_enemy(1,cold_context,0)
	var saw_shatter := false
	for event in cold.events:
		if event.type == "shatter": saw_shatter = true
	check(saw_shatter and cold.enemies[2].hp_raw == 0,"frozen death damages neighboring target through bounded shatter")
	var chain = sandbox("chapter1.skill.arc")
	follow_primary(chain)
	for i in 12: chain._spawn("walker",Vector2(float(i%4)*.6,-2.0-float(i/4)*.6))
	chain._rebuild_grid()
	var chain_context := context_for(chain,"chapter1.skill.arc")
	var positions: Array = chain._chain(chain.enemies[1],chain_context)
	var hit_ids: Dictionary = {}
	var no_repeat := true
	for event in chain.events:
		if event.type != "hit": continue
		if hit_ids.has(event.target_id): no_repeat = false
		hit_ids[event.target_id] = true
	check(no_repeat and hit_ids.size() <= int(chain_context.effects.hit_budget) and positions.size() > 0,"arc direct branches and death procs share per-entity dedup and cast budget")
	var pulse = sandbox("chapter1.skill.arc")
	follow_primary(pulse)
	pulse._spawn("walker",Vector2(0,-2))
	pulse._spawn("walker",Vector2(1,-2))
	pulse._spawn("walker",Vector2(5,-2))
	pulse._rebuild_grid()
	var pulse_context := context_for(pulse,"chapter1.skill.arc")
	pulse._damage_enemy(1,pulse_context,0)
	check(pulse.enemies[2].hp_raw == 0 and pulse.enemies[3].hp_raw > 0,"arc residual pulse is local3m, not chain reach")
	var pulse_cue := false
	for event in pulse.events:
		if event.type == "explosion" and event.radius_cm == 300: pulse_cue = true
	check(pulse_cue,"arc pulse VFX cue advertises actual local radius")
	var corner = sandbox()
	corner.hero.position = Vector2(19,19)
	var safe_spawn := true
	for i in 40:
		if corner._spawn_point(9.0,12.0).distance_to(corner.hero.position) < 7.2-.0001: safe_spawn = false
	check(safe_spawn,"corner clamping cannot spawn normal enemies on the hero")
	var one = sandbox()
	one._spawn("walker",Vector2(0,-2))
	one._spawn("walker",Vector2(.1,-2))
	one._rebuild_grid()
	var one_context := context_for(one,"chapter1.skill.ember")
	one_context.remaining_hits = 1
	one._area_hit(Vector2(0,-2),3,one_context,-1,0)
	check(one.kills == 1 and one_context.remaining_hits == 0,"area damage cannot exceed cast hit budget")

	var timed = sandbox()
	timed.tick = 100*60
	timed._elite_spawned = true
	timed._next_spawn = 1000000
	timed.step()
	check(timed.mode == "playing","clock alone cannot win encounter")
	var win = sandbox()
	win.tick = 75*60
	win._spawn("elite",Vector2(0,-2))
	win._rebuild_grid()
	var winning := context_for(win,"chapter1.skill.ember")
	winning.effects.damage_raw = 1000*256
	win._damage_enemy(1,winning,0)
	check(win.mode == "victory" and win.tick < 90*60 and win.inventory.size() == 1,"actual elite kill ends immediately with owned reward, no ninety-second wait")
	var ended: int = win.tick
	win.step(Vector2.RIGHT)
	check(win.tick == ended,"terminal encounter freezes further simulation")
	var lose = sandbox()
	lose._hero_damage(200*256,Vector2.ZERO)
	check(lose.mode == "defeat" and lose.hero.hp_raw == 0,"player HP zero causes real defeat")
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional combat harness failure")
	print("CHAPTER1_COMBAT_RESULT ",JSON.stringify({"checks":checks,"failures":failures,"scope":"behavioral fixtures; normal pilot is a separate script"}))
	quit(0 if failures.is_empty() else 1)
