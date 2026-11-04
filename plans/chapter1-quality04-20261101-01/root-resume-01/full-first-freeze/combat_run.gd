extends RefCounted
## C2 representative encounter, independent design. Fixed 60 Hz, no profile I/O.
## Existing CombatResolver integer damage pattern is reused; presentation cannot deal damage.
## Auto casts reserve a per-skill cooldown (no mana in this encounter), then retain an immutable
## release snapshot. Changing gear/rank while a projectile exists cannot change that shot.
const GrowthCatalog = preload("res://chapter1/core/growth_catalog.gd")
const Growth = preload("res://chapter1/core/run_growth.gd")
const Resolver = preload("res://combat/combat_resolver.gd")
const HZ := 60
const UNIT := 256
const STEP := 1.0 / HZ
const BOUND := 19.0
const MAX_ALIVE := 180
const MAX_ENTITIES := 512
const MAX_PROJECTILES := 384
const MAX_HOSTILE_PROJECTILES := 192
const MAX_ORBS := 400
const MAX_GROUND_ITEMS := 32
const MAX_INVENTORY := 64
const MAX_OBJECTIVE_REWARDS := 1 # Reserved owned slot; never replaces ordinary gear.
const MAX_EVENTS := 1024
# Local approach steering is an independent crowd rule, not cosmetic displacement.
# At most32 bodies from the current/adjacent2m cells can influence an approach.
const MAX_CROWD_NEIGHBORS := 32
const CROWD_RADIUS := 1.85
const CROWD_GAP := .08
const CROWD_PUSH_PER_STEP := .045
const HERO_RADIUS := .28
const HERO_APPROACH_GAP := .12
const ELITE_TICK := 70 * HZ
const SKILL_IDS := ["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"]
const ENEMY_DEFS := {
	"walker":{"hp":12,"speed":1.60,"radius":.30,"damage":5,"windup":25,"recover":58,"xp":1},
	"ranged":{"hp":18,"speed":1.45,"radius":.32,"damage":5,"windup":40,"recover":125,"xp":2},
	"charger":{"hp":32,"speed":1.95,"radius":.43,"damage":8,"windup":48,"recover":90,"xp":3},
	"elite":{"hp":720,"speed":1.75,"radius":.85,"damage":12,"windup":48,"recover":100,"xp":12}
}
const ITEM_TEMPLATES := [
	{"base_id":"chapter1.item.cinder_branch","name":"균열의 잿불 가지","slot":"weapon","stats":{"damage_bps":1000,"projectiles":1},"description":"피해 증가 · 발사체 +1. 연쇄 기술은 연쇄 대상 +1."},
	{"base_id":"chapter1.item.guard_robe","name":"수호의 재옷","slot":"body","stats":{"max_hp_raw":7680,"damage_reduction_bps":700},"description":"최대 생명력 +30 · 받는 피해 감소. 장착은 현재 생명력을 회복하지 않습니다."},
	{"base_id":"chapter1.item.harvest_crystal","name":"회수의 재결정","slot":"charm","stats":{"pickup_radius_cm":100,"cooldown_bps":800},"description":"회수 반경 +1m · 기술 주기 단축."},
	{"base_id":"chapter1.item.conductor_ring","name":"갈래 도체 반지","slot":"ring","stats":{"damage_bps":500,"chain_targets":1,"shatter_count":1},"description":"피해 증가 · 연쇄 +1 · 파쇄 파편 +1."}
]
var mode := "menu"
var tick := 0
var kills := 0
var hero: Dictionary = {}
var enemies: Dictionary = {}
var projectiles: Array[Dictionary] = []
var orbs: Array[Dictionary] = []
var items: Array[Dictionary] = []
var inventory: Array[Dictionary] = []
var equipped: Dictionary = {}
var events: Array[Dictionary] = []
var growth = Growth.new()
var errors: Array[String] = []
var metrics: Dictionary = {}
var _catalog = GrowthCatalog.new()
var _spawn_rng := RandomNumberGenerator.new()
var _loot_rng := RandomNumberGenerator.new()
var _next_cast: Dictionary = {}
var _contexts: Dictionary = {}
var _grid: Dictionary = {}
var _enemy_sequence := 0
var _projectile_sequence := 0
var _orb_sequence := 0
var _item_sequence := 0
var _cast_sequence := 0
var _event_sequence := 0
var _epoch := 0
var _next_spawn := 0
var _elite_spawned := false
var _elite_killed := false
var _paused := false
var _inventory_open := false
var _terminal_mode := ""
var _dash_direction := Vector2.ZERO
var _dash_until := 0
var _next_dash := 0
var _invulnerable_until := 0
var _gear_stats: Dictionary = {}
var _guaranteed_drops := 0
var _elite_reward_uid := 0

