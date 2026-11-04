extends SceneTree
## Independent contract tests. Isolated evidence files only; never user saves.
const Sim = preload("res://baseline_sim.gd")
const Loot = preload("res://data/loot_catalog.gd")
const Progress = preload("res://data/progression.gd")
var checks := 0
var failures: Array[String] = []

func _initialize() -> void: call_deferred("run")
func check(ok: bool, text: String) -> void:
	checks += 1
	if not ok:
		failures.append(text)
		printerr("PHASE6 INDEPENDENT FAILED: "+text)

func fresh() -> RefCounted:
	var s = Sim.new()
	s.reset(0)
	s.enemy_ai = false
	return s

func state(s: RefCounted) -> Dictionary:
	return {"document":s.progress_document(),"context":s.equipment_context(),"epoch":s._loot_epoch,"floor":s._generation_floor,"life":s.life,"mana":s.mana_raw,"stats":s.player_stats_snapshot(),"tick":s.tick,"damage_rng":str(s.rng.state),"generations":s.generations.duplicate(true),"enemies":s.enemies.duplicate(true),"history":s.history_snapshot(),"progress_history":s.progress_history_snapshot(),"progress_events":s.progress_events.duplicate(true),"pending":s.pending_context_snapshot(),"paused":s.paused}

func kill(s: RefCounted, position: Vector2 = Vector2(10,10)) -> Dictionary:
	var h: Dictionary = s.spawn_enemy(position)
	if h.is_empty(): return {}
	var target: Dictionary = s.entity(h)
	target.life_raw = 1
	var context: Dictionary = s._make_context("skill.ember_bolt")
	context["shot"] = 1
	s._apply_damage(target,context,position)
	return h

func reward_cases() -> void:
	var s = fresh()
	check(s.progression_snapshot().xp == 0 and s.progression_snapshot().level == 1,"initial XP and level")
	var alive: Dictionary = s.spawn_enemy(Vector2(10,10))
	var before: Dictionary = state(s)
	check(not s.claim_death_reward(alive) and state(s) == before,"living identity cannot claim rewards")
	check(not s.claim_death_reward({"id":999999,"generation":1}) and state(s) == before,"unknown identity cannot claim rewards")
	s.despawn_enemy(alive)
	s.life = 17
	s.mana_raw = 1234
	var stats: Dictionary = s.player_stats_snapshot()
	var h: Dictionary = kill(s)
	check(s.progression_snapshot().xp == 3 and s.progression_snapshot().level == 1,"one actual death gives three XP")
	before = state(s)
	for i in range(10):
		check(not s.claim_death_reward(h) and state(s) == before,"duplicate death claim is atomic "+str(i))
	check(s.life == 17 and s.mana_raw == 1234,"death rewards do not heal")
	var old_id: int = h.id
	s.despawn_enemy(h)
	h = kill(s)
	check(h.id == old_id and s.progression_snapshot().xp == 6 and s.progression_snapshot().level == 2,"reused slot new generation gets reward and unlocks level2")
	check(s.equipment_context().level == 2 and s.equip_item(3),"XP level unlocks actual charm requirement")
	check(s.life == 17 and s.mana_raw == 1234,"level and equip do not restore current vitals")
	s.unequip_item("charm")
	check(s.player_stats_snapshot() == stats,"level2 changes no base combat stats")
	for i in range(4): kill(s)
	check(s.progression_snapshot().xp == 18 and s.progression_snapshot().level == 3,"six deaths reach level3 at cumulative eighteen")
	var inventory: Dictionary = s.equipment_snapshot()
	var xp: Dictionary = s.progression_snapshot()
	var stale: Dictionary = {}
	if not s.ground_loot_snapshot().is_empty(): stale = s.loot_handle(s.ground_loot_snapshot()[0].uid)
	s.reset(0)
	check(s.progression_snapshot() == xp and s.equipment_snapshot() == inventory,"R preserves XP/equipment/UID/item RNG")
	check(s.ground_loot_snapshot().is_empty(),"R clears ground loot")
	check(not s.claim_death_reward(h),"R invalidates old death handle")
	if not stale.is_empty(): check(not s.pickup_loot(stale),"R invalidates old ground handle")
	for i in range(120):
		var dead: Dictionary = kill(s)
		s.despawn_enemy(dead)
	check(s.ground_loot_snapshot().size() <= 32,"ground bounded to32 under120 deaths")
	check(s.progression_snapshot().xp == 378,"ground capacity cannot suppress XP")
	check(s.progress_history_snapshot().size() <= 256,"reward history bounded to256")

