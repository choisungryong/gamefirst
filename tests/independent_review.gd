extends SceneTree
## Independent bounded reconstruction checks; no original-game/OBS/UI input.
const Sim = preload("res://baseline_sim.gd")
var failures: Array[String] = []
var checks := 0

func _initialize() -> void:
	call_deferred("run")

func check(condition: bool, message: String) -> void:
	checks += 1
	if not condition:
		failures.append(message)
		push_error("REVIEW FAILED: " + message)

func isolated() -> RefCounted:
	var s = Sim.new()
	s.enemy_ai = false
	s.enemy.p = Vector2(100,100)
	return s

func bolt_at(point: Vector2, id_: int = 1) -> Dictionary:
	return {"p":point,"direction":Vector2.RIGHT,"age":0,"life":132,"id":id_}

func run() -> void:
	var profile: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://evidence-profile.json"))
	check(profile.player.raw_unit == Sim.UNIT, "profile raw unit agrees with core")
	check(profile.player.mana_raw == Sim.MANA_MAX, "profile initial mana agrees with core")
	check(profile.firebolt.mana_cost_raw == Sim.MANA_COST, "profile cost agrees with core")
	check(profile.firebolt.damage_raw.size() == 2 and profile.firebolt.damage_raw[0] == Sim.MIN_DAMAGE and profile.firebolt.damage_raw[1] == Sim.MAX_DAMAGE, "profile damage bounds agree with core")
	check(is_equal_approx(float(Sim.MANA_COST)/Sim.UNIT,2.5), "640 raw is exactly 2.5 units")
	check(Sim.MIN_DAMAGE == 768 and Sim.MAX_DAMAGE == 1536, "damage preserves raw 768-1536")
	check(profile.provisional_parameters.simulation_hz == Sim.HZ, "60Hz is explicit experiment setting")
	check(is_equal_approx(float(Sim.STARTUP_TICKS)/Sim.HZ,profile.firebolt.visible_startup_seconds), "startup target agrees with profile")
	check(profile.provisional_parameters.death_threshold_raw == 0, "zero death threshold explicitly provisional")
	check(FileAccess.get_sha256("res://assets/firebolt-sheet.png") == profile.original_firebolt_atlas_sha256, "decoded atlas hash preserved")
	var defaults = Sim.new()
	var provisional: Dictionary = profile.provisional_parameters
	check(defaults.life == profile.player.life, "profile initial life agrees with core")
	check(defaults.enemy.life_raw == provisional.enemy_hp*Sim.UNIT, "profile provisional enemyHP agrees with core")
	check(defaults.player == Vector2(provisional.spawn_player_world[0],provisional.spawn_player_world[1]), "profile player spawn agrees with core")
	check(defaults.enemy.p == Vector2(provisional.spawn_enemy_world[0],provisional.spawn_enemy_world[1]), "profile enemy spawn agrees with core")
	check(defaults.rng.seed == provisional.rng_seed, "profile seed agrees with core")
	check(is_equal_approx(float(defaults.cycle_ticks)/Sim.HZ,provisional.repeat_seconds), "profile repeat assumption agrees with core")
	check(is_equal_approx(defaults.bolt_speed,provisional.projectile_world_speed), "profile projectile speed agrees with core")
	defaults.set_destination(defaults.player+Vector2.RIGHT)
	var default_player: Vector2 = defaults.player
	var default_enemy: Vector2 = defaults.enemy.p
	defaults.step()
	check(is_equal_approx(defaults.player.distance_to(default_player)*Sim.HZ,provisional.player_world_speed), "profile player movement speed agrees with runtime step")
	check(is_equal_approx(Vector2(defaults.enemy.p).distance_to(default_enemy)*Sim.HZ,provisional.enemy_speed), "profile enemy movement speed agrees with runtime step")
	defaults.reset()
	defaults.enemy.p = defaults.player+Vector2.RIGHT
	defaults.step()
	check(defaults.enemy.state == "windup" and defaults.enemy.timer == provisional.enemy_attack_windup_seconds*Sim.HZ, "profile attack windup agrees with core")
	for i in range(int(provisional.enemy_attack_windup_seconds*Sim.HZ)): defaults.step()
	check(defaults.life == profile.player.life-provisional.enemy_damage, "profile enemy damage agrees with core")
	check(defaults.enemy.state == "recover" and defaults.enemy.timer == provisional.enemy_attack_recovery_seconds*Sim.HZ, "profile attack recovery agrees with core")

	var s = isolated()
	check(s.cast_request(s.player+Vector2.RIGHT*8), "first cast accepted")
	check(s.mana_raw == Sim.MANA_MAX-640, "one accepted request deducts one cost")
	check(not s.cast_request(s.player+Vector2.UP*8), "pending cast rejects duplicate request")
	for i in range(17): s.step()
	check(s.shots == 0, "no early projectile before tick18")
	s.step()
	check(s.shots == 1 and s.bolts.size() == 1, "single projectile at release boundary")
	check(s.bolts[0].direction == Vector2.RIGHT, "cast aim fixed at request")
	check(is_equal_approx(s.bolts[0].p.x-s.player.x,s.bolt_speed/Sim.HZ+provisional.projectile_spawn_offset), "profile spawn offset agrees with post-release step")
	check(s.bolts[0].life == provisional.projectile_life_seconds*Sim.HZ-1, "profile projectile lifetime agrees with first age step")
	for i in range(15): s.step()
	check(s.shots == 1, "release does not repeat without a new request")
	check(s.history.filter(func(e): return e.kind == "release").size() == 1, "one release event")

	s = isolated()
	s.mana_raw = 639
	check(not s.cast_request(s.player+Vector2.RIGHT), "639 raw refuses cast")
	check(s.pending.is_empty() and s.shots == 0 and s.mana_raw == 639, "failed cast creates nothing and spends nothing")
	s.set_destination(s.player+Vector2.RIGHT)
	var old_position: Vector2 = s.player
	s.step()
	check(s.player != old_position, "insufficient mana notification does not lock movement")
	s = isolated()
	s.mana_raw = 640
	check(s.cast_request(s.player+Vector2.RIGHT) and s.mana_raw == 0, "exactly640 raw pays once")
	for i in range(33): s.step()
	check(not s.cast_request(s.player+Vector2.RIGHT), "zero mana refuses next cast")

	s = isolated()
	for i in range(14):
		check(s.cast_request(s.player+Vector2.RIGHT*8), "exhaustion cast %d accepted" % (i+1))
		for j in range(33): s.step()
	check(s.shots == 14 and s.mana_raw == 0, "14 casts exhaust35 mana with14 releases")
	check(not s.cast_request(s.player+Vector2.RIGHT*8), "15th cast refused")
	for i in range(40): s.step()
	check(s.shots == 14, "refused15th cast cannot release later")

	s = isolated()
	s.enemy.p = Vector2.ZERO
	s.enemy.life_raw = 1000000
	s.bolts = [bolt_at(Vector2(-5,0))]
	s.bolt_speed = 600.0
	s.step()
	check(s.hits == 1 and s.bolts.is_empty(), "swept collision catches fast crossing and consumes bolt")
	check(s.enemy.timer == provisional.enemy_hurt_seconds*Sim.HZ, "profile enemy hurt time agrees with core")
	var damaged_life: int = s.enemy.life_raw
	for i in range(10): s.step()
	check(s.hits == 1 and s.enemy.life_raw == damaged_life, "consumed bolt never damages twice")
	check(s.swept_fraction(Vector2(-1,1),Vector2(1,1),Vector2.ZERO,.52) < 0, "parallel miss remains miss")
	check(s.swept_fraction(Vector2.ZERO,Vector2.ZERO,Vector2.ZERO,.52) >= 0, "zero-length overlap has defined collision")

	s = isolated()
	s.enemy.p = Vector2.ZERO
	s.enemy.life_raw = 1
	s.bolts = [bolt_at(Vector2.ZERO,1),bolt_at(Vector2.ZERO,2)]
	s.step()
	check(s.enemy.state == "dead" and s.hits == 1, "simultaneous bolts cannot damage newly dead enemy again")
	check(s.history.filter(func(e): return e.kind == "enemy_dead").size() == 1, "one death event")
	var death_hits: int = s.hits
	s.bolts.append(bolt_at(Vector2.ZERO,3))
	s.step()
	check(s.hits == death_hits and s.enemy.life_raw == 0, "dead enemy immune to subsequent projectiles")

	s = isolated()
	s.enemy.p = Vector2.ZERO
	s.enemy.life_raw = 1000000
	var fractional_seen := false
	for i in range(20):
		s.bolts = [bolt_at(Vector2.ZERO,i+1)]
		var before: int = s.enemy.life_raw
		s.step()
		var applied: int = before-int(s.enemy.life_raw)
		check(applied >= 768 and applied <= 1536, "seeded raw damage stays in declared range")
		if applied % 256 != 0: fractional_seen = true
	check(fractional_seen, "raw damage was not truncated to whole display units")

	s = isolated()
	s.cast_request(s.player+Vector2.RIGHT*8)
	for i in range(5): s.step()
	s.paused = true
	var snapshot := [s.tick,s.player,s.mana_raw,s.pending.duplicate(true),s.history.duplicate(true)]
	for i in range(50): s.step(true,Vector2.UP)
	check(snapshot == [s.tick,s.player,s.mana_raw,s.pending,s.history], "pause freezes core and pending release")
	check(not s.cast_request(Vector2.UP), "paused requests cannot charge mana")
	s.reset()
	check(s.tick == 0 and s.mana_raw == Sim.MANA_MAX and s.pending.is_empty() and s.bolts.is_empty() and s.history.is_empty(), "reset clears pending/log/projectiles and refills mana")
	for i in range(40): s.step()
	check(s.shots == 0, "pre-reset pending release cannot fire after reset")

	var traces: Array = []
	for repetition in range(2):
		s = isolated()
		s.enemy.p = Vector2(3,3.5)
		s.enemy.life_raw = 100000
		for i in range(180): s.step(i < 150,Vector2(3,3.5))
		traces.append(s.history.duplicate(true))
	check(traces[0] == traces[1], "fixed seed and input produce same event trace")

	var scene: PackedScene = load("res://Baseline.tscn")
	var view = scene.instantiate()
	root.add_child(view)
	view.set_process(false)
	view.set_physics_process(false)
	view.sim.enemy_ai = false
	view.sim.enemy.p = Vector2(100,100)
	view.sim.set_destination(view.sim.player)
	view.sync_actors()
	for actor in [view.hero,view.enemy_actor]:
		var animation_names: Dictionary = actor.get_meta("animations")
		for clip in ["Idle","Walking_A","Spellcast_Shoot","Hit_A","Death_A","Unarmed_Melee_Attack_Punch_A"]:
			check(animation_names.has(clip), "required proxy animation exists: "+clip)
	view.queued_cast = true
	view.held = false
	view._physics_process(1.0/60)
	check(view.sim.pending.size() > 0 and view.sim.events.filter(func(e): return e.kind == "cast_start").size() == 1, "quick queued click starts one cast and retains event")
	check(not view.queued_cast, "queued quick click consumed once")
	view.restart()
	view.sim.enemy_ai = false
	view.sim.enemy.p = Vector2(100,100)
	view.handle_event({"kind":"player_hurt","life":37})
	var ap: AnimationPlayer = view.hero.get_meta("player")
	for i in range(100):
		view._physics_process(1.0/60)
		view._process(1.0/60)
		ap.advance(1.0/60)
	check(String(ap.current_animation).get_file() == "Idle", "hero returns to Idle after finite hurt response")
	view.held = true
	var release := InputEventMouseButton.new()
	release.button_index = MOUSE_BUTTON_RIGHT
	release.pressed = false
	# Directly exercise app-side global release handler; no OS input injection.
	if view.has_method("_input"): view._input(release)
	check(not view.held, "global release clears held flag even if GUI consumes event")
	view.held = true
	view.queued_cast = true
	view.clear_pointer_state()
	check(not view.held and not view.queued_cast, "focus loss clears held and queued inputs")
	view.sim.cast_request(view.sim.player+Vector2.RIGHT*8)
	view._physics_process(1.0/60)
	view.toggle_pause()
	var paused_tick: int = view.sim.tick
	var paused_fx: float = view.fx_time
	var hero_ap: AnimationPlayer = view.hero.get_meta("player")
	var enemy_ap: AnimationPlayer = view.enemy_actor.get_meta("player")
	view._physics_process(1.0/60)
	view._process(1.0/60)
	check(view.sim.tick == paused_tick and view.fx_time == paused_fx, "view pause freezes simulation and FX")
	check(hero_ap.speed_scale == 0 and enemy_ap.speed_scale == 0, "view pause freezes both actor animation players")
	view.restart()
	check(not view.sim.paused and view.sim.pending.is_empty() and view.projectile_nodes.is_empty() and view.particles.is_empty(), "view restart clears paused state and visuals")
	check(hero_ap.speed_scale == 1 and enemy_ap.speed_scale == 1, "restart restores animation playback")
	view.queue_free()
	if OS.get_cmdline_user_args().has("--prove-failure"):
		check(false, "intentional independent harness failure proof")
	print(JSON.stringify({"scope":"independent reconstruction checks, not original D2R validation","checks":checks,"failures":failures}))
	quit(0 if failures.is_empty() else 1)
