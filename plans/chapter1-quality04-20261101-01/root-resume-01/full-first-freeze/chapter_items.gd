extends RefCounted
## Independent item grammar for the full chapter. No D2 assets/data/code.
## One base, quality-specific affixes, no duplicate affix group, bounded stats.
const BASES := [
	{"id":"cinder_staff","name":"잿불 지팡이","slot":"weapon","level":1,"stats":{"damage_bps":800,"projectiles":1}},
	{"id":"swift_wand","name":"박동의 마법봉","slot":"weapon","level":1,"stats":{"damage_bps":500,"cooldown_bps":1200}},
	{"id":"piercing_sceptre","name":"관통의 홀","slot":"weapon","level":3,"stats":{"damage_bps":1400,"pierce":1}},
	{"id":"linen_robe","name":"순례자의 로브","slot":"body","level":1,"stats":{"max_hp_raw":5120,"damage_reduction_bps":300}},
	{"id":"iron_vest","name":"쇠실 흉의","slot":"body","level":2,"stats":{"max_hp_raw":8960,"damage_reduction_bps":600,"cooldown_bps":-500}},
	{"id":"warden_mantle","name":"수문장의 외투","slot":"body","level":3,"stats":{"max_hp_raw":3840,"damage_reduction_bps":700,"pickup_radius_cm":40}},
	{"id":"winter_shard","name":"겨울 파편","slot":"charm","level":1,"stats":{"slow_bps":1200,"max_hp_raw":2560}},
	{"id":"ember_lens","name":"잿불 렌즈","slot":"charm","level":2,"stats":{"radius_cm":40,"fire_damage_bps":1000}},
	{"id":"chain_knot","name":"연쇄 매듭","slot":"charm","level":3,"stats":{"chain_targets":1,"damage_bps":-300}},
	{"id":"quick_loop","name":"은빛 고리","slot":"ring","level":1,"stats":{"cooldown_bps":500,"pickup_radius_cm":40}},
	{"id":"glass_ring","name":"유리 반지","slot":"ring","level":2,"stats":{"damage_bps":1200,"max_hp_raw":-2560}},
	{"id":"ward_ring","name":"봉인의 반지","slot":"ring","level":3,"stats":{"damage_reduction_bps":500,"max_hp_raw":3072}}
]
const AFFIXES := [
	{"id":"wrath","name":"격노","group":"damage","slots":["weapon","ring","charm"],"level":1,"stat":"damage_bps","low":800,"high":1800,"weight":100},
	{"id":"haste","name":"신속","group":"haste","slots":["weapon","ring","charm"],"level":1,"stat":"cooldown_bps","low":500,"high":1200,"weight":100},
	{"id":"vigor","name":"활력","group":"health","slots":["body","ring","charm"],"level":1,"stat":"max_hp_raw","low":3072,"high":6656,"weight":100},
	{"id":"ward","name":"보호","group":"ward","slots":["body","ring"],"level":1,"stat":"damage_reduction_bps","low":300,"high":700,"weight":100},
	{"id":"harvest","name":"수확","group":"harvest","slots":["body","ring","charm"],"level":1,"stat":"pickup_radius_cm","low":40,"high":100,"weight":100},
	{"id":"volley","name":"다중","group":"shape","slots":["weapon"],"level":2,"stat":"projectiles","low":1,"high":1,"weight":35},
	{"id":"pierce","name":"꿰뚫음","group":"shape","slots":["weapon","ring"],"level":3,"stat":"pierce","low":1,"high":1,"weight":55},
	{"id":"conductor","name":"도체","group":"chain","slots":["weapon","ring","charm"],"level":3,"stat":"chain_targets","low":1,"high":2,"weight":60},
	{"id":"shatter","name":"파쇄","group":"shatter","slots":["weapon","ring","charm"],"level":4,"stat":"shatter_count","low":1,"high":2,"weight":60},
	{"id":"expanse","name":"확장","group":"area","slots":["weapon","charm"],"level":3,"stat":"radius_cm","low":30,"high":70,"weight":65},
	{"id":"binding","name":"결박","group":"slow","slots":["weapon","charm","body"],"level":3,"stat":"slow_bps","low":600,"high":1400,"weight":65},
	{"id":"flame","name":"불꽃","group":"damage","slots":["weapon","ring","charm"],"level":2,"stat":"fire_damage_bps","low":500,"high":1500,"weight":85}
]
const UNIQUES := [
	{"id":"ash_bloom","name":"잿꽃의 유언","slot":"weapon","stats":{"damage_bps":-1000,"projectiles":1,"fire_burst":1},"description":"화염 처치 폭발 · 피해 -10% · 발사체 +1"},
	{"id":"winter_heart","name":"겨울의 심장","slot":"charm","stats":{"cooldown_bps":-500,"frost_threshold":1,"shatter_count":2},"description":"서리 빙결 문턱 -1(최소2회) · 파쇄 +2 · 기술 주기 증가"},
	{"id":"forked_covenant","name":"갈림길의 서약","slot":"ring","stats":{"arc_branches":1,"arc_damage_bps":-1200,"chain_targets":1},"description":"번개 분기 +1 · 연쇄 +1 · 번개 피해 -12%"}
]
const LIMITS := {"damage_bps":[-5000,30000],"cooldown_bps":[-5000,10000],"max_hp_raw":[-12800,76800],"damage_reduction_bps":[0,6000],"pickup_radius_cm":[0,800],"projectiles":[0,4],"pierce":[0,4],"chain_targets":[0,8],"shatter_count":[0,8],"radius_cm":[0,250],"slow_bps":[0,5000],"fire_damage_bps":[0,10000],"fire_burst":[0,1],"frost_threshold":[0,1],"arc_branches":[0,1],"arc_damage_bps":[-5000,10000]}

