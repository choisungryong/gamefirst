extends SceneTree
const Before = preload("res://chapter1/core/chapter_run_quality36.gd")
const After = preload("res://chapter1/core/chapter_run_quality37.gd")
const Pilot = preload("res://chapter1/core/chapter_pilot.gd")
const Catalog = preload("res://chapter1/core/growth_catalog.gd")
const OUT = "res://plans/chapter1-quality04-20261101-01/masonry37/text01/RESULT.json"
var checks: Array[Dictionary] = []
var traces: Array[Dictionary] = []
var failed := false

func check(ok: bool, label: String) -> void:
	checks.append({"ok":ok,"label":label})
	if not ok:failed = true

func predecessor_text(value: Variant) -> Variant:
	if value is String:return "두 갈래 폭풍" if value == "세 갈래 폭풍" else value
	if value is Dictionary:
		var result: Dictionary = {}
		for key in value:result[key] = predecessor_text(value[key])
		return result
	if value is Array:
		var result: Array = []
		for item in value:result.append(predecessor_text(item))
		return result
	return value

func _initialize() -> void:
	var old_catalog = Catalog.new()
	var new_catalog = Catalog.new()
	check(old_catalog.load_file("res://chapter1/data/growth_quality36.json"),"predecessor catalog validates")
	check(new_catalog.load_file("res://chapter1/data/growth_quality37.json"),"successor catalog validates")
	var old_doc: Dictionary = old_catalog.snapshot()
	var new_doc: Dictionary = new_catalog.snapshot()
	var corrected: Dictionary = old_doc.duplicate(true)
	corrected.skills[2].evolution_name = "세 갈래 폭풍"
	check(new_doc == corrected and new_doc != old_doc,"catalog full dictionary differs only arc evolution name")
	check(new_doc.skills[2].evolution.branches == 3,"successor name matches three evolution branches")
	for primary in ["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"]:
		var before = Before.new()
		var after = After.new()
		check(before.start(90131,primary) and after.start(90131,primary),primary+" starts")
		check(before.snapshot() == after.snapshot(),primary+" entire initial snapshot same")
		check(before.growth.snapshot().epoch == 2 and after.growth.snapshot().epoch == 2,primary+" exactly two inherited configurations")
		check(after.growth.xp_thresholds() == before.FULL_XP,primary+" FULL_XP preserved")
		var before_pilot = Pilot.new()
		var after_pilot = Pilot.new()
		before_pilot.run = before
		after_pilot.run = after
		var frames_same := true
		var rng_same := true
		for frame in 1200:
			before.step(before_pilot.decide())
			after.step(after_pilot.decide())
			if predecessor_text(after.snapshot()) != before.snapshot():frames_same = false;break
			if before._spawn_rng.state != after._spawn_rng.state or before._loot_rng.state != after._loot_rng.state or before.growth.snapshot().rng_state != after.growth.snapshot().rng_state:rng_same = false;break
		check(frames_same,primary+" 1200-frame full snapshots same except approved text")
		check(rng_same,primary+" spawn loot and growth RNG states same every frame")
		check(before_pilot.selections == after_pilot.selections,primary+" normal growth selection tokens and IDs same")
		traces.append({"primary":primary,"tick":after.tick,"kills":after.kills,"level":after.growth.snapshot().level,"growth_epoch":after.growth.snapshot().epoch,"growth_rng":after.growth.snapshot().rng_state,"spawn_rng":str(after._spawn_rng.state),"loot_rng":str(after._loot_rng.state)})
		check(before.start(90131,primary) and after.start(90131,primary),primary+" same objects restart")
		check(before.snapshot() == after.snapshot() and after.growth.snapshot().epoch == 4,primary+" restart configure count epoch4 and snapshot same")
		# Pure growth fixture reaches normal protected offers without sim grants or profile I/O.
		check(before.growth.award_xp(1640) and after.growth.award_xp(1640),primary+" growth fixture XP accepted")
		var offer_same := true
		var evolved := false
		var corrected_title := false
		for index in 11:
			var offer_before: Dictionary = before.growth.next_offer()
			var offer_after: Dictionary = after.growth.next_offer()
			if predecessor_text(offer_after) != offer_before:offer_same = false;break
			if offer_after.is_empty():break
			var picked: Dictionary = offer_after.cards[0]
			if picked.kind == "evolve" and picked.skill_id == primary:
				evolved = true
				if primary == "chapter1.skill.arc":corrected_title = picked.title == "세 갈래 폭풍"
			if not before.growth.choose(offer_before.token,picked.id) or not after.growth.choose(offer_after.token,picked.id):offer_same = false;break
			if predecessor_text(after.growth.snapshot()) != before.growth.snapshot():offer_same = false;break
			if evolved:break
		check(offer_same and evolved,primary+" protected offers tokens RNG and choices identical through evolution")
		if primary == "chapter1.skill.arc":
			check(corrected_title and after.growth.effective_skill(primary).name == "세 갈래 폭풍","arc offer and effective evolved skill use new name")
			check(after.growth.effective_skill(primary).effects == before.growth.effective_skill(primary).effects,"evolved arc every numeric effect unchanged")
		before_pilot.run = null
		after_pilot.run = null
	var file = FileAccess.open(OUT,FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":not failed,"checks":checks,"normal_traces":traces,"scope":"Unadopted successor catalog wording; inherited two-configure start and restart, all3 primary normal1200frame and pure growth offer/evolution fixtures. No old full completion reruns, no user profiles, no GPU/native/audio/performance approval."},"\t"))
	file.close()
	quit(1 if failed else 0)