func start(seed_: int = 1, primary: String = "chapter1.skill.ember") -> bool:
	if not _catalog.load_file():
		errors.assign(_catalog.errors)
		return false
	if not growth.configure(_catalog.snapshot(),primary,seed_ ^ 0x47524f57):
		errors.assign(growth.errors)
		return false
	_epoch += 1
	tick = 0
	kills = 0
	mode = "playing"
	hero = {"position":Vector2.ZERO,"hp_raw":120*UNIT,"max_hp_raw":120*UNIT,"speed":5.8,"direction":Vector2.UP}
	enemies.clear()
	projectiles.clear()
	orbs.clear()
	items.clear()
	inventory.clear()
	equipped.clear()
	events.clear()
	_next_cast.clear()
	_contexts.clear()
	_grid.clear()
	_enemy_sequence = 0
	_projectile_sequence = 0
	_orb_sequence = 0
	_item_sequence = 0
	_cast_sequence = 0
	_event_sequence = 0
	_next_spawn = 30
	_elite_spawned = false
	_elite_killed = false
	_paused = false
	_inventory_open = false
	_terminal_mode = ""
	_dash_direction = Vector2.ZERO
	_dash_until = 0
	_next_dash = 0
	_invulnerable_until = 0
	_gear_stats.clear()
	_guaranteed_drops = 0
	_elite_reward_uid = 0
	_spawn_rng.seed = seed_ ^ 0x53504157
	_loot_rng.seed = seed_ ^ 0x4c4f4f54
	metrics = {"casts":{},"hits":{},"max_alive":0,"peak_projectiles":0,"enemy_attacks":0,"collected_xp":0,"dropped_items":0,"picked_items":0,"events_dropped":0,"orbs_merged":0,"damage_raw":0,"crowd_neighbor_checks":0,"crowd_peak_neighbors":0,"crowd_adjustments":0}
	for i in 24:
		var angle := TAU*float(i)/24.0
		_spawn("walker",hero.position+Vector2(cos(angle),sin(angle))*_spawn_rng.randf_range(5.5,8.0))
	_rebuild_grid()
	_update_metrics()
	errors.clear()
	return true

func elapsed() -> float:
	return float(tick)/HZ

func get_next_dash_tick() -> int:
	return _next_dash

func alive_count() -> int:
	var count := 0
	for e in enemies.values():
		if e.hp_raw > 0: count += 1
	return count

func set_paused(value: bool) -> void:
	_paused = value
	_refresh_mode()

func open_inventory() -> bool:
	if mode == "menu" or _terminal_mode == "defeat": return false
	_inventory_open = true
	_refresh_mode()
	return true

func close_inventory() -> void:
	_inventory_open = false
	_refresh_mode()

func _refresh_mode() -> void:
	if mode == "menu": return
	if not _terminal_mode.is_empty():
		mode = "inventory" if _inventory_open and _terminal_mode == "victory" else _terminal_mode
	elif _paused: mode = "paused"
	elif _inventory_open: mode = "inventory"
	elif not growth.snapshot().pending_levels.is_empty(): mode = "choice"
	else: mode = "playing"

func get_offer() -> Dictionary:
	return growth.next_offer() if mode == "choice" else {}

func choose(token: String, card_id: String) -> bool:
	if mode != "choice" or not growth.choose(token,card_id): return false
	_emit("growth",hero.position,{"card_id":card_id,"growth":growth.snapshot()})
	_refresh_mode()
	return true

func request_dash(direction: Vector2) -> bool:
	if mode != "playing" or tick < _next_dash or not direction.is_finite(): return false
	_dash_direction = direction.normalized() if direction.length_squared() > .001 else hero.direction
	_dash_until = tick+12
	_next_dash = tick+180
	# step() increments first: protect the next18 simulation steps, including step18.
	_invulnerable_until = maxi(_invulnerable_until,tick+19)
	_emit("dash",hero.position,{"direction":_dash_direction})
	return true

func equip(uid: int) -> bool:
	if mode != "inventory": return false
	var found: Dictionary = {}
	for item in inventory:
		if item.uid == uid: found = item
	if found.is_empty(): return false
	equipped[found.slot] = found.uid
	_recompute_gear()
	_emit("equip",hero.position,{"item":found.duplicate(true),"stats":_gear_stats.duplicate(true)})
	return true

func unequip(slot: String) -> bool:
	if mode != "inventory" or not equipped.has(slot): return false
	equipped.erase(slot)
	_recompute_gear()
	_emit("equip",hero.position,{"slot":slot,"unequipped":true,"stats":_gear_stats.duplicate(true)})
	return true

func _recompute_gear() -> void:
	_gear_stats.clear()
	for item in inventory:
		if equipped.get(item.slot,-1) != item.uid: continue
		for stat in item.stats:
			_gear_stats[stat] = int(_gear_stats.get(stat,0))+int(item.stats[stat])
	hero.max_hp_raw = 120*UNIT+int(_gear_stats.get("max_hp_raw",0))
	hero.hp_raw = mini(int(hero.hp_raw),int(hero.max_hp_raw))

