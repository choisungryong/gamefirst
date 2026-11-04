extends SceneTree
## Independent raw arithmetic, state transaction and isolated file cases.
const Sim = preload("res://baseline_sim.gd")
const Storage = preload("res://data/equipment_storage.gd")
const CombatCatalog = preload("res://data/game_catalog.gd")
var checks := 0
var failures: Array[String] = []

func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok:
		failures.append(message)
		printerr("PHASE5 SIM/STORAGE FAILED: "+message)

func fresh() -> RefCounted:
	var s = Sim.new()
	s.reset(0)
	s.enemy_ai = false
	return s

func state(s: RefCounted) -> Dictionary:
	return {"equipment":s.equipment_snapshot(),"context":s.equipment_context(),"stats":s.player_stats_snapshot(),"life":s.life,"life_max":s.life_max_raw,"mana":s.mana_raw,"mana_max":s.mana_max_raw,"rng":s.rng.state,"tick":s.tick,"pending":s.pending_context_snapshot()}

func modifier(index: int, stat: String = "stat.spell_power", amount: int = 0) -> Dictionary:
	return {"source_id":"external","id":"m"+str(index),"stat_id":stat,"operation":"add","value":amount}

@warning_ignore("integer_division")
func positive_floor_ratio(n: int, d: int) -> int:
	return n/d

