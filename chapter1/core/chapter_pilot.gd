extends RefCounted
## Explicit QA normal input policy; no resource grants.
const Chapter=preload("res://chapter1/core/chapter_run.gd")
var run: RefCounted
var selections: Array[Dictionary]=[]
var wall_avoidances := 0
var potion_uses := 0
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
		if not run.choose(offer.token,picked.id):push_error("QA growth choice rejected");return Vector2.ZERO
	if run.mode!="playing":return Vector2.ZERO
	for item in run.inventory:
		var current: Dictionary={}
		for owned in run.inventory:
			if run.equipped.get(item.slot,-1)==owned.uid:current=owned;break
		if current.is_empty() or equipment_score(item)>equipment_score(current)+.01:
			if not run.open_inventory():push_error("QA inventory open rejected");return Vector2.ZERO
			if not run.equip(item.uid):push_error("QA equipment rejected");run.close_inventory();return Vector2.ZERO
			run.close_inventory()
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