func effective_skill(id_: String) -> Dictionary:
	var value: Dictionary = growth.effective_skill(id_)
	if value.is_empty(): return {}
	var effect: Dictionary = value.effects
	var additional := int(_gear_stats.get("projectiles",0))
	if effect.projectiles > 0: effect.projectiles = mini(16,int(effect.projectiles)+additional)
	else: effect.chain_targets = mini(32,int(effect.chain_targets)+additional)
	effect.chain_targets = mini(32,int(effect.chain_targets)+int(_gear_stats.get("chain_targets",0)))
	if int(effect.shatter_count) > 0: effect.shatter_count = mini(16,int(effect.shatter_count)+int(_gear_stats.get("shatter_count",0)))
	effect.damage_raw = int(effect.damage_raw)*(10000+int(_gear_stats.get("damage_bps",0)))/10000
	effect.cooldown_ticks = maxi(12,int(effect.cooldown_ticks)*10000/(10000+int(_gear_stats.get("cooldown_bps",0))))
	# Equipment augments attack shape, but cannot escape a cast's global damage budget.
	effect.hit_budget = mini(128,int(effect.hit_budget)+additional*8+int(_gear_stats.get("chain_targets",0))*2)
	return value

func compare_item(uid: int) -> Dictionary:
	for item in inventory:
		if item.uid != uid: continue
		var current: Dictionary = {}
		for owned in inventory:
			if equipped.get(item.slot,-1) == owned.uid: current = owned.duplicate(true)
		return {"candidate":item.duplicate(true),"equipped":current}
	return {}

func step(move: Vector2 = Vector2.ZERO) -> void:
	if mode != "playing": return
	events.clear()
	tick += 1
	if not move.is_finite(): move = Vector2.ZERO
	var direction := move.limit_length(1.0)
	if direction.length_squared() > .001: hero.direction = direction.normalized()
	var displacement: Vector2 = direction*float(hero.speed)*STEP
	if tick <= _dash_until: displacement = _dash_direction*13.5*STEP
	hero.position = _clamp_point(hero.position+displacement)
	_spawn_wave()
	_step_enemies()
	if _terminal_mode == "defeat": return
	_rebuild_grid()
	_auto_casts()
	_step_projectiles()
	if not _terminal_mode.is_empty():
		_update_metrics()
		return
	_collect_pickups()
	_cleanup()
	_refresh_mode()
	_update_metrics()

func _clamp_point(point: Vector2) -> Vector2:
	return Vector2(clampf(point.x,-BOUND,BOUND),clampf(point.y,-BOUND,BOUND))

func _spawn(kind: String, point: Vector2) -> bool:
	if enemies.size() >= MAX_ENTITIES: return false
	var def: Dictionary = ENEMY_DEFS[kind]
	_enemy_sequence += 1
	var hp: int = int(def.hp)*UNIT
	if kind == "walker" and tick > 35*HZ: hp = 18*UNIT
	var entity := {"id":_enemy_sequence,"generation":_epoch,"kind":kind,"position":_clamp_point(point),
		"hp_raw":hp,"max_hp_raw":hp,"radius":def.radius,"state":"move","telegraph":{},"elite":kind=="elite",
		"state_until":0,"frozen_until":0,"slow_until":0,"slow_bps":0,"freeze_stacks":0,"freeze_expires":0,
		"direction":Vector2.UP,"attack_direction":Vector2.UP,"attack_kind":"","attack_index":0,"dash_until":0,"dead_tick":-1,"attacked":false}
	enemies[entity.id] = entity
	_emit("spawn",entity.position,{"target_id":entity.id,"kind":kind,"elite":entity.elite})
	return true

func _spawn_point(min_radius: float, max_radius: float) -> Vector2:
	# Clamping an outside ring point at a corner must not spawn on top of the hero.
	for attempt in 12:
		var angle := _spawn_rng.randf_range(0,TAU)
		var candidate := _clamp_point(hero.position+Vector2(cos(angle),sin(angle))*_spawn_rng.randf_range(min_radius,max_radius))
		if candidate.distance_squared_to(hero.position) >= min_radius*min_radius*.64: return candidate
	var toward_center: Vector2 = -hero.position.normalized() if hero.position.length_squared() > .001 else Vector2.UP
	return _clamp_point(hero.position+toward_center*min_radius)

func _spawn_wave() -> void:
	if not _elite_spawned and tick >= ELITE_TICK:
		_elite_spawned = _spawn("elite",_spawn_point(7.0,8.0))
	if tick < _next_spawn: return
	var interval := 30 if tick < 15*HZ else (22 if tick < 35*HZ else 16)
	var amount := 2 if tick < 15*HZ else (3 if tick < 50*HZ else 4)
	_next_spawn = tick+interval
	var count := alive_count()
	for i in amount:
		if count >= MAX_ALIVE-1: break
		var point := _spawn_point(9.0,12.0)
		var roll := _spawn_rng.randi_range(0,99)
		var kind := "walker"
		if tick >= 12*HZ and roll >= 90: kind = "charger"
		elif tick >= 10*HZ and roll >= 72: kind = "ranged"
		if _spawn(kind,point): count += 1

