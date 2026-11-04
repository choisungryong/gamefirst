extends SceneTree
const Catalog = preload("res://chapter1/core/growth_catalog.gd")
const Growth = preload("res://chapter1/core/run_growth.gd")
var checks := 0
var failures: Array[String] = []

func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok: failures.append(label)

func rejected_catalog(catalog: RefCounted, bad: Variant, label: String) -> void:
	var before: Dictionary = catalog.snapshot()
	check(not catalog.replace_document(bad) and catalog.snapshot() == before,label)

func _initialize() -> void:
	var catalog = Catalog.new()
	check(catalog.load_file(),"independent growth definitions load")
	var doc: Dictionary = catalog.snapshot()
	if doc.is_empty():
		print("CHAPTER1_GROWTH_RESULT ",JSON.stringify({"checks":checks,"failures":failures,"catalog_errors":catalog.errors}))
		quit(1)
		return
	var bad: Dictionary = doc.duplicate(true)
	bad.skills[0].passive_id = "missing"
	rejected_catalog(catalog,bad,"missing evolution prerequisite rejected atomically")
	bad = doc.duplicate(true)
	bad.skills[1].id = bad.skills[0].id
	rejected_catalog(catalog,bad,"duplicate skill id rejected")
	bad = doc.duplicate(true)
	bad.xp_thresholds[2] = bad.xp_thresholds[1]
	rejected_catalog(catalog,bad,"unreachable XP progression rejected")
	bad = doc.duplicate(true)
	bad.skills[0].ranks[0].proc_depth = 2
	rejected_catalog(catalog,bad,"recursive proc budget rejected")
	bad = doc.duplicate(true)
	bad.skills[0].evolution.hit_budget = 0
	rejected_catalog(catalog,bad,"zero hit budget rejected")
	bad = doc.duplicate(true)
	bad.skills[0].ranks[0].projectiles = 1.5
	rejected_catalog(catalog,bad,"fractional projectile count rejected")
	bad = doc.duplicate(true)
	bad.skills[0].ranks[0].projectiles = NAN
	rejected_catalog(catalog,bad,"nonfinite projectile count rejected")
	var escaped: Dictionary = catalog.snapshot()
	escaped.skills[0].ranks[0].projectiles = 99
	check(catalog.snapshot() == doc,"catalog snapshots detached")

	for s in doc.skills:
		var run = Growth.new()
		check(run.configure(doc,s.id,771),"configure primary "+s.id)
		var first: Dictionary = run.effective_skill(s.id)
		var kinds: Array[String] = []
		# Player deliberately follows the always-reachable primary evolution path.
		for level_index in range(1,6):
			var amount: int = int(doc.xp_thresholds[level_index])-int(run.snapshot().xp)
			check(run.award_xp(amount),"XP accepted for next choice")
			var offer: Dictionary = run.next_offer()
			check(not offer.is_empty() and offer.cards.size() >= 2 and offer.cards.size() <= 3,"legal choice count")
			var before_repeat: Dictionary = run.snapshot()
			check(run.next_offer() == offer and run.snapshot() == before_repeat,"opening same offer is idempotent")
			var ids: Array[String] = []
			for card in offer.cards:
				check(not card.id in ids,"no duplicate card")
				ids.append(card.id)
			var protected: Dictionary = offer.cards[0]
			check(protected.skill_id == s.id,"primary path offered without a loot lottery")
			kinds.append(protected.kind)
			var token: String = offer.token
			check(run.choose(token,protected.id),"offered choice commits")
			var committed: Dictionary = run.snapshot()
			check(not run.choose(token,protected.id) and run.snapshot() == committed,"double commit cannot duplicate growth")
		check(kinds == ["rank","rank","rank","passive","evolve"],"rank/prerequisite/evolution ordering")
		var last: Dictionary = run.effective_skill(s.id)
		check(last.evolved and last.rank == 4 and last.effects != first.effects,"evolution changes effective attack definition")
		if s.id == "chapter1.skill.ember":
			check(first.effects.projectiles == 1 and last.effects.projectiles == 3 and last.effects.radius_cm > 0,"fire grows from one bolt to multi-target explosion")
		elif s.id == "chapter1.skill.frost":
			check(first.effects.freeze_stacks == 0 and last.effects.freeze_stacks > 0 and last.effects.shatter_count > 0,"cold adds control and shatter")
		else:
			check(first.effects.branches == 1 and last.effects.branches == 2 and last.effects.chain_targets > first.effects.chain_targets,"lightning adds branches and chain targets")

	var a = Growth.new()
	var b = Growth.new()
	a.configure(doc,doc.skills[0].id,12345)
	b.configure(doc,doc.skills[0].id,12345)
	a.award_xp(396)
	b.award_xp(396)
	check(a.snapshot().level == 12 and a.snapshot().pending_levels.size() == 11,"large XP gain queues bounded level choices")
	for i in range(11):
		var oa: Dictionary = a.next_offer()
		var ob: Dictionary = b.next_offer()
		check(oa == ob and a.snapshot() == b.snapshot(),"same-seed same-input replay")
		var select_index := 0
		for j in oa.cards.size():
			if oa.cards[j].kind == "unlock": select_index = j
		check(a.choose(oa.token,oa.cards[select_index].id) and b.choose(ob.token,ob.cards[select_index].id),"replayed selections commit")
	check(a.snapshot().ranks.size() == 3 and a.snapshot().pending_levels.is_empty() and a.next_offer().is_empty(),"all three skill slots unlock without extra offers")
	var before_invalid: Dictionary = a.snapshot()
	check(not a.award_xp(-1) and not a.award_xp(1.5) and not a.award_xp(true) and a.snapshot() == before_invalid,"invalid XP rejected without mutation")
	check(not a.configure(doc,"missing",1) and a.snapshot() == before_invalid,"bad run configuration preserves current run")
	var detached: Dictionary = a.snapshot()
	detached.ranks.clear()
	check(not a.snapshot().ranks.is_empty(),"run snapshots cannot mutate active ranks")
	var effect_copy: Dictionary = a.effective_skill(doc.skills[0].id)
	effect_copy.effects.damage_raw = 1
	check(a.effective_skill(doc.skills[0].id).effects.damage_raw != 1,"effective definition is detached")

	var stale = Growth.new()
	stale.configure(doc,doc.skills[0].id,1)
	stale.award_xp(6)
	var old_offer: Dictionary = stale.next_offer()
	var before_wrong: Dictionary = stale.snapshot()
	check(not stale.choose(old_offer.token,"unoffered") and stale.snapshot() == before_wrong,"unoffered card rejected atomically")
	stale.configure(doc,doc.skills[0].id,1)
	stale.award_xp(6)
	var new_offer: Dictionary = stale.next_offer()
	check(old_offer.token != new_offer.token,"reset invalidates old offer token")
	var before_stale: Dictionary = stale.snapshot()
	check(not stale.choose(old_offer.token,old_offer.cards[0].id) and stale.snapshot() == before_stale,"previous run cannot consume current choice")
	stale.award_xp(1000000000)
	stale.award_xp(1000000000)
	check(stale.snapshot().xp == 1000000000 and stale.snapshot().pending_levels.size() <= 11,"XP saturates and pending queue stays bounded")
	if OS.get_cmdline_user_args().has("--prove-failure"): check(false,"intentional harness failure")
	print("CHAPTER1_GROWTH_RESULT ",JSON.stringify({"checks":checks,"failures":failures,"scope":"growth core only; no world/VFX/audio/save integration"}))
	quit(0 if failures.is_empty() else 1)