func profile_cases() -> void:
	var s = fresh()
	for i in range(10): kill(s)
	s.life = 9
	s.mana_raw = 456
	var saved: Dictionary = s.progress_document()
	check(not saved.is_empty(),"progress document includes complete profile")
	var before: Dictionary = state(s)
	for candidate in [null, [], {}, {"schema_version":999}]:
		check(not s.replace_progress_document(candidate) and state(s) == before,"malformed profile rejects atomically "+str(candidate))
	for field in saved.keys():
		var malformed: Dictionary = saved.duplicate(true)
		malformed.erase(field)
		check(not s.replace_progress_document(malformed) and state(s) == before,"missing profile field atomic "+str(field))
	var unknown: Dictionary = saved.duplicate(true)
	unknown["unknown_field"] = 1
	check(not s.replace_progress_document(unknown) and state(s) == before,"unknown profile field rejects atomically")
	check(s.replace_progress_document(saved),"valid complete profile accepted")
	check(s.life == 9 and s.mana_raw == 456,"complete profile load preserves absolute vitals")
	check(s.progression_snapshot().xp == 30,"complete profile roundtrip preserves XP")
	var post: Dictionary = kill(s)
	check(not post.is_empty() and s.progression_snapshot().xp == 33,"new enemy after load rewards normally")
	check(not s.claim_death_reward(post),"new post-load death still rewards once")
	var folder := "res://evidence/phase7/verification-independent/storage-"+str(OS.get_process_id())+"-"+str(Time.get_ticks_usec())
	check(DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(folder)) == OK,"isolated storage folder")
	var path: String = folder+"/progress.json"
	before = state(s)
	check(s.save_progress(path) and state(s) == before,"save leaves full gameplay state unchanged")
	var bytes: String = FileAccess.get_file_as_string(path)
	check(not bytes.is_empty() and JSON.parse_string(bytes) is Dictionary,"saved profile is readable JSON")
	check(s.save_progress(path),"second save succeeds and preserves prior file")
	var backups := 0
	for name_ in DirAccess.open(folder).get_files():
		if name_.ends_with(".previous"):
			backups += 1
			check(FileAccess.get_file_as_string(folder+"/"+name_) == bytes,"previous save exact bytes retained")
	check(backups == 1,"one prior file retained for replacement")
	check(s.load_progress(path) and s.life == 9 and s.mana_raw == 456,"file load preserves vitals")
	before = state(s)
	for unsupported in ["user://equipment-v1.json","res://game_data/catalog.json",folder+"/../escape.json",folder+"/wrong.txt"]:
		check(not s.save_progress(unsupported) and state(s) == before,"unsupported save path leaves state unchanged "+unsupported)
	var broken: String = folder+"/broken.json"
	var f := FileAccess.open(broken,FileAccess.WRITE)
	f.store_string("{broken")
	f.close()
	check(not s.load_progress(broken) and state(s) == before and FileAccess.get_file_as_string(broken) == "{broken","malformed file preserves memory and input bytes")

