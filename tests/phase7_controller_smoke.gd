extends SceneTree
const Controller = preload("res://run/expedition_controller.gd")
var failures: Array[String] = []
func check(value: bool, message: String) -> void:
	if not value: failures.append(message)
func _initialize() -> void:
	var run := Controller.new()
	check(run.state == "ready" and run.sim.enemies.is_empty(),"ready has no enemies")
	check(run.start(),"start")
	run.sim.enemy_ai = false
	run.sim.mana_raw = 0
	for i in range(60): run.step()
	check(run.sim.mana_raw == 768 and run.elapsed_ticks == 60,"exact3mana/s")
	run.set_paused(true)
	var before: Dictionary = run.snapshot()
	var rng_state: int = run.spawn_rng.state
	for i in range(60): run.step()
	check(before == run.snapshot() and rng_state == run.spawn_rng.state,"paused frozen")
	run.set_paused(false)
	run.sim.life = 7
	run.sim.mana_raw = 123
	var doc: Dictionary = run.sim.progress_document()
	check(run.replace_profile_document(doc),"load candidate")
	check(run.sim.life == 7 and run.sim.mana_raw == 123 and run.elapsed_ticks == 0,"load noheal clock0")
	run.elapsed_ticks = run.ELITE_TICK-1
	run.step()
	check(run.elite_spawned and int(run.sim.entity(run.elite_identity).max_raw) == 54*256,"one elite54HP")
	run.elapsed_ticks = run.TIMEOUT_TICK-1
	run.step()
	check(run.state == "timeout","300seconds timeout")
	var tick: int = run.sim.tick
	var elapsed: int = run.elapsed_ticks
	run.step()
	check(run.sim.tick == tick and run.elapsed_ticks == elapsed,"terminal frozen")
	check(run.restart() and run.sim.life == float(run.sim.life_max_raw)/256,"R explicit fullheal")
	print(JSON.stringify({"success":failures.is_empty(),"failures":failures,"scope":"implementation smoke with explicit boundary clock fixtures; no real-time/GPU claim"}))
	quit(0 if failures.is_empty() else 1)
