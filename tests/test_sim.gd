extends SceneTree
const Core = preload("res://baseline_sim.gd")
var checked := 0
var failures: Array[String] = []

func check(value: bool, message: String) -> void:
	checked += 1
	if not value:
		failures.append(message)
		printerr("CHECK FAILED: "+message)

func _initialize() -> void:
	var sim = Core.new()
	var profile: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://evidence-profile.json"))
	check(profile.firebolt.mana_cost_raw == Core.MANA_COST,"profile/raw mana contract")
	check(int(profile.firebolt.damage_raw[0]) == Core.MIN_DAMAGE and int(profile.firebolt.damage_raw[1]) == Core.MAX_DAMAGE,"profile/raw damage contract")
	check(is_equal_approx(profile.firebolt.visible_startup_seconds,float(Core.STARTUP_TICKS)/Core.HZ),"profile/visible target contract")
	check(profile.provisional_parameters.simulation_hz == Core.HZ,"profile/simulation hz contract")
	check(is_equal_approx(profile.provisional_parameters.repeat_seconds,float(sim.cycle_ticks)/Core.HZ),"profile/assumed repeat contract")
	check(profile.provisional_parameters.projectile_world_speed == sim.bolt_speed,"profile/assumed speed contract")
	sim.enemy_ai = false
	check(sim.mana_raw==8960,"35 mana uses raw 1/256 units")
	check(sim.cast_request(Vector2(3.4,-2.5)),"initial cast accepted")
	check(sim.mana_raw==8320,"exact 640 raw cost")
	check(not sim.cast_request(Vector2(3.4,-2.5)),"no duplicate request during startup")
	for i in range(17): sim.step()
	check(sim.shots==0,"nothing emitted before 18 ticks")
	sim.step()
	check(sim.shots==1,"single projectile at the 18 tick target")
	check(sim.history.filter(func(e):return e.kind=="release").size()==1,"exactly one release event")
	var before: int = sim.tick
	var pending_before: String = JSON.stringify(sim.pending)
	sim.paused = true
	for i in range(20): sim.step(true,Vector2.ZERO)
	check(sim.tick==before and JSON.stringify(sim.pending)==pending_before,"pause preserves simulation")
	sim.paused = false
	for i in range(80): sim.step()
	check(sim.hits==1,"one bolt damages once")
	var hit_events: Array = sim.history.filter(func(e):return e.kind=="hit")
	check(not hit_events.is_empty(),"collision emits damage event")
	if not hit_events.is_empty():
		var hit_event: Dictionary = hit_events[0]
		check(hit_event.damage_raw>=768 and hit_event.damage_raw<=1536,"raw damage within tooltip-derived interval")
	check(sim.bolts.is_empty(),"colliding projectile consumed")
	check(sim.swept_fraction(Vector2(-4,0),Vector2(4,0),Vector2.ZERO,.5)>=0,"sweep prevents crossing through target")
	sim.reset()
	sim.enemy_ai = false
	for cast in range(14):
		check(sim.cast_request(Vector2(-7,-5)),"cast "+str(cast+1)+" can be paid")
		for i in range(34): sim.step()
	check(sim.mana_raw==0,"fourteen exact costs exhaust 35")
	check(not sim.cast_request(Vector2.ZERO),"insufficient mana rejects cast")
	sim.set_destination(sim.player+Vector2(1,0))
	var movement_before: Vector2 = sim.player
	sim.step()
	check(sim.player != movement_before,"insufficient mana notice does not lock movement")
	for i in range(40): sim.step()
	check(sim.shots==14,"rejected cast cannot emit")
	sim.reset()
	sim.enemy_ai = false
	sim.enemy.life_raw = 1
	sim.enemy.p = Vector2(0,1)
	for i in range(90): sim.step(true,Vector2(0,1))
	check(sim.enemy.state=="dead" and sim.hits==1,"dead enemy cannot take duplicate hits")
	check(sim.history.filter(func(e):return e.kind=="enemy_dead").size()==1,"one death event")
	sim.reset()
	check(sim.life==40 and sim.mana_raw==8960 and sim.enemy.state=="approach" and sim.history.is_empty(),"restart clears experiment")
	if OS.get_cmdline_user_args().has("--prove-failure"):
		check(false,"intentional harness negative control")
	var result: Dictionary = {"checks":checked,"failures":failures,"success":failures.is_empty()}
	print("BASELINE_TEST_RESULT ",JSON.stringify(result))
	if failures.is_empty(): print("BASELINE_TESTS_OK checks=",checked)
	quit(0 if failures.is_empty() else 1)