func catalog_cases() -> void:
	var s = fresh()
	var c = Loot.new(s.equipment_catalog)
	check(c.load_file(),"independent loot definition loads")
	var original: Dictionary = c.snapshot()
	for entries in [[],[{"kind":"no-drop","weight":0}],[{"kind":"no-drop","weight":-1}],[{"kind":"no-drop","weight":1.5}],[{"kind":"table","weight":1,"table_id":"loot.prototype"}],[{"kind":"item","weight":1,"base_id":"unknown","quality":"common"}],[{"kind":"item","weight":1,"base_id":"item.ember_focus","quality":"rare"}],[{"kind":"no-drop","weight":1,"reference":"cycle"}]]:
		var bad: Dictionary = original.duplicate(true)
		bad.entries = entries
		check(not c.replace_document(bad) and c.snapshot() == original,"invalid loot table rejected without mutation "+str(entries))
	var mutable: Dictionary = c.snapshot()
	mutable.entries.clear()
	check(c.snapshot() == original,"loot catalog snapshot cannot mutate rules")
	var a := RandomNumberGenerator.new()
	var b := RandomNumberGenerator.new()
	a.seed = 7418
	b.seed = 7418
	var counts := [0,0,0,0]
	var reproducible := true
	for i in range(14000):
		var selected: Dictionary = c.roll(a)
		var expected: Dictionary = c.roll(b)
		reproducible = reproducible and selected == expected and a.state == b.state
		var index := 0 if selected.kind == "no-drop" else (1 if selected.base_id == "item.ember_focus" else (2 if selected.base_id == "item.ward_robe" else 3))
		counts[index] += 1
	check(reproducible,"same seed independent streams reproduce14000 selections")
	for i in range(4):
		var expected: float = 2000.0 if i == 3 else 4000.0
		var sigma: float = sqrt(expected*(1.0-(1.0/7.0 if i == 3 else 2.0/7.0)))
		check(absf(float(counts[i])-expected) < 6.0*sigma,"flat weighted probability within6sigma bucket "+str(i)+" observed "+str(counts[i]))
	var exact: Dictionary = original.duplicate(true)
	exact.entries = [{"kind":"no-drop","weight":0},{"kind":"item","weight":1,"base_id":"item.ember_focus","quality":"common"},{"kind":"item","weight":0,"base_id":"item.ward_robe","quality":"crafted"}]
	check(c.replace_document(exact),"zero weight entries valid with positive total")
	for i in range(20): check(c.roll(a).base_id == "item.ember_focus","zero weights never selected "+str(i))
	var p = Progress.new()
	p.xp = 999999999
	check(p.award() == 1 and p.xp == 1000000000 and p.award() == 0,"XP upper bound saturates without overflow")