func _step_enemies() -> void:
	# Explicit UID order makes approach steering independent of Dictionary insertion.
	# Windup/recovery/freeze anchors and active charge trajectories never get pushed.
	_rebuild_grid()
	var ids := enemies.keys()
	ids.sort()
	for id_ in ids:
		var e: Dictionary = enemies[id_]
		if e.hp_raw <= 0: continue
		if tick < int(e.frozen_until):
			# Freeze pauses attack/recovery motion time, not just the actor position.
			# Thaw cannot jump past an unseen windup and attack immediately.
			if e.state in ["windup","recover","dash"]: e.state_until += 1
			continue
		if tick > int(e.freeze_expires): e.freeze_stacks = 0
		var def: Dictionary = _enemy_definition(e)
		var delta: Vector2 = hero.position-e.position
		var distance := delta.length()
		var toward := delta/distance if distance > .001 else Vector2.UP
		e.direction = toward
		var speed: float = float(def.speed)
		if tick < int(e.slow_until): speed *= 1.0-float(e.slow_bps)/10000.0
		if e.state == "recover":
			if tick >= int(e.state_until): e.state = "move"
			else: continue
		if e.state == "dash":
			e.position = _clamp_point(e.position+e.attack_direction*9.0*STEP)
			if not e.attacked and e.position.distance_to(hero.position) <= float(e.radius)+.28:
				_hero_damage(int(def.damage)*UNIT,e.position)
				e.attacked = true
			if tick >= int(e.state_until):
				e.state = "recover"
				e.state_until = tick+int(def.recover)
			continue
		if e.state == "windup":
			e.telegraph.remaining_ticks = maxi(0,int(e.state_until)-tick)
			if tick < int(e.state_until): continue
			e.telegraph = {}
			metrics.enemy_attacks += 1
			_emit("enemy_attack",e.position,{"target_id":e.id,"kind":e.kind,"direction":e.attack_direction,"attack_kind":e.attack_kind})
			if e.kind == "ranged": _enemy_projectiles(e)
			elif e.kind == "charger":
				e.state = "dash"
				e.state_until = tick+32
				e.attacked = false
				continue
			elif e.kind == "elite":
				if e.attack_kind == "circle" and distance <= 3.4: _hero_damage(int(def.damage)*UNIT,e.position)
				elif e.attack_kind == "fan": _enemy_projectiles(e)
			else:
				if distance <= 1.15: _hero_damage(int(def.damage)*UNIT,e.position)
			e.attack_index += 1
			e.state = "recover"
			e.state_until = tick+int(def.recover)
			continue
		var attack_distance := .85
		if e.kind == "ranged": attack_distance = 6.0
		elif e.kind == "charger": attack_distance = 5.0
		elif e.kind == "elite": attack_distance = 3.0 if int(e.attack_index)%2 == 0 else 6.0
		var approach := _approach_crowd(e,speed,attack_distance)
		e.position = approach.position
		delta = hero.position-e.position
		distance = delta.length()
		toward = delta/distance if distance > .001 else toward
		e.direction = toward
		# The leading movable body claims a stance; queued bodies keep steering.
		# Paid windup/recovery/freeze/dash anchors always retain their attack space.
		if distance <= attack_distance and approach.room and distance >= float(e.radius)+HERO_RADIUS+HERO_APPROACH_GAP-.015:
			e.state = "windup"
			e.state_until = tick+int(def.windup)
			e.attack_direction = toward
			e.attack_kind = "line" if e.kind == "charger" else ("fan" if e.kind == "ranged" else ("circle" if int(e.attack_index)%2 == 0 else "fan") if e.elite else "circle")
			# Telegraphs describe the actual hero-center hazard, not the AI trigger range.
			# A charger is a swept capsule: center travel4.8m, radius .43+.28m.
			var hazard_radius := float(e.radius)+.28 if e.kind == "charger" else (3.4 if e.elite else 1.15)
			var hazard_length := 4.8 if e.kind == "charger" else (17.5 if e.elite else 14.7)
			var rays: Array[Vector2] = []
			if e.attack_kind == "fan":
				var count := 7 if e.elite else 3
				for ray in count: rays.append(toward.rotated((float(ray)-float(count-1)*.5)*(.18 if e.elite else .14)))
				hazard_radius = hazard_length+.44
			e.telegraph = {"shape":e.attack_kind,"direction":toward,"radius":hazard_radius,"length":hazard_length,"width":1.42 if e.kind == "charger" else .88,"rays":rays,"remaining_ticks":int(def.windup)}
		if _terminal_mode == "defeat": return

func _crowd_neighbors(point: Vector2, self_id: int) -> Array[int]:
	var result: Array[int] = []
	var cell := Vector2i(floori(point.x/2.0),floori(point.y/2.0))
	# Central cell first, then cardinal and diagonal cells. Every cell list is UID
	# ordered. The32-body work budget bounds pathological coincident crowds too.
	var offsets := [Vector2i.ZERO,Vector2i.LEFT,Vector2i.RIGHT,Vector2i.UP,Vector2i.DOWN,Vector2i(-1,-1),Vector2i(1,-1),Vector2i(-1,1),Vector2i(1,1)]
	var examined := 0
	for offset in offsets:
		for other_id in _grid.get(cell+offset,[]):
			if int(other_id) == self_id: continue
			examined += 1
			var other: Dictionary = enemies[other_id]
			if other.hp_raw > 0 and other.position.distance_squared_to(point) < CROWD_RADIUS*CROWD_RADIUS:
				result.append(int(other_id))
			if examined >= MAX_CROWD_NEIGHBORS: break
		if examined >= MAX_CROWD_NEIGHBORS: break
	metrics.crowd_neighbor_checks += examined
	metrics.crowd_peak_neighbors = maxi(int(metrics.crowd_peak_neighbors),examined)
	return result

