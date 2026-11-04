extends RefCounted
## Fixed-tick independent expedition policy. The baseline simulation is unchanged.
## All time, spawn, resource and outcome authority lives here, not in presenters.
const Simulation = preload("res://baseline_sim.gd")
const HZ := 60
const VICTORY_TICK := 240*HZ
const TIMEOUT_TICK := 300*HZ
const ELITE_TICK := 180*HZ
const MAX_BACKLOG := 8
const REGEN_RAW_PER_SECOND := 3*256
const DEFAULT_SEED := 73001
var sim: RefCounted
var state := "ready"
var elapsed_ticks := 0
var paused := false
var seed := DEFAULT_SEED
var spawn_rng := RandomNumberGenerator.new()
var backlog: Array = []
var dropped_requests := 0
var failed_positions := 0
var events: Array = []
var history: Array = []
var elite_identity: Dictionary = {}
var elite_spawned := false
var elite_defeated := false
var elite_reserved := false
var _elite_queued := false
var _mana_remainder := 0
var _start_xp := 0
var _pickup_count := 0
var _result: Dictionary = {}

func _init(simulation: RefCounted = null) -> void:
	sim = simulation if simulation != null else Simulation.new()
	sim.reset(0)
	sim.paused = true
	spawn_rng.seed = seed

func _emit(kind: String, details: Dictionary = {}) -> void:
	var event: Dictionary = details.duplicate(true)
	event["kind"] = kind
	event["run_tick"] = elapsed_ticks
	events.append(event)
	if history.size() >= 256: history.pop_front()
	history.append(event.duplicate(true))

func start(seed_value: int = DEFAULT_SEED) -> bool:
	if not sim.valid_profile: return false
	var old_epoch: int = sim._loot_epoch
	sim.reset(0)
	if sim._loot_epoch == old_epoch: return false
	_begin(seed_value)
	return true

func _begin(seed_value: int) -> void:
	state = "active"
	elapsed_ticks = 0
	paused = false
	sim.paused = false
	seed = seed_value
	spawn_rng.seed = seed_value
	backlog.clear()
	events.clear()
	history.clear()
	dropped_requests = 0
	failed_positions = 0
	elite_identity.clear()
	elite_spawned = false
	elite_defeated = false
	elite_reserved = false
	_elite_queued = false
	_mana_remainder = 0
	_start_xp = int(sim.progression_snapshot().xp)
	_pickup_count = 0
	_result.clear()
	_emit("run_started",{"seed":seed,"loaded_profile":not sim.ground_loot_snapshot().is_empty()})
	_enqueue("normal")
	_drain_backlog()

func restart() -> bool:
	return start(seed)

func return_to_menu() -> void:
	state = "ready"
	paused = false
	sim.paused = true
	events.clear()

func set_paused(value: bool) -> void:
	if state != "active": return
	paused = value
	sim.paused = value

func load_profile(path: String = "user://progress-v1.json") -> bool:
	if not sim.load_progress(path): return false
	# Sim.load_progress already starts new combat and preserves absolute vitals.
	# A second reset here would heal and destroy the restored ground rewards.
	_begin(seed)
	return true

func replace_profile_document(candidate: Variant) -> bool:
	if not sim.replace_progress_document(candidate): return false
	_begin(seed)
	return true

func adopt_loaded_profile() -> void:
	# Called only after the shared equipment modal has committed Sim.load_progress.
	_begin(seed)

func save_profile(path: String = "user://progress-v1.json") -> bool:
	return sim.save_progress(path)

func phase() -> String:
	if elapsed_ticks < 15*HZ: return "arrival"
	if elapsed_ticks < 60*HZ: return "awakening"
	if elapsed_ticks < 150*HZ: return "pressure"
	if elapsed_ticks < ELITE_TICK: return "warning"
	if elapsed_ticks < VICTORY_TICK: return "elite"
	return "finale"

func alive_cap() -> int:
	if elapsed_ticks < 60*HZ: return 8
	if elapsed_ticks < 150*HZ: return 16
	if elapsed_ticks < ELITE_TICK: return 12
	return 20

func _enqueue(kind: String) -> void:
	if backlog.size() >= MAX_BACKLOG:
		if kind != "elite":
			dropped_requests += 1
			_emit("spawn_request_dropped",{"reason":"backlog_full","count":1})
		return
	backlog.append({"kind":kind,"requested_tick":elapsed_ticks})
	if kind == "elite": _elite_queued = true

func _schedule() -> void:
	if elapsed_ticks >= VICTORY_TICK: return
	if elapsed_ticks >= ELITE_TICK and not elite_reserved:
		elite_reserved = true
		_emit("elite_reserved")
	if elite_reserved and not elite_spawned and not _elite_queued: _enqueue("elite")
	if elapsed_ticks >= 15*HZ and elapsed_ticks < 60*HZ and (elapsed_ticks-15*HZ)%(6*HZ) == 0:
		_enqueue("normal")
	elif elapsed_ticks >= 60*HZ and elapsed_ticks < 150*HZ and (elapsed_ticks-60*HZ)%(4*HZ) == 0:
		_enqueue("normal")
		_enqueue("normal")
	elif elapsed_ticks >= 150*HZ and (elapsed_ticks-150*HZ)%(6*HZ) == 0:
		_enqueue("normal")