static func roll(rng: RandomNumberGenerator, level: int, quality: String="", forced_slot: String="") -> Dictionary:
	level=clampi(level,1,12)
	if quality.is_empty():
		var q := rng.randi_range(0,99)
		quality="common" if q<30 else ("magic" if q<85 else "rare")
	assert(quality in ["common","magic","rare"])
	var pool: Array=[]
	for base in BASES:
		if base.level<=level and (forced_slot.is_empty() or base.slot==forced_slot):pool.append(base)
	assert(not pool.is_empty())
	var base: Dictionary=pool[rng.randi_range(0,pool.size()-1)]
	var result := {"base_id":"chapter1.full."+base.id,"name":base.name,"slot":base.slot,"stats":base.stats.duplicate(true),"quality":quality,"item_level":level,"affixes":[],"description":""}
	var candidates: Array=[]
	for affix in AFFIXES:
		if affix.level<=level and base.slot in affix.slots:candidates.append(affix)
	var count := 0 if quality=="common" else (1 if quality=="magic" else 2)
	for i in count:
		if candidates.is_empty():break
		var total := 0
		for a in candidates:total+=a.weight
		var draw := rng.randi_range(1,total)
		var picked: Dictionary={}
		for a in candidates:
			draw-=a.weight
			if draw<=0:picked=a;break
		var amount := rng.randi_range(picked.low,picked.high)
		result.stats[picked.stat]=int(result.stats.get(picked.stat,0))+amount
		result.affixes.append({"id":picked.id,"group":picked.group,"stat":picked.stat,"value":amount})
		result.name=picked.name+"의 "+result.name
		var remaining: Array=[]
		for a in candidates:
			if a.group!=picked.group:remaining.append(a)
		candidates=remaining
	assert(validate(result).is_empty())
	return result

static func unique(index: int, level: int) -> Dictionary:
	var item: Dictionary=UNIQUES[clampi(index,0,2)].duplicate(true)
	item.base_id="chapter1.full.unique."+item.id;item.erase("id")
	item.quality="unique";item.item_level=clampi(level,1,12);item.affixes=[]
	assert(validate(item).is_empty())
	return item

static func validate(item: Dictionary) -> Array[String]:
	var issues: Array[String]=[]
	for key in ["base_id","name","slot","stats","quality","item_level","affixes","description"]:
		if not item.has(key):issues.append("Missing "+key)
	if not issues.is_empty():return issues
	if not item.slot in ["weapon","body","charm","ring"]:issues.append("Unknown slot")
	if not item.quality in ["common","magic","rare","unique"]:issues.append("Unknown quality")
	if not item.stats is Dictionary or not item.affixes is Array:return ["Stats/affixes shape"]
	if item.item_level<1 or item.item_level>12:issues.append("Item level")
	var groups: Array=[]
	for a in item.affixes:
		if not a is Dictionary or not a.has_all(["id","group","stat","value"]):return ["Affix shape"]
		if a.group in groups:issues.append("Duplicate affix group")
		groups.append(a.group)
		var found := false
		for def in AFFIXES:
			if def.id==a.id:
				found=true
				if a.group!=def.group or a.stat!=def.stat or not item.slot in def.slots or item.item_level<def.level or a.value<def.low or a.value>def.high:issues.append("Affix eligibility/range")
		if not found:issues.append("Unknown affix")
	var allowed_count := 0 if item.quality in ["common","unique"] else (1 if item.quality=="magic" else 2)
	if item.affixes.size()!=allowed_count:issues.append("Affix count")
	for stat in item.stats:
		if not LIMITS.has(stat):issues.append("Unknown stat")
		elif not item.stats[stat] is int or item.stats[stat]<LIMITS[stat][0] or item.stats[stat]>LIMITS[stat][1]:issues.append("Stat range/type")
	return issues