func ground_and_corruption_cases() -> void:
	var s = fresh()
	for i in range(12): kill(s)
	var ground: Array = s.ground_loot_snapshot()
	check(not ground.is_empty(),"deterministic fixture yields ground loot")
	if ground.is_empty(): return
	var item: Dictionary = ground[0]
	var identity: Dictionary = s.loot_handle(item.uid)
	var before: Dictionary = state(s)
	check(not s.pickup_loot(identity) and state(s) == before,"remote pickup rejected atomically")
	s.player = Vector2(item.p[0],item.p[1])+Vector2(1.75,0)
	s.life = 12
	s.mana_raw = 123
	var owned: int = s.equipment_items().size()
	check(s.pickup_loot(identity) and s.equipment_items().size() == owned+1,"pickup radius boundary transfers ownership")
	check(s.life == 12 and s.mana_raw == 123,"pickup leaves vitals unchanged")
	before = state(s)
	check(not s.pickup_loot(identity) and state(s) == before,"second pickup cannot duplicate UID")
	var doc: Dictionary = s.progress_document()
	var edits: Array = []
	for pair in [["xp",-1],["xp",1000000001],["xp",1.5],["loot_sha256","changed"],["loot_rng_state","01"],["loot_rng_state",17],["generation_high_water",2147483647],["claims",[{"id":2001,"generation":1}]],["claims",[{"id":1,"generation":0}]]]:
		var bad: Dictionary = doc.duplicate(true)
		bad[pair[0]] = pair[1]
		edits.append(bad)
	for kind in ["lifetime_zero","lifetime_over","unknown_item","duplicate_uid","nan_position","uid_counter","equipment_invalid"]:
		var bad: Dictionary = doc.duplicate(true)
		match kind:
			"lifetime_zero": bad.ground[0].remaining_ticks = 0
			"lifetime_over": bad.ground[0].remaining_ticks = 1801
			"unknown_item": bad.ground[0].item.base_id = "item.missing"
			"duplicate_uid": bad.ground[0].item = bad.equipment.items[0].duplicate(true)
			"nan_position": bad.ground[0].p[0] = NAN
			"uid_counter": bad.equipment.next_uid = 1
			"equipment_invalid": bad.equipment.equipped = {"focus":999999}
		edits.append(bad)
	before = state(s)
	for i in range(edits.size()): check(not s.replace_progress_document(edits[i]) and state(s) == before,"corrupt full profile preserves all state "+str(i))
	var old_ground: Dictionary = s.loot_handle(s.ground_loot_snapshot()[0].uid)
	var old_enemies: Array = []
	for enemy_state in s.enemies.values(): old_enemies.append(s.handle(enemy_state))
	var old_water: int = doc.generation_high_water
	s.tick = 123
	check(s.replace_progress_document(doc) and s.tick == 0,"profile loads into fresh combat clock")
	check(not s.pickup_loot(old_ground),"pre-load ground epoch rejected despite restored UID")
	for h in old_enemies: check(not s.claim_death_reward(h),"pre-load dead handle cannot duplicate reward "+str(h.id))
	var h: Dictionary = s.spawn_enemy(Vector2(20,20))
	check(h.generation > old_water,"post-load entity generation exceeds saved high-water")
	check(s.ground_loot_snapshot()[0].remaining_ticks == doc.ground[0].remaining_ticks,"ground remaining lifetime restored relative to new clock")
	# Keep all rewards remote, fill inventory, then advance one expiry boundary.
	s.player = Vector2(-20,-20)
	s.move_target = s.player
	while s.equipment_items().size() < 64: s.equipment_inventory.create_item("item.ember_focus")
	var remaining: Dictionary = s.ground_loot_snapshot()[0]
	s.player = Vector2(remaining.p[0],remaining.p[1])
	before = state(s)
	check(not s.pickup_loot(s.loot_handle(remaining.uid)) and state(s) == before,"full inventory preserves ground ownership")
	s.player = Vector2(-20,-20)
	s.move_target = s.player
	s.tick = 1800
	s.step()
	check(s.ground_loot_snapshot().is_empty(),"all ground items expire at TTL boundary")

func stream_and_floor_cases() -> void:
	var a = fresh()
	var b = fresh()
	var oracle := RandomNumberGenerator.new()
	for i in range(25):
		oracle.state = a.loot_rng.state
		var selection: Dictionary = a.loot_catalog.roll(oracle)
		for n in range(3): b.rng.randi()
		var h: Dictionary = kill(a)
		kill(b)
		check(a.loot_rng.state == oracle.state,"exactly one loot selection per actual death "+str(i))
		var last: Dictionary = a.progress_history_snapshot().back()
		check(last.kind == "loot_result" and last.selection == selection,"recorded loot selection matches independent oracle "+str(i))
		check(a.ground_loot_snapshot() == b.ground_loot_snapshot() and a.equipment_snapshot() == b.equipment_snapshot(),"perturbed damage RNG cannot affect item/loot streams "+str(i))
		var prior: int = a.loot_rng.state
		a.claim_death_reward(h)
		check(a.loot_rng.state == prior,"duplicate claim consumes no loot randomness "+str(i))
	var old_document: Dictionary = a.progress_document()
	var last_identity: Dictionary = {}
	for i in range(5): last_identity = kill(a)
	var current_water: int = a.progress_document().generation_high_water
	check(a.replace_progress_document(old_document),"older valid profile accepted")
	check(not a.claim_death_reward(last_identity),"loading older profile rejects future pre-load death identity")
	var identity: Dictionary = a.spawn_enemy(Vector2(20,20))
	check(identity.generation > current_water,"load merges current highwater instead of rolling it back")
	var s = fresh()
	for i in range(10): kill(s)
	var item: Dictionary = s.ground_loot_snapshot()[0]
	s.player = Vector2(item.p[0],item.p[1])
	s.life = 1000000
	s.mana_raw = 100000000
	check(s.pickup_loot(s.loot_handle(item.uid)) and s.life == 1000000 and s.mana_raw == 100000000,"ownership-only pickup does not rebuild/clamp synthetic combat fixture vitals")