func sim_cases() -> void:
	var s = fresh()
	check(s.valid_profile and s.equipment_valid and s.equipment_items().size() == 3,"simulation initializes three owned unequipped items")
	check(s.equipment_snapshot().equipped.is_empty() and s.skill_display().effective_level == 1,"initial ownership supplies no equipment bonuses")
	var stats_before: Dictionary = s.player_stats_snapshot()
	var rng_before: int = s.rng.state
	var extra: Dictionary = s.equipment_inventory.create_item("item.ember_focus")
	check(extra.uid == 4 and s.rng.state == rng_before,"item creation uses independent RNG stream")
	var first: Dictionary = s.equipment_snapshot().items[0]
	var power: int = int(first.affixes[0].value)
	s.life = 17
	s.mana_raw = 1234
	check(s.equip_item(1),"equip initial focus")
	var display: Dictionary = s.skill_display("skill.ember_bolt")
	check(display.effective_level == 2 and display.bonus_level == 1 and display.cost_raw == 640,"single-skill bonus changes level with preserved cost")
	check(display.damage_min_raw == positive_floor_ratio(1024*(10000+power),10000) and display.damage_max_raw == positive_floor_ratio(2048*(10000+power),10000),"independent +256/+512 curve then rolled power floor")
	check(s.life == 17 and s.mana_raw == 1234,"focus equip grants no vital recovery")
	check(s.unequip_item("focus") and s.player_stats_snapshot() == stats_before and s.life == 17 and s.mana_raw == 1234,"unequip returns exact baseline stats without restoring vitals")
	check(s.equip_item(2) and s.life_max_raw == 12800 and s.life == 17,"robe increases max40 to50 with current17 unchanged")
	s.life = 49
	check(s.unequip_item("body") and s.life_max_raw == 10240 and s.life == 40,"max reduction clamps current to40")
	check(s.equip_item(2) and s.life == 40 and s.life_max_raw == 12800,"reequip cannot refill lost HP")
	check(s.replace_equipment_context({"actor_tag":"caster","level":2}) and s.equip_item(3),"explicit base context permits charm")
	check(s.mana_max_raw == 10240 and s.mana_raw == 1234,"charm max35 to40 leaves current raw unchanged")
	s.mana_raw = 10000
	check(s.unequip_item("charm") and s.mana_max_raw == 8960 and s.mana_raw == 8960,"charm removal clamps current mana to original maximum")
	check(s.equip_item(3) and s.mana_raw == 8960,"charm reequip does not grant mana")
	var before: Dictionary = state(s)
	check(not s.replace_equipment_context({"actor_tag":"caster","level":1}) and state(s) == before,"ineligible context reduction preserves items/stats/vitals")
	check(s.replace_player_modifiers([modifier(0,"stat.health",256)]),"external and gear modifiers compose")
	check(s.life_max_raw == 13056 and s.equipment_snapshot().equipped.body == 2,"external health +1 composes with robe +10")
	check(s.equip_item(1),"third slot can become equipped")
	var gear_before: Dictionary = s.player_stats_snapshot()
	check(s.replace_player_modifiers([]) and s.life_max_raw == 12800 and s.player_stats_snapshot()["stat.skill.ember_level"] == 1,"external replacement preserves equipment contribution")
	var saved: Dictionary = s.equipment_snapshot()
	var item_rng: String = saved.rng_state
	s.life = 3
	s.mana_raw = 9
	s.reset(0)
	check(s.equipment_snapshot() == saved and s.equipment_snapshot().rng_state == item_rng,"combat reset preserves items/equipment/UID/item RNG")
	check(s.life == 50 and s.mana_raw == 10240 and s.skill_display().effective_level == 2,"explicit reset full-heals modified maxima and preserves equipped level")
	var peer = fresh()
	peer.reset(2)
	var handles: Array = peer.enemies.keys()
	peer.enemies[handles[0]].life_raw = 1
	check(peer.enemies[handles[1]].life_raw == 2304,"two enemies sharing definition retain independent HP")

	var cap = fresh()
	var external: Array = []
	for i in range(64): external.append(modifier(i))
	check(cap.replace_player_modifiers(external),"64 external modifiers are supported without gear")
	before = state(cap)
	check(not cap.equip_item(1) and state(cap) == before,"equipment exceeding combined64 limit is atomic")
	check(cap.replace_player_modifiers([]) and cap.equip_item(1),"equip succeeds after removing capacity conflict")
	before = state(cap)
	check(not cap.replace_player_modifiers(external) and state(cap) == before,"external replacement exceeding combined64 preserves gear/stats/vitals")
	check(not cap.replace_player_modifiers([{"source_id":"equipment/999","id":"injected","stat_id":"stat.spell_power","operation":"add","value":10000}]) and state(cap) == before,"external caller cannot impersonate reserved gear namespace")
	var invalid: Dictionary = cap.equipment_snapshot()
	invalid.equipped["charm"] = 3
	check(not cap.replace_equipment_document(invalid) and state(cap) == before,"ineligible saved equip cannot alter committed stats")

	var pending = fresh()
	pending.player = Vector2.ZERO
	pending.move_target = Vector2.ZERO
	var target: Dictionary = pending.spawn_enemy(Vector2(1,0))
	pending.entity(target).life_raw = 100000
	check(pending.equip_item(1),"paid snapshot fixture equips focus")
	power = int(pending.equipment_snapshot().items[0].affixes[0].value)
	var expected_rng := RandomNumberGenerator.new()
	expected_rng.state = pending.rng.state
	var expected_base: int = expected_rng.randi_range(1024,2048)
	var expected_damage: int = positive_floor_ratio(expected_base*(10000+power),10000)
	pending.step(true,Vector2.RIGHT)
	var committed: Dictionary = pending.pending_context_snapshot()
	check(committed.base_min_raw == 1024 and committed.base_max_raw == 2048 and committed.bonus_level == 1 and committed.power_bps == power,"request snapshots skill bonus curve and rolled attacker power")
	check(pending.unequip_item("focus") and pending.skill_display().effective_level == 1,"live equipment can change while paid cast waits")
	for i in range(18): pending.step()
	check(pending.combat_trace.size() == 1 and pending.combat_trace[0].base_raw == expected_base and pending.combat_trace[0].total_raw == expected_damage,"paid projectile uses independent expected committed level/power after unequip")
	check(pending.rng.state == expected_rng.state and pending.mana_raw == 8320,"paid cast consumes one damage roll and original raw640 cost")

	var historical = CombatCatalog.new()
	check(historical.load_file("res://evidence/phase4/reference-phase3/game_data/catalog.json"),"accepted historical v1 catalog loads")
	var old = Sim.new(historical)
	check(old.valid_profile and not old.equipment_valid and old.equipment_items().is_empty(),"v1 without semantic stat keeps combat available and equipment disabled")
	check(not old.equip_item(1) and not old.save_equipment("res://evidence/phase6/verification/never-written.json"),"unavailable equipment fails without affecting compatibility combat")
	var precise_catalog = CombatCatalog.new()
	check(precise_catalog.load_file(),"precise combat fingerprint fixture loads")
	var precise_doc: Dictionary = precise_catalog.snapshot()
	var previous_speed: float = precise_doc.enemies[0].move_speed_world_per_second
	precise_doc.enemies[0].move_speed_world_per_second = previous_speed+0.0000000001
	check(precise_doc.enemies[0].move_speed_world_per_second != previous_speed and precise_catalog.replace_document(precise_doc),"valid close float combat rule remains a distinct definition")
	var precise = Sim.new(precise_catalog)
	var ordinary = fresh()
	check(precise.equipment_valid and precise.equipment_snapshot().catalog_sha256 != ordinary.equipment_snapshot().catalog_sha256,"full-precision combat rule change alters equipment save fingerprint")
	check(not precise.replace_equipment_document(ordinary.equipment_snapshot()),"close float combat rule mismatch rejects equipment save")