func _spawn_position() -> Variant:
	var bounds := Vector2(sim.params.world_bounds[0],sim.params.world_bounds[1])
	for attempt in range(4):
		var angle: float = spawn_rng.randf_range(-PI,PI)
		var radius: float = spawn_rng.randf_range(5.5,9.0)
		var candidate: Vector2 = sim.player+Vector2(cos(angle),sin(angle))*radius
		if absf(candidate.x) <= bounds.x and absf(candidate.y) <= bounds.y and candidate.distance_squared_to(sim.player) >= 25.0: return candidate
	return null

func _drain_backlog() -> void:
	# At most eight requests and four position trials each per fixed tick.
	var attempts := 0
	while not backlog.is_empty() and attempts < MAX_BACKLOG and sim.alive_count() < alive_cap():
		attempts += 1
		var request: Dictionary = backlog[0]
		var position: Variant = _spawn_position()
		if position == null:
			failed_positions += 1
			_emit("spawn_position_failed",{"kind_requested":request.kind,"attempts":4})
			if request.kind == "elite": break
			backlog.pop_front()
			continue
		var identity: Dictionary = sim.spawn_enemy(position)
		if identity.is_empty():
			_emit("spawn_rejected",{"reason":"entity_capacity_or_counter","kind_requested":request.kind})
			if request.kind == "elite": break
			backlog.pop_front()
			continue
		backlog.pop_front()
		if request.kind == "elite":
			elite_identity = identity.duplicate(true)
			elite_spawned = true
			_elite_queued = false
			var enemy: Dictionary = sim.entity(identity)
			enemy.life_raw = 54*256
			enemy.max_raw = 54*256
		_emit("run_spawned",{"entity":identity,"elite":request.kind == "elite","p":[position.x,position.y]})

func _observe_elite() -> void:
	if not elite_spawned or elite_defeated: return
	var enemy: Dictionary = sim.entity(elite_identity)
	if not enemy.is_empty() and enemy.state == "dead":
		elite_defeated = true
		_emit("elite_defeated",{"entity":elite_identity})

func _finish_if_needed() -> bool:
	if sim.life <= 0: _finish("defeat")
	elif elapsed_ticks >= TIMEOUT_TICK and not elite_defeated: _finish("timeout")
	elif elapsed_ticks >= VICTORY_TICK and elite_defeated: _finish("victory")
	return state != "active"

func _finish(outcome: String) -> void:
	if state != "active": return
	state = outcome
	paused = false
	sim.paused = true
	_result = {"outcome":state,"elapsed_ticks":elapsed_ticks,"elapsed_seconds":float(elapsed_ticks)/HZ,"kills":sim.kills,"elite_spawned":elite_spawned,"elite_defeated":elite_defeated,"xp_delta":int(sim.progression_snapshot().xp)-_start_xp,"pickups":_pickup_count,"equipped":sim.equipment_snapshot().get("equipped",{}).duplicate(true),"seed":seed}
	_emit("run_ended",_result)

func step(cast_held: bool = false, aim: Vector2 = Vector2.ZERO, skill_id: String = "") -> void:
	events.clear()
	if state != "active" or paused or sim.paused: return
	if sim.life <= 0:
		_finish("defeat")
		return
	elapsed_ticks += 1
	sim.step(cast_held,aim,skill_id)
	for event in sim.progress_events:
		if event.kind == "loot_pickup": _pickup_count += 1
	_observe_elite()
	if _finish_if_needed(): return
	# Integer remainder makes 768 raw/second exact without float drift.
	_mana_remainder += REGEN_RAW_PER_SECOND
	var recovered: int = _mana_remainder/HZ
	_mana_remainder %= HZ
	var previous: int = sim.mana_raw
	sim.mana_raw = mini(sim.mana_max_raw,sim.mana_raw+recovered)
	if sim.mana_raw > previous: _emit("run_resource_regen",{"amount_raw":sim.mana_raw-previous,"resource":"mana"})
	_schedule()
	if elapsed_ticks < VICTORY_TICK: _drain_backlog()
	else:
		# No ordinary spawning after 240s. A deferred one-shot elite stays eligible.
		var retained: Array = []
		for request in backlog:
			if request.kind == "elite": retained.append(request)
		backlog = retained
		if elite_reserved and not elite_spawned and not _elite_queued: _enqueue("elite")
		_drain_backlog()

func snapshot() -> Dictionary:
	return {"state":state,"elapsed_ticks":elapsed_ticks,"elapsed_seconds":float(elapsed_ticks)/HZ,"remaining_seconds":maxf(0,float(TIMEOUT_TICK-elapsed_ticks)/HZ),"phase":phase(),"elite_spawned":elite_spawned,"elite_defeated":elite_defeated,"elite_identity":elite_identity.duplicate(true),"paused":paused,"seed":seed,"backlog":backlog.duplicate(true),"dropped_requests":dropped_requests,"failed_positions":failed_positions,"summary":_result.duplicate(true)}

func history_snapshot() -> Array:
	return history.duplicate(true)