func reservation_and_capacity_cases() -> void:
	var s = fresh()
	var inv = s.equipment_inventory
	for quality in ["common","crafted"]:
		var before: Dictionary = inv.snapshot()
		var item: Dictionary = inv.reserve_item("item.ember_focus",quality)
		var after: Dictionary = inv.snapshot()
		check(item.uid == before.next_uid and after.next_uid == before.next_uid+1 and after.items == before.items,"reservation allocates shared UID without granting ownership "+quality)
		check(item.affixes.size() == (0 if quality == "common" else 1) and after.rng_state != before.rng_state,"quality controls affix count and advances separate roll RNG "+quality)
		check(inv.acquire_reserved(item) and inv.items_snapshot().size() == before.items.size()+1,"reserved item can atomically become owned "+quality)
		before = inv.snapshot()
		check(not inv.acquire_reserved(item) and inv.snapshot() == before,"duplicate reserved UID cannot be acquired twice "+quality)
	var snapshot: Dictionary = inv.snapshot()
	check(inv.reserve_item("item.invalid","common").is_empty() and inv.snapshot() == snapshot,"invalid reservation preserves allocator and RNG")
	var exhausted: Dictionary = s.equipment_snapshot()
	exhausted.next_uid = 2147483648
	check(s.replace_equipment_document(exhausted),"exhausted allocator sentinel is representable without wrap")
	var had_uid_exhaustion := false
	for i in range(12):
		kill(s)
		var result: Dictionary = s.progress_history_snapshot().back()
		if result.reason == "uid_exhausted": had_uid_exhaustion = true
	check(had_uid_exhaustion and s.ground_loot_snapshot().is_empty() and s.progression_snapshot().xp == 36,"UID exhaustion records reason and preserves XP rewards")
	s = fresh()
	for i in range(100):
		var dead: Dictionary = kill(s)
		s.despawn_enemy(dead)
	check(s.ground_loot_snapshot().size() == 32,"deterministic overload reaches exact32 ground cap")
	var saw_full := false
	for e in s.progress_history_snapshot():
		if e.kind == "loot_result" and e.reason == "ground_full": saw_full = true
	check(saw_full,"selected item suppressed by cap records ground_full")
	var capacity_doc: Dictionary = s.progress_document()
	var too_many: Dictionary = capacity_doc.duplicate(true)
	too_many.ground.append(too_many.ground[0].duplicate(true))
	var before: Dictionary = state(s)
	check(not s.replace_progress_document(too_many) and state(s) == before,"ground33 profile rejects atomically")
	var oversized_claim: Dictionary = capacity_doc.duplicate(true)
	oversized_claim.claims = []
	for i in range(2001): oversized_claim.claims.append({"id":i+1,"generation":1})
	check(not s.replace_progress_document(oversized_claim) and state(s) == before,"claim2001 profile rejects atomically")
	# Force derived modifier failure after all document references are valid.
	s = fresh()
	var modifiers: Array = []
	for i in range(64): modifiers.append({"source_id":"external","id":"m"+str(i),"stat_id":"stat.spell_power","operation":"add","value":0})
	check(s.replace_player_modifiers(modifiers),"derived-stat failure fixture accepts64 external modifiers")
	var conflicting: Dictionary = s.progress_document()
	conflicting.equipment.equipped.focus = 1
	before = state(s)
	check(not s.replace_progress_document(conflicting) and state(s) == before,"profile derived-modifier failure cannot partially publish XP/gear/RNG/generation")

func run() -> void:
	reward_cases()
	profile_cases()
	catalog_cases()
	ground_and_corruption_cases()
	stream_and_floor_cases()
	reservation_and_capacity_cases()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional independent harness failure proof")
	print(JSON.stringify({"scope":"Independent phase6 death/XP/identity/profile contracts; no GPU claim","checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