func _coincident_away(self_id: int, other_id: int) -> Vector2:
	# No gameplay RNG is consumed by steering; a coincident pair gets opposite,
	# stable directions instead of both choosing UP and remaining interpenetrated.
	var key := (mini(self_id,other_id)*73856093) ^ (maxi(self_id,other_id)*19349663)
	var axis := Vector2.from_angle(float(key & 1023)*TAU/1024.0)
	return axis if self_id < other_id else -axis

func _approach_crowd(e: Dictionary, speed: float, attack_distance: float) -> Dictionary:
	var origin: Vector2 = e.position
	var toward_hero: Vector2 = hero.position-origin
	var distance := toward_hero.length()
	var movement := toward_hero/distance*speed*STEP if distance > maxf(attack_distance,.001) else Vector2.ZERO
	var neighbors := _crowd_neighbors(origin,int(e.id))
	var pressure := Vector2.ZERO
	for other_id in neighbors:
		var other: Dictionary = enemies[other_id]
		var away: Vector2 = origin-other.position
		var separation := away.length()
		var desired := float(e.radius)+float(other.radius)+CROWD_GAP
		if separation >= desired: continue
		var direction := away/separation if separation > .0001 else _coincident_away(int(e.id),other_id)
		pressure += direction*(desired-separation)*.5
	var candidate := _clamp_point(origin+movement+pressure.limit_length(CROWD_PUSH_PER_STEP))
	var clearance := float(e.radius)+HERO_RADIUS+HERO_APPROACH_GAP
	var hero_away: Vector2 = candidate-hero.position
	if hero_away.length() < clearance:
		var direction := hero_away.normalized() if hero_away.length_squared() > .000001 else _coincident_away(int(e.id),0)
		var desired := _clamp_point(hero.position+direction*clearance)
		if desired.distance_to(hero.position) < clearance-.015:
			# At a world corner prefer the inward legal arc, never teleport outside.
			direction = -hero.position.normalized() if hero.position.length_squared() > .001 else direction
			desired = _clamp_point(hero.position+direction*clearance)
		candidate = _clamp_point(candidate+(desired-candidate).limit_length(CROWD_PUSH_PER_STEP))
	# Combined peer/hero correction still has one documented displacement bound.
	candidate = _clamp_point(origin+(candidate-origin).limit_length(speed*STEP+CROWD_PUSH_PER_STEP))
	var room := true
	for other_id in neighbors:
		var other: Dictionary = enemies[other_id]
		var minimum := (float(e.radius)+float(other.radius))*.92
		if candidate.distance_squared_to(other.position) < minimum*minimum:
			# Requiring all movable peers to be clear makes a compressed corner
			# queue wait forever. The front body claims the stance and rear bodies
			# yield to its anchored windup. Stable UID resolves equal-distance ties.
			var our_distance := candidate.distance_to(hero.position)
			var their_distance: float = other.position.distance_to(hero.position)
			var anchored: bool = other.state != "move" or tick < int(other.frozen_until)
			if anchored or their_distance < our_distance-.001 or (absf(their_distance-our_distance) <= .001 and int(other.id) < int(e.id)):
				room = false
				break
	if candidate.distance_squared_to(origin+movement) > .000001: metrics.crowd_adjustments += 1
	return {"position":candidate,"room":room}

func _hero_damage(raw: int, from: Vector2) -> void:
	if tick < _invulnerable_until or not _terminal_mode.is_empty(): return
	var result: Dictionary = Resolver.damage(raw,int(hero.hp_raw),0,int(_gear_stats.get("damage_reduction_bps",0)))
	hero.hp_raw = int(result.hp_after_raw)
	_invulnerable_until = tick+24
	_emit("hero_hit",hero.position,{"damage_raw":result.total_raw,"from":from})
	if hero.hp_raw <= 0:
		_terminal_mode = "defeat"
		_refresh_mode()
		_emit("defeat",hero.position)

func _enemy_projectiles(e: Dictionary) -> void:
	var hostile := 0
	for p in projectiles:
		if p.hostile: hostile += 1
	var count := 7 if e.elite else 3
	for i in count:
		if hostile >= MAX_HOSTILE_PROJECTILES or projectiles.size() >= MAX_PROJECTILES: break
		var spread: float = (float(i)-float(count-1)*.5)*(.18 if e.elite else .14)
		_projectile_sequence += 1
		projectiles.append({"uid":_projectile_sequence,"position":e.position,"previous":e.position,"direction":e.attack_direction.rotated(spread),
			"speed":5.0 if e.elite else 4.2,"radius":.16,"skill_id":"hostile."+e.kind,"hostile":true,"damage_raw":int(_enemy_definition(e).damage)*UNIT,"expires":tick+210,"cast_id":0,"pierce_left":0,"hit_ids":[]})
		hostile += 1

func _rebuild_grid() -> void:
	_grid.clear()
	var ids := enemies.keys()
	ids.sort()
	for id_ in ids:
		var e: Dictionary = enemies[id_]
		if e.hp_raw <= 0: continue
		var cell := Vector2i(floori(e.position.x/2.0),floori(e.position.y/2.0))
		if not _grid.has(cell): _grid[cell] = []
		_grid[cell].append(int(e.id))

