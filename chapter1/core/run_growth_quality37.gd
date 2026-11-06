extends "res://chapter1/core/run_growth.gd"
## Successor-only catalog wording. Keeps inherited configure count, seed and XP policy.
const SuccessorCatalog = preload("res://chapter1/core/growth_catalog.gd")
var _successor_document: Dictionary = {}

func configure(candidate: Variant, primary_skill: String, run_seed: int) -> bool:
	var issues := SuccessorCatalog.validate(candidate)
	if not issues.is_empty():
		errors = issues
		return false
	if _successor_document.is_empty():
		var catalog = SuccessorCatalog.new()
		if not catalog.load_file("res://chapter1/data/growth_quality37.json"):
			errors.assign(catalog.errors)
			return false
		_successor_document = catalog.snapshot()
	var expected: Dictionary = candidate.duplicate(true)
	var changed := false
	for skill in expected.get("skills",[]):
		if skill.get("id","") == "chapter1.skill.arc":
			if skill.get("evolution_name","") != "두 갈래 폭풍":
				errors.assign(["Unexpected predecessor arc evolution name"])
				return false
			skill.evolution_name = "세 갈래 폭풍"
			changed = true
	if not changed or not expected.has("xp_thresholds"):
		errors.assign(["Successor growth predecessor fields missing"])
		return false
	var successor: Dictionary = _successor_document.duplicate(true)
	# ChapterRun's second configure supplies FULL_XP; preserve that exact incoming policy.
	successor.xp_thresholds = expected.xp_thresholds.duplicate(true)
	if successor != expected:
		errors.assign(["Successor catalog may differ only in arc evolution name"])
		return false
	return super.configure(successor,primary_skill,run_seed)
