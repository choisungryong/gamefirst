extends SceneTree
const Growth = preload("res://chapter1/core/run_growth_quality37.gd")
const BaseGrowth = preload("res://chapter1/core/run_growth.gd")
const Catalog = preload("res://chapter1/core/growth_catalog.gd")
var checks: Array[Dictionary] = []
var passed := true
func check(ok: bool,label: String) -> void:
	checks.append({"ok":ok,"label":label})
	passed = passed and ok
func _initialize() -> void:
	var catalog = Catalog.new()
	check(catalog.load_file("res://chapter1/data/growth_quality36.json"),"valid predecessor loads")
	var doc: Dictionary = catalog.snapshot()
	var bad_skills: Dictionary = doc.duplicate(true)
	bad_skills.skills = [17]
	var bad_skill_records: Dictionary = doc.duplicate(true)
	bad_skill_records.skills = [17,17,17]
	var bad_xp: Dictionary = doc.duplicate(true)
	bad_xp.xp_thresholds = 17
	var invalids: Array = [17,bad_skills,bad_skill_records,bad_xp]
	var labels: Array[String] = ["nonDictionary","skills array17","three nonDictionary skill records","xp_thresholds17"]
	for index in invalids.size():
		var candidate: Variant = invalids[index]
		var fresh = Growth.new()
		var initial: Dictionary = fresh.snapshot()
		check(not fresh.configure(candidate,"chapter1.skill.arc",7),labels[index]+" rejected fresh")
		check(fresh.errors == Catalog.validate(candidate) and not fresh.errors.is_empty(),labels[index]+" matches inherited validation errors")
		check(fresh.snapshot() == initial and fresh._successor_document.is_empty(),labels[index]+" fresh state and template untouched")
	var active = Growth.new()
	var base = BaseGrowth.new()
	check(active.configure(doc,"chapter1.skill.arc",90131) and base.configure(doc,"chapter1.skill.arc",90131),"valid configuration remains accepted")
	check(active.award_xp(36) and base.award_xp(36),"existing growth state populated")
	check(active.next_offer() == base.next_offer(),"valid offer tokens and RNG unchanged before rejection")
	var previous: Dictionary = active.snapshot()
	var template: Dictionary = active._successor_document.duplicate(true)
	for index in invalids.size():
		check(not active.configure(invalids[index],"chapter1.skill.arc",1),labels[index]+" rejected configured")
		check(active.snapshot() == previous and active._successor_document == template,labels[index]+" configured state RNG offer and template preserved")
		check(active.errors == Catalog.validate(invalids[index]),labels[index]+" configured validation errors match base")
	check(active.configure(doc,"chapter1.skill.arc",90132) and base.configure(doc,"chapter1.skill.arc",90132),"valid reconfiguration works after errors")
	check(active.errors.is_empty() and active.snapshot() == base.snapshot(),"reconfiguration clears errors and preserves inherited epoch RNG")
	var file = FileAccess.open("res://plans/chapter1-quality04-20261101-01/masonry37/text02/RESULT.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"passed":passed,"checks":checks,"scope":"Targeted malformed configure Variant failfalse guard and state preservation; no GPU/profile/performance or full prior run repeats."},"\t"))
	file.close()
	quit(0 if passed else 1)