func _near(point: Vector2, radius: float) -> Array[int]:
	var result: Array[int] = []
	var low := Vector2i(floori((point.x-radius)/2.0),floori((point.y-radius)/2.0))
	var high := Vector2i(floori((point.x+radius)/2.0),floori((point.y+radius)/2.0))
	for x in range(low.x,high.x+1):
		for y in range(low.y,high.y+1):
			for id_ in _grid.get(Vector2i(x,y),[]):
				var e: Dictionary = enemies[id_]
				if e.hp_raw > 0 and e.position.distance_squared_to(point) <= radius*radius: result.append(id_)
	result.sort_custom(func(a: int,b: int) -> bool:
		var da: float = enemies[a].position.distance_squared_to(point)
		var db: float = enemies[b].position.distance_squared_to(point)
		return a < b if is_equal_approx(da,db) else da < db)
	return result

func _auto_casts() -> void:
	for id_ in SKILL_IDS:
		if tick < int(_next_cast.get(id_,0)): continue
		var skill := effective_skill(id_)
		if skill.is_empty(): continue
		var nearest := _near(hero.position,13.0)
		if nearest.is_empty(): continue
		var target: Dictionary = enemies[nearest[0]]
		var direction: Vector2 = (target.position-hero.position).normalized()
		var effects: Dictionary = skill.effects.duplicate(true)
		_cast_sequence += 1
		var context := {"uid":_cast_sequence,"skill_id":id_,"effects":effects,"remaining_hits":int(effects.hit_budget),"hit_ids":[],"evolved":skill.evolved}
		_contexts[context.uid] = context
		_next_cast[id_] = tick+int(effects.cooldown_ticks)
		metrics.casts[id_] = int(metrics.casts.get(id_,0))+1
		if id_ == "chapter1.skill.arc":
			var positions := _chain(target,context)
			_emit("cast",hero.position,{"skill_id":id_,"direction":direction,"effects":effects.duplicate(true),"targets":positions,"evolved":skill.evolved})
			_contexts.erase(context.uid)
		else:
			_emit("cast",hero.position,{"skill_id":id_,"direction":direction,"effects":effects.duplicate(true),"targets":[],"evolved":skill.evolved})
			var count: int = effects.projectiles
			for i in count:
				if projectiles.size() >= MAX_PROJECTILES: break
				_projectile_sequence += 1
				var spread := (float(i)-float(count-1)*.5)*.16
				projectiles.append({"uid":_projectile_sequence,"position":hero.position,"previous":hero.position,"direction":direction.rotated(spread),
					"speed":14.0 if id_ == "chapter1.skill.ember" else 16.0,"radius":.24 if skill.evolved else .16,"skill_id":id_,"hostile":false,
					"damage_raw":int(effects.damage_raw),"expires":tick+100,"cast_id":int(context.uid),"pierce_left":int(effects.pierce),"hit_ids":[]})

func _chain(first: Dictionary, context: Dictionary) -> Array[Vector2]:
	var positions: Array[Vector2] = []
	var effects: Dictionary = context.effects
	var origin: Vector2 = hero.position
	var preferred := int(first.id)
	for branch in int(effects.branches):
		var at := origin
		for bounce in int(effects.chain_targets):
			var target_id := -1
			if branch == 0 and bounce == 0: target_id = preferred
			else:
				for id_ in _near(at,float(effects.radius_cm)/100.0):
					if not id_ in context.hit_ids:
						target_id = id_
						break
			if target_id < 0 or int(context.remaining_hits) <= 0: break
			var target: Dictionary = enemies[target_id]
			positions.append(target.position)
			at = target.position
			_damage_enemy(target_id,context,0)
	return positions

func _segment_distance_sq(point: Vector2, start_: Vector2, end_: Vector2) -> float:
	var line := end_-start_
	var t := clampf((point-start_).dot(line)/maxf(line.length_squared(),.000001),0,1)
	return point.distance_squared_to(start_+line*t)

func _step_projectiles() -> void:
	var remaining: Array[Dictionary] = []
	for p in projectiles:
		if not _terminal_mode.is_empty(): break
		if tick >= int(p.expires): continue
		p.previous = p.position
		p.position += p.direction*float(p.speed)*STEP
		var remove := false
		if p.hostile:
			if _segment_distance_sq(hero.position,p.previous,p.position) <= pow(float(p.radius)+.28,2):
				_hero_damage(int(p.damage_raw),p.position)
				remove = true
		else:
			if not _contexts.has(p.cast_id): continue
			var context: Dictionary = _contexts[p.cast_id]
			var midpoint: Vector2 = (p.previous+p.position)*.5
			var query_radius: float = p.previous.distance_to(p.position)*.5+float(p.radius)+1.0
			for id_ in _near(midpoint,query_radius):
				if id_ in p.hit_ids: continue
				var e: Dictionary = enemies[id_]
				if _segment_distance_sq(e.position,p.previous,p.position) > pow(float(e.radius)+float(p.radius),2): continue
				p.hit_ids.append(id_)
				_damage_enemy(id_,context,0)
				if p.skill_id == "chapter1.skill.ember" and context.effects.radius_cm > 0:
					_emit("explosion",p.position,{"skill_id":p.skill_id,"radius_cm":context.effects.radius_cm,"cast_uid":context.uid,"evolved":context.evolved})
					_area_hit(p.position,float(context.effects.radius_cm)/100.0,context,id_,0)
				if int(p.pierce_left) <= 0 or int(context.remaining_hits) <= 0:
					remove = true
					break
				p.pierce_left -= 1
		if not remove: remaining.append(p)
	projectiles = remaining
	var active: Dictionary = {}
	for p in projectiles:
		if not p.hostile: active[p.cast_id] = true
	for uid in _contexts.keys():
		if not active.has(uid): _contexts.erase(uid)