func write_fixture(path: String, text: String) -> void:
	var handle := FileAccess.open(path,FileAccess.WRITE)
	check(handle != null,"isolated fixture writable "+path)
	if handle:
		handle.store_string(text)
		handle.close()

func storage_cases() -> void:
	var s = fresh()
	var storage = Storage.new()
	var folder: String = "res://evidence/phase6/verification/storage-"+str(OS.get_process_id())+"-"+str(Time.get_ticks_usec())
	check(DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(folder)) == OK,"isolated phase5 storage folder created")
	var path: String = folder+"/equipment.json"
	check(s.equip_item(2),"save fixture has robe")
	s.life = 19
	s.mana_raw = 2222
	var saved: Dictionary = s.equipment_snapshot()
	var before: Dictionary = state(s)
	check(s.save_equipment(path) and state(s) == before,"save writes separate document without gameplay changes")
	var first_bytes: String = FileAccess.get_file_as_string(path)
	check(not first_bytes.is_empty() and JSON.parse_string(first_bytes) is Dictionary,"saved JSON readable")
	check(s.unequip_item("body") and s.life == 19,"prepare load of robe with unchanged current HP")
	check(s.load_equipment(path) and s.equipment_snapshot() == saved and s.life == 19 and s.mana_raw == 2222,"load reconstructs definitions/roll modifiers without healing")
	check(s.unequip_item("body") and s.save_equipment(path),"second save replaces intended test file")
	var directory := DirAccess.open(folder)
	var backups: Array[String] = []
	for name_ in directory.get_files():
		if name_.ends_with(".previous"): backups.append(name_)
	check(backups.size() == 1 and FileAccess.get_file_as_string(folder+"/"+backups[0]) == first_bytes,"overwriting own test save preserves exact prior bytes as backup")
	var invalid: Dictionary = saved.duplicate(true)
	invalid.items[0].affixes[0].value = 999999
	var invalid_path: String = folder+"/invalid.json"
	write_fixture(invalid_path,JSON.stringify(invalid))
	var invalid_bytes: String = FileAccess.get_file_as_string(invalid_path)
	before = state(s)
	check(not s.load_equipment(invalid_path) and state(s) == before and FileAccess.get_file_as_string(invalid_path) == invalid_bytes,"tampered save rejects atomically and preserves input bytes")
	var broken_path: String = folder+"/broken.json"
	write_fixture(broken_path,"{bad JSON")
	check(not s.load_equipment(broken_path) and state(s) == before and FileAccess.get_file_as_string(broken_path) == "{bad JSON","malformed save preserves state and file")
	check(not s.load_equipment(folder+"/missing.json") and state(s) == before,"missing save preserves state")
	var oversized_path: String = folder+"/oversized.json"
	write_fixture(oversized_path,"x".repeat(1048577))
	check(not s.load_equipment(oversized_path) and state(s) == before,"size bound rejects before state mutation")
	for unsupported in ["res://game_data/catalog.json","res://evidence/phase4/not-written.json",folder+"/../escape.json",folder+"/file.txt","user://other-save.json"]:
		check(not storage.allowed_path(unsupported),"storage refuses unsupported path "+unsupported)
		check(not s.save_equipment(unsupported) and state(s) == before,"unsupported save has no state effects")
	var occupied: String = folder+"/occupied.json"
	check(DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(occupied)) == OK,"create dedicated directory to force replacement failure")
	check(not s.save_equipment(occupied) and state(s) == before and DirAccess.dir_exists_absolute(ProjectSettings.globalize_path(occupied)),"filesystem replacement failure is atomic and retains destination directory")

func run() -> void:
	sim_cases()
	storage_cases()
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional sim/storage harness failure proof")
	print(JSON.stringify({"scope":"Independent gear/stat/paid-cast and isolated storage contracts", "checks":checks,"failures":failures,"success":failures.is_empty()}))
	quit(0 if failures.is_empty() else 1)
