extends RefCounted
## Pure run growth. No world simulation, rendering, native profile reads or writes.
## RNG docs: https://docs.godotengine.org/en/4.5/classes/class_randomnumbergenerator.html
const Catalog = preload("res://chapter1/core/growth_catalog.gd")
const MAX_XP := 1000000000
var errors: Array[String] = []
var _doc: Dictionary = {}
var _skills: Dictionary = {}
var _passives: Dictionary = {}
var _ranks: Dictionary = {}
var _owned_passives: Array[String] = []
var _evolved: Array[String] = []
var _xp := 0
var _level := 1
var _primary := ""
var _pending: Array[int] = []
var _offer: Dictionary = {}
var _epoch := 0
var _offer_sequence := 0
var _rng := RandomNumberGenerator.new()

func configure(candidate: Variant, primary_skill: String, run_seed: int) -> bool:
	var issues := Catalog.validate(candidate)
	if not issues.is_empty():
		errors = issues
		return false
	var new_skills: Dictionary = {}
	var new_passives: Dictionary = {}
	for s in candidate.skills: new_skills[s.id] = s.duplicate(true)
	for p in candidate.passives: new_passives[p.id] = p.duplicate(true)
	if not new_skills.has(primary_skill):
		errors.assign(["Unknown primary skill"])
		return false
	_doc = candidate.duplicate(true)
	_skills = new_skills
	_passives = new_passives
	_primary = primary_skill
	_ranks = {primary_skill:1}
	_owned_passives.clear()
	_evolved.clear()
	_pending.clear()
	_offer.clear()
	_xp = 0
	_level = 1
	_epoch += 1
	_offer_sequence = 0
	_rng.seed = run_seed
	errors.clear()
	return true

func award_xp(amount: Variant) -> bool:
	if _doc.is_empty() or not Catalog.integer(amount,0,MAX_XP):
		errors.assign(["XP must be a bounded nonnegative integer on a configured run"])
		return false
	_xp = mini(MAX_XP,_xp+int(amount))
	var next_level := 1
	for threshold in _doc.xp_thresholds:
		if _xp >= int(threshold): next_level += 1
	next_level -= 1
	for earned in range(_level+1,next_level+1): _pending.append(earned)
	_level = next_level
	errors.clear()
	return true

func effective_skill(id_: String) -> Dictionary:
	if not _ranks.has(id_): return {}
	var rank: int = _ranks[id_]
	var definition: Dictionary = _skills[id_]
	var effect: Dictionary = definition.evolution if id_ in _evolved else definition.ranks[rank-1]
	return {"id":id_,"rank":rank,"evolved":id_ in _evolved,
		"name":definition.evolution_name if id_ in _evolved else definition.name,
		"effects":effect.duplicate(true)}

func xp_thresholds() -> Array:
	return _doc.get("xp_thresholds",[0]).duplicate()

func _eligible_cards() -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	# Catalog order is authoritative; no hash-table iteration is used for the draw.
	for s in _doc.skills:
		var rank := int(_ranks.get(s.id,0))
		if rank == 0 and _ranks.size() < int(_doc.max_active_skills):
			result.append({"id":"unlock:"+s.id,"kind":"unlock","skill_id":s.id,"rank":1,"weight":int(s.weight),"title":s.name,"after":s.ranks[0].duplicate(true)})
		elif rank > 0 and rank < 4:
			result.append({"id":"rank:%s:%d" % [s.id,rank+1],"kind":"rank","skill_id":s.id,"rank":rank+1,"weight":int(s.weight),"title":s.name,"after":s.ranks[rank].duplicate(true)})
		if rank >= 2 and not s.passive_id in _owned_passives and _owned_passives.size() < int(_doc.max_passives):
			var p: Dictionary = _passives[s.passive_id]
			result.append({"id":"passive:"+p.id,"kind":"passive","skill_id":s.id,"passive_id":p.id,"weight":int(p.weight),"title":p.name})
		if rank == 4 and s.passive_id in _owned_passives and not s.id in _evolved:
			result.append({"id":"evolve:"+s.id,"kind":"evolve","skill_id":s.id,"rank":4,"weight":int(s.weight),"title":s.evolution_name,"after":s.evolution.duplicate(true)})
	return result

func _protected_card(cards: Array[Dictionary]) -> int:
	# Keep a reachable primary evolution path; the player still chooses it or another card.
	for preferred in ["evolve","rank","passive"]:
		for i in cards.size():
			if cards[i].skill_id == _primary and cards[i].kind == preferred: return i
	return -1

func next_offer() -> Dictionary:
	if not _offer.is_empty(): return _offer.duplicate(true)
	if _doc.is_empty() or _pending.is_empty(): return {}
	var pool := _eligible_cards()
	if pool.is_empty():
		errors.assign(["No legal growth candidates"])
		return {}
	var selected: Array[Dictionary] = []
	var protected := _protected_card(pool)
	if protected >= 0:
		selected.append(pool[protected])
		pool.remove_at(protected)
	while selected.size() < 3 and not pool.is_empty():
		var total := 0
		for card in pool: total += int(card.weight)
		var roll := _rng.randi_range(1,total)
		var index := 0
		while roll > int(pool[index].weight):
			roll -= int(pool[index].weight)
			index += 1
		selected.append(pool[index])
		pool.remove_at(index)
	_offer_sequence += 1
	_offer = {"token":"%d:%d" % [_epoch,_offer_sequence],"level":_pending[0],"cards":selected}
	return _offer.duplicate(true)

func choose(token: String, card_id: String) -> bool:
	if _offer.is_empty() or token != _offer.token or _pending.is_empty():
		errors.assign(["Expired or missing growth offer"])
		return false
	var chosen: Dictionary = {}
	for card in _offer.cards:
		if card.id == card_id: chosen = card
	if chosen.is_empty():
		errors.assign(["Card was not offered"])
		return false
	match chosen.kind:
		"unlock","rank": _ranks[chosen.skill_id] = int(chosen.rank)
		"passive": _owned_passives.append(chosen.passive_id)
		"evolve": _evolved.append(chosen.skill_id)
	_pending.pop_front()
	_offer = {}
	errors.clear()
	return true

func snapshot() -> Dictionary:
	return {"xp":_xp,"level":_level,"primary":_primary,"ranks":_ranks.duplicate(true),
		"passives":_owned_passives.duplicate(),"evolved":_evolved.duplicate(),
		"pending_levels":_pending.duplicate(),"offer":_offer.duplicate(true),
		"epoch":_epoch,"rng_state":str(_rng.state)}