func _area_hit(position: Vector2, radius: float, context: Dictionary, exclude: int, depth: int) -> void:
	for id_ in _near(position,radius):
		if id_ == exclude or int(context.remaining_hits) <= 0: continue
		_damage_enemy(id_,context,depth)

func _damage_enemy(id_: int, context: Dictionary, depth: int) -> void:
	if not _terminal_mode.is_empty() or not enemies.has(id_) or int(context.remaining_hits) <= 0: return
	var e: Dictionary = enemies[id_]
	if e.hp_raw <= 0 or e.generation != _epoch: return
	# Arc has one hit per entity across both direct branches and death procs in a cast.
	# Fire/frost may hit an entity with separate projectiles, each with its own hit_ids.
	if context.skill_id == "chapter1.skill.arc":
		if id_ in context.hit_ids: return
		context.hit_ids.append(id_)
	context.remaining_hits -= 1
	var effect: Dictionary = context.effects
	var was_frozen: bool = tick < int(e.frozen_until)
	var result: Dictionary = Resolver.damage(int(effect.damage_raw),int(e.hp_raw))
	e.hp_raw = int(result.hp_after_raw)
	metrics.damage_raw += int(result.total_raw)
	metrics.hits[context.skill_id] = int(metrics.hits.get(context.skill_id,0))+1
	if context.skill_id == "chapter1.skill.frost":
		e.slow_until = tick+100
		e.slow_bps = int(effect.slow_bps)
		if int(effect.freeze_stacks) > 0:
			e.freeze_stacks += 1
			e.freeze_expires = tick+180
			if int(e.freeze_stacks) >= int(effect.freeze_stacks):
				e.frozen_until = tick+(12 if e.elite else 75)
				e.freeze_stacks = 0
	_emit("hit",e.position,{"target_id":id_,"skill_id":context.skill_id,"damage_raw":int(result.total_raw),"frozen":tick<int(e.frozen_until),"shatter":was_frozen and int(effect.shatter_count)>0,
		"radius_cm":int(effect.radius_cm),"blast_radius_cm":int(effect.radius_cm) if context.skill_id == "chapter1.skill.ember" else 0,"cast_uid":context.uid,"evolved":context.evolved})
	if e.hp_raw > 0: return
	e.state = "dead"
	e.dead_tick = tick
	e.telegraph = {}
	kills += 1
	_emit("death",e.position,{"target_id":id_,"kind":e.kind,"elite":e.elite,"skill_id":context.skill_id})
	_drop_orb(e.position,int(_enemy_definition(e).xp))
	_maybe_drop_item(e)
	if depth < int(effect.proc_depth) and int(effect.death_burst) > 0:
		# Arc radius_cm means chain search reach, never the residual pulse size.
		var burst_radius := 3.0 if context.skill_id == "chapter1.skill.arc" else maxf(1.5,float(effect.radius_cm)/100.0)
		_emit("explosion",e.position,{"skill_id":context.skill_id,"radius_cm":int(burst_radius*100),"cast_uid":context.uid,"evolved":context.evolved,"proc":true})
		_area_hit(e.position,burst_radius,context,id_,depth+1)
	if was_frozen and int(effect.shatter_count) > 0 and depth == 0:
		_emit("shatter",e.position,{"skill_id":context.skill_id,"radius_cm":350,"count":int(effect.shatter_count),"cast_uid":context.uid,"evolved":context.evolved})
		var remaining: int = effect.shatter_count
		for other in _near(e.position,3.5):
			if other == id_ or remaining <= 0: continue
			_damage_enemy(other,context,1)
			remaining -= 1
	if e.elite:
		_on_elite_defeated(e)

func _enemy_definition(e: Dictionary) -> Dictionary:
	return ENEMY_DEFS[e.kind]

func _on_elite_defeated(_e: Dictionary) -> void:
	# The representative encounter ends here. The full chapter overrides only
	# this objective hook; damage, proc budgets and actual kill still happen above.
	_elite_killed = true
	_terminal_mode = "victory"
	_refresh_mode()
	_emit("victory",hero.position,{"kills":kills,"elapsed":elapsed()})

func _drop_orb(position: Vector2, amount: int) -> void:
	if orbs.size() >= MAX_ORBS:
		orbs[orbs.size()-1].amount += amount
		metrics.orbs_merged += 1
		return
	_orb_sequence += 1
	orbs.append({"uid":_orb_sequence,"position":position,"amount":amount})

