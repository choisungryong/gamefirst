extends SceneTree
# Candidate03 targeted fixtures. Direct test setup is deliberately synthetic.
const Run = preload("res://chapter1/core/combat_run.gd")
var checks := 0
var failures: Array[String] = []
var observations: Array[Dictionary] = []

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures.append(label)

func fresh() -> RefCounted:
	var r = Run.new()
	r.start(71)
	r.enemies.clear()
	r.events.clear()
	r._next_spawn = 999999
	r._rebuild_grid()
	return r

func item(uid: int, pos: Vector2 = Vector2.ZERO) -> Dictionary:
	var result: Dictionary = Run.ITEM_TEMPLATES[(uid-1)%4].duplicate(true)
	result.uid = uid
	result.position = pos
	result.drop_tick = 0
	result.collected = false
	result.quality = "magic"
	return result

func context(r: RefCounted) -> Dictionary:
	var fx: Dictionary = r.effective_skill(Run.SKILL_IDS[0]).effects
	fx.damage_raw = 1000000
	return {"uid":999,"skill_id":Run.SKILL_IDS[0],"effects":fx,"remaining_hits":int(fx.hit_budget),"hit_ids":[],"evolved":false}

func kill_elite(r: RefCounted) -> int:
	r._spawn("elite",Vector2(10,0))
	r._rebuild_grid()
	var id_: int = r._enemy_sequence
	r._damage_enemy(id_,context(r),0)
	return id_

func _initialize() -> void:
	for owned in [0,63,64]:
		var r = fresh()
		for i in owned: r.inventory.append(item(i+1))
		for i in 32: r.items.append(item(owned+i+1,Vector2(18,18)))
		r._item_sequence = owned+32
		if owned > 0:
			r.open_inventory()
			r.equip(1)
			r.close_inventory()
		var old_inventory: Array = r.inventory.duplicate(true)
		var old_ground: Array = r.items.duplicate(true)
		var old_equipped: Dictionary = r.equipped.duplicate(true)
		var elite_id := kill_elite(r)
		var reward: Dictionary = r.inventory.back()
		check(r.mode == "victory" and r.inventory.size() == owned+1,"ground32 independent elite owned reward at owned"+str(owned))
		check(r.items == old_ground,"elite reward does not evict or modify ground gear at owned"+str(owned))
		check(r.inventory.slice(0,owned) == old_inventory and r.equipped == old_equipped,"elite reward preserves every old UID/item/equip at owned"+str(owned))
		check(reward.uid == owned+33 and reward.quality == "rare" and reward.collected,"elite reward has unique next UID and owned metadata at owned"+str(owned))
		var old_count: int = r.inventory.size()
		var old_pickups: int = r.metrics.picked_items
		var old_drops: int = r.metrics.dropped_items
		var old_orbs: int = r.orbs.size()
		r._damage_enemy(elite_id,context(r),0)
		check(r.inventory.size() == old_count and r.metrics.picked_items == old_pickups and r.metrics.dropped_items == old_drops and r.orbs.size() == old_orbs and r.kills == 1,"repeated elite corpse damage grants no second reward at owned"+str(owned))
		var compared: Dictionary = r.compare_item(reward.uid)
		check(compared.candidate.uid == reward.uid,"overflow reward remains available to compare at owned"+str(owned))
		check(r.open_inventory() and r.equip(reward.uid) and r.equipped[reward.slot] == reward.uid,"overflow reward uses existing victory inventory equip API at owned"+str(owned))
		r.close_inventory()
		check(r.mode == "victory","reward inventory closes back to victory at owned"+str(owned))
		observations.append({"owned_before":owned,"ground_count":r.items.size(),"owned_after":r.inventory.size(),"reward_uid":reward.uid,"equip_slot":reward.slot})

	# Ordinary pickups cannot occupy the dedicated objective allowance.
	var r = fresh()
	for i in 63: r.inventory.append(item(i+1))
	r.items.append(item(64))
	r.items.append(item(65))
	r._item_sequence = 65
	r._collect_pickups()
	check(r.inventory.size() == 64 and r.items.size() == 1 and r.items[0].uid == 65,"ordinary pickup stops at64 without consuming pending ground item")
	var before: Array = r.inventory.duplicate(true)
	kill_elite(r)
	check(r.inventory.size() == 65 and r.inventory.slice(0,64) == before,"actual ordinary64 then elite path yields bounded65 without replacement")
	r.hero.position = Vector2.ZERO
	r._collect_pickups()
	check(r.inventory.size() == 65 and r.items.size() == 1,"ordinary pickup cannot expand owned65")
	check(r.snapshot().inventory.size() == 65,"snapshot exposes objective overflow as ordinary owned gear")
	check(r.start(907) and r.inventory.is_empty() and r.items.is_empty(),"new run resets reserve through existing start without profile I/O")

	# Exact dash movement count and map boundaries after requested duration correction.
	r = fresh()
	check(r.request_dash(Vector2.RIGHT),"dash accepted for duration fixture")
	var moving := 0
	for i in 12:
		var p: Vector2 = r.hero.position
		r.step(Vector2.ZERO)
		if r.hero.position != p: moving += 1
	check(moving == 12 and absf(r.hero.position.x-2.7)<.0001,"dash moves exactly12 fixed steps for2.7m")
	var at_end: Vector2 = r.hero.position
	r.step(Vector2.ZERO)
	check(r.hero.position == at_end,"dash stops on13th step with zero input")
	for corner in [Vector2(19,19),Vector2(-19,19),Vector2(-19,-19),Vector2(19,-19)]:
		r = fresh()
		r.hero.position = corner
		r.request_dash(corner.normalized())
		for i in 12: r.step(corner.normalized())
		check(absf(r.hero.position.x)<=19 and absf(r.hero.position.y)<=19,"dash clamps world corner"+str(corner))
		var safe := true
		for i in 100:
			var p: Vector2 = r._spawn_point(9,12)
			if absf(p.x)>19 or absf(p.y)>19 or p.distance_to(r.hero.position)<7.2-.0001: safe = false
		check(safe,"spawn rejection preserves safety and bounds at corner"+str(corner))

	r = fresh()
	r._spawn("ranged",Vector2(5,0))
	var e: Dictionary = r.enemies[r._enemy_sequence]
	for i in 100: r._enemy_projectiles(e)
	check(r.projectiles.size() == 192,"hostile projectile allocation hard cap192")
	print("CANDIDATE03_REWARD_BOUNDS ",JSON.stringify({"checks":checks,"failures":failures,"observations":observations,"scope":"synthetic candidate03 overflow/duration/bounds fixtures; not normal play"}))
	quit(0 if failures.is_empty() else 1)
