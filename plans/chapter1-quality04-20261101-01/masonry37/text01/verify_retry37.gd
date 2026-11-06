extends SceneTree
const Before = preload("res://chapter1/core/chapter_run_quality36.gd")
const After = preload("res://chapter1/core/chapter_run_quality37.gd")
var checks: Array[Dictionary] = []
var passed := true
func check(ok: bool,label: String) -> void:
	checks.append({"ok":ok,"label":label})
	passed = passed and ok
func _initialize() -> void:
	for primary in ["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"]:
		var before = Before.new()
		var after = After.new()
		check(before.start(90131,primary) and after.start(90131,primary),primary+" initial start")
		var cached: Dictionary = after.growth._successor_document.duplicate(true)
		for tick in 10:
			before.step(Vector2.RIGHT)
			after.step(Vector2.RIGHT)
		check(before.growth.award_xp(72) and after.growth.award_xp(72),primary+" old growth state populated")
		check(before.growth.next_offer() == after.growth.next_offer(),primary+" old offer and tokens equal")
		# ChapterView.retry increments seed then calls start_run, which delegates to run.start.
		check(before.start(90132,primary) and after.start(90132,primary),primary+" retry seed increment starts")
		check(before.snapshot() == after.snapshot() and after.growth.snapshot().epoch == 4,primary+" retry resets full snapshot identically without extra configure")
		check(after.growth._successor_document == cached and after.growth.xp_thresholds() == before.FULL_XP,primary+" cached successor remains unchanged and FULL_XP restored")
		check(before._spawn_rng.state == after._spawn_rng.state and before._loot_rng.state == after._loot_rng.state and before.growth.snapshot().rng_state == after.growth.snapshot().rng_state,primary+" all retry RNG states identical")
	var file = FileAccess.open("res://plans/chapter1-quality04-20261101-01/masonry37/text01/RETRY-RESULT.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":passed,"checks":checks,"scope":"Bounded inherited retry contract: view increments seed and invokes start; no standalone core reset API. Normal10frames followed by pending growth offer then same-object retry. No UI/GPU/profile."},"\t"))
	file.close()
	quit(0 if passed else 1)