func _maybe_drop_item(e: Dictionary) -> void:
	var thresholds := [6,24,55,100]
	var forced: bool = _guaranteed_drops < thresholds.size() and kills >= int(thresholds[_guaranteed_drops])
	if not e.elite and not forced and _loot_rng.randi_range(0,99) != 0: return
	if e.elite:
		# Objective reward is directly owned, independent of ground/ordinary capacity.
		# There is only one objective in this run; the reserved slot bounds total65.
		if _elite_reward_uid != 0 or inventory.size() >= MAX_INVENTORY+MAX_OBJECTIVE_REWARDS: return
	elif items.size() >= MAX_GROUND_ITEMS or inventory.size() >= MAX_INVENTORY: return
	var template_index := _guaranteed_drops if forced else _loot_rng.randi_range(0,ITEM_TEMPLATES.size()-1)
	if forced: _guaranteed_drops += 1
	_item_sequence += 1
	var item: Dictionary = ITEM_TEMPLATES[template_index].duplicate(true)
	item.uid = _item_sequence
	item.position = e.position
	item.quality = "rare" if e.elite else ("magic" if template_index != 1 else "common")
	item.collected = false
	if e.elite: item.objective_reward = true
	item.drop_tick = tick
	# Distinct bounded rolls provide a comparison without changing the guaranteed shape effect.
	if item.stats.has("damage_bps"): item.stats.damage_bps += _loot_rng.randi_range(0,5)*100
	if item.stats.has("max_hp_raw"): item.stats.max_hp_raw += _loot_rng.randi_range(0,5)*UNIT
	metrics.dropped_items += 1
	_emit("item_drop",item.position,{"item":item.duplicate(true)})
	if e.elite:
		item.collected = true
		_elite_reward_uid = int(item.uid)
		inventory.append(item)
		metrics.picked_items += 1
		_emit("item_pickup",hero.position,{"item":item.duplicate(true)})
	else: items.append(item)

func _collect_pickups() -> void:
	var radius := 1.3+float(_gear_stats.get("pickup_radius_cm",0))/100.0
	var leftover: Array[Dictionary] = []
	for orb in orbs:
		var delta: Vector2 = hero.position-orb.position
		var distance := delta.length()
		if distance < radius+2.0:
			orb.position += delta.normalized()*minf(distance,9.0*STEP)
		if orb.position.distance_squared_to(hero.position) <= radius*radius:
			growth.award_xp(int(orb.amount))
			metrics.collected_xp += int(orb.amount)
			_emit("xp_pickup",orb.position,{"amount":orb.amount})
		else: leftover.append(orb)
	orbs = leftover
	var ground: Array[Dictionary] = []
	for item in items:
		if item.position.distance_squared_to(hero.position) <= pow(radius+.3,2) and inventory.size() < MAX_INVENTORY:
			item.collected = true
			inventory.append(item)
			metrics.picked_items += 1
			_emit("item_pickup",hero.position,{"item":item.duplicate(true)})
		elif tick-int(item.drop_tick) < 180*HZ: ground.append(item)
	items = ground
	if not growth.snapshot().pending_levels.is_empty():
		_emit("level_choice",hero.position,{"level":growth.snapshot().level})

func _cleanup() -> void:
	for id_ in enemies.keys():
		var e: Dictionary = enemies[id_]
		if e.hp_raw <= 0 and tick-int(e.dead_tick) > 75: enemies.erase(id_)
		elif e.hp_raw > 0 and e.position.distance_squared_to(hero.position) > 25.0*25.0 and not e.elite and e.state == "move" and tick >= int(e.frozen_until):
			# Recycle only a freely approaching survivor. A paid windup, dash,
			# recovery or frozen body keeps its attack/telegraph origin until it
			# returns to movement; relocation never creates another reward identity.
			e.position = _spawn_point(12.0,12.0)

func _update_metrics() -> void:
	metrics.max_alive = maxi(int(metrics.max_alive),alive_count())
	metrics.peak_projectiles = maxi(int(metrics.peak_projectiles),projectiles.size())

func _emit(type: String, position: Vector2, details: Dictionary = {}) -> void:
	_event_sequence += 1
	var event := details.duplicate(true)
	event.type = type
	event.position = position
	event.tick = tick
	event.seq = _event_sequence
	if events.size() >= MAX_EVENTS:
		events.pop_front()
		metrics.events_dropped = int(metrics.get("events_dropped",0))+1
	events.append(event)

func snapshot() -> Dictionary:
	return {"mode":mode,"tick":tick,"kills":kills,"hero":hero.duplicate(true),"enemies":enemies.duplicate(true),
		"projectiles":projectiles.duplicate(true),"orbs":orbs.duplicate(true),"items":items.duplicate(true),
		"inventory":inventory.duplicate(true),"equipped":equipped.duplicate(true),"growth":growth.snapshot(),
		"metrics":metrics.duplicate(true),"elite_spawned":_elite_spawned,"elite_killed":_elite_killed,
		"next_dash_tick":_next_dash,"epoch":_epoch,"elite_reward_uid":_elite_reward_uid}
