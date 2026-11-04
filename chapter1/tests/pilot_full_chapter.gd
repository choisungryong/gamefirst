extends SceneTree
const Chapter=preload("res://chapter1/core/chapter_run.gd")
var run=Chapter.new()
var trace: Array[Dictionary]=[]
var selections: Array[Dictionary]=[]
var outcome: Array[Dictionary]=[]
var wall_avoidances := 0
var potion_uses := 0
func _initialize() -> void:call_deferred("execute")
func equipment_score(item: Dictionary) -> float:
	var score := 0.0
	var weights := {"damage_bps":.006,"cooldown_bps":.008,"max_hp_raw":.001,"damage_reduction_bps":.01,"pickup_radius_cm":.035,"projectiles":16,"chain_targets":10,"pierce":7,"shatter_count":5,"radius_cm":.02,"slow_bps":.002,"fire_damage_bps":.003,"fire_burst":20,"frost_threshold":20,"arc_branches":20,"arc_damage_bps":.003}
	for stat in item.stats:score+=float(item.stats[stat])*float(weights.get(stat,0))
	return score
func decide() -> Vector2:
	if run.mode=="choice":
		var offer: Dictionary=run.get_offer()
		var picked: Dictionary=offer.cards[0]
		var best := -1
		for card in offer.cards:
			var score := 10
			if card.skill_id==run.growth.snapshot().primary:score=100 if card.kind=="evolve" else (90 if card.kind=="rank" else 80)
			elif card.kind=="unlock":score=65
			elif card.kind=="evolve":score=60
			elif card.kind=="rank":score=50
			if score>best:best=score;picked=card
		selections.append({"tick":run.tick,"id":picked.id,"kind":picked.kind})
		assert(run.choose(offer.token,picked.id))
	if run.mode!="playing":return Vector2.ZERO
	for item in run.inventory:
		var current: Dictionary={}
		for owned in run.inventory:
			if run.equipped.get(item.slot,-1)==owned.uid:current=owned;break
		if current.is_empty() or equipment_score(item)>equipment_score(current)+.01:
			assert(run.open_inventory());assert(run.equip(item.uid));run.close_inventory()
	if run.hero.hp_raw*100<run.hero.max_hp_raw*68:
		if run.drink_potion():potion_uses+=1
	var center: Vector2=Chapter.ZONES[run.zone]
	var at: Vector2=run.hero.position
	var target := center+Vector2(cos(run.elapsed()*.24),sin(run.elapsed()*.24))*7
	if not run._zone_entered:
		# Route through actual 7.2m wide passage; no teleport or map bypass.
		target=Vector2(center.x-26,0) if at.x<center.x-27 else center
	else:
		var nearest := 25.0
		for pickup in run.orbs:
			var d: float=at.distance_squared_to(pickup.position)
			if d<nearest:nearest=d;target=pickup.position
		if run.potions<3:
			for pickup in run.potion_pickups:
				var d: float=at.distance_squared_to(pickup.position)
				if d<36:target=pickup.position;break
	var move: Vector2=(target-at).normalized()
	if run._zone_entered:
		var danger := Vector2.ZERO
		for e in run.enemies.values():
			if e.hp_raw<=0:continue
			var away: Vector2=at-e.position;var d := away.length()
			var safe := 3.8 if e.elite else (1.6 if e.kind=="charger" else 1.15)
			if d<safe:danger+=away.normalized()*(safe-d)/safe*(2.2 if e.elite else 1.0)
			if e.kind=="charger" and e.state=="windup" and d<6:
				danger+=e.attack_direction.orthogonal()*.9
		move=(move+danger*1.7).normalized()
		for h in run.chapter_hazards:
			var away: Vector2=at-h.position
			if away.length()<2.4:
				if away.length()<.05:away=Vector2.UP
				move=(move*.1+away.normalized()*2).normalized()
		var relative: Vector2=at-center
		if absf(relative.x)>15.5 and move.x*relative.x>0:move.x=-signf(relative.x)*.85;wall_avoidances+=1
		if absf(relative.y)>15.5 and move.y*relative.y>0:move.y=-signf(relative.y)*.85;wall_avoidances+=1
		if run.hero.hp_raw*100<run.hero.max_hp_raw*40 or danger.length()>1.2:run.request_dash(move)
	return move.limit_length(1)
func execute() -> void:
	var primary := "chapter1.skill.ember";var seed_ := 90131;var out_path := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--primary="):primary=arg.trim_prefix("--primary=")
		elif arg.begins_with("--seed="):seed_=int(arg.trim_prefix("--seed="))
		elif arg.begins_with("--output="):out_path=arg.trim_prefix("--output=")
	assert(run.start(seed_,primary))
	var iterations := 0
	while run.mode not in ["victory","defeat"] and run.tick<12*60*60 and iterations<12*60*60+500:
		var movement := decide();run.step(movement);iterations+=1
		if run.tick%600==0:
			trace.append({"tick":run.tick,"kills":run.kills,"zone":run.zone,"zone_kills":run.zone_kills,"alive":run.alive_count(),"hp_raw":run.hero.hp_raw,"potions":run.potions,"position":[run.hero.position.x,run.hero.position.y],"growth":run.growth.snapshot()})
	var result := {"primary":primary,"seed":seed_,"mode":run.mode,"elapsed":run.elapsed(),"kills":run.kills,"zone":run.zone,"hero":run.hero,"growth":run.growth.snapshot(),"chapter":run.snapshot().chapter,"metrics":run.metrics,"selections":selections,"trace":trace,"wall_avoidances":wall_avoidances,"potion_uses":potion_uses,
		"scope":"Normal input/choices/equipment/potion driver, not manual play or pacing approval. No HP/XP/loot grants or teleportation."}
	if not out_path.is_empty():
		assert(not FileAccess.file_exists(out_path));var file := FileAccess.open(out_path,FileAccess.WRITE);assert(file!=null);file.store_string(JSON.stringify(result,"  "));file.close()
	print("FULL_CHAPTER_PILOT ",JSON.stringify({"primary":primary,"seed":seed_,"mode":run.mode,"elapsed":run.elapsed(),"kills":run.kills,"zone":run.zone,"hp_raw":run.hero.hp_raw,"level":run.growth.snapshot().level,"evolved":run.growth.snapshot().evolved,"potion_uses":potion_uses,"events_dropped":run.metrics.events_dropped,"history":run.history}))
	quit(0)
