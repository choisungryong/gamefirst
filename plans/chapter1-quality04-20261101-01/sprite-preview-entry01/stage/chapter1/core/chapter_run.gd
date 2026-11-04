extends "res://chapter1/core/combat_run.gd"
## Complete-chapter simulation branch. Representative encounter remains intact.
const Items=preload("res://chapter1/core/chapter_items.gd")
const ZONES := [Vector2(0,0),Vector2(48,0),Vector2(96,0)]
const ZONE_NAMES := ["잿빛 앞뜰","무너진 성가대","재의 성소"]
const SEAL_KILLS := [600,900,900]
const FULL_XP := [0,12,36,72,120,180,260,380,560,820,1180,1640]
const RITUALS := [
	{"id":"vigil","name":"꺼지지 않는 불씨","position":Vector2(8,-7),"zone":0,"kind":"hold"},
	{"id":"reliquary","name":"봉인된 성유물","position":Vector2(40,6),"zone":1,"kind":"kill"}
]
var zone := 0
var zone_kills := 0
var seals: Array[Dictionary]=[]
var potions := 3
var potion_pickups: Array[Dictionary]=[]
var pending_rewards: Array[Dictionary]=[]
var chapter_hazards: Array[Dictionary]=[]
var rituals: Dictionary={}
var history: Array[Dictionary]=[]
var _next_potion := 0
var _champion_id := -1
var _boss_phase := 0
var _next_ward := 0
var _hazard_sequence := 0
var _potion_sequence := 0
var _zone_entered := false
var _normal_drop_sequence := 0
var _ritual_spawn_tick := 0

func start(seed_: int=1, primary: String="chapter1.skill.ember") -> bool:
	zone=0;zone_kills=0;potions=3;_next_potion=0;_champion_id=-1;_boss_phase=0;_next_ward=0
	_hazard_sequence=0;_potion_sequence=0;_zone_entered=true;_normal_drop_sequence=0;_ritual_spawn_tick=0
	seals.clear();history.clear();potion_pickups.clear();pending_rewards.clear();chapter_hazards.clear();rituals.clear()
	for i in 3:seals.append({"kills":0,"champion_spawned":false,"cleared":false})
	for def in RITUALS:rituals[def.id]={"state":"ready","progress":0,"started_tick":-1,"completed_tick":-1}
	if not super.start(seed_,primary):return false
	var doc: Dictionary=_catalog.snapshot();doc.xp_thresholds=FULL_XP.duplicate()
	if not growth.configure(doc,primary,seed_ ^ 0x47524f57):errors.assign(growth.errors);return false
	_record("chapter_started")
	return true

func _record(type: String) -> void:
	history.append({"type":type,"tick":tick,"zone":zone,"kills":kills,"zone_kills":zone_kills,"hp_raw":hero.get("hp_raw",0)})

func _initial_pack_count() -> int:
	return 12

func _clamp_point(point: Vector2) -> Vector2:
	var best := Vector2.ZERO
	var distance := INF
	for i in range(zone+1):
		var center: Vector2=ZONES[i]
		var candidate := point.clamp(center-Vector2.ONE*19,center+Vector2.ONE*19)
		var d := point.distance_squared_to(candidate)
		if d<distance:best=candidate;distance=d
		if i>0:
			candidate=point.clamp(Vector2(center.x-29,-3.6),Vector2(center.x-19,3.6))
			d=point.distance_squared_to(candidate)
			if d<distance:best=candidate;distance=d
	return best

func _spawn_point(min_radius: float,max_radius: float) -> Vector2:
	for attempt in 16:
		var angle := _spawn_rng.randf_range(0,TAU)
		var point := _clamp_point(hero.position+Vector2(cos(angle),sin(angle))*_spawn_rng.randf_range(min_radius,max_radius))
		if point.distance_squared_to(hero.position)>=min_radius*min_radius*.64:return point
	var inward: Vector2=(ZONES[zone]-hero.position).normalized()
	if inward.length_squared()<.01:inward=Vector2.LEFT
	return _clamp_point(hero.position+inward*min_radius)

func _spawn(kind: String,point: Vector2) -> bool:
	if not super._spawn(kind,point):return false
	var e: Dictionary=enemies[_enemy_sequence]
	var definition: Dictionary=ENEMY_DEFS[kind].duplicate(true)
	# Opening trash must actually die to the first shot from every primary.
	# Distributing rank1 hits across 16HP bodies delayed all growth in pilot01.
	if kind=="walker":definition.hp=9 if tick<30*HZ else 12+zone*3
	elif kind=="ranged":definition.hp=18+zone*6
	elif kind=="charger":definition.hp=32+zone*8
	e.definition=definition
	e.hp_raw=int(definition.hp)*UNIT;e.max_hp_raw=e.hp_raw
	return true

func _enemy_definition(e: Dictionary) -> Dictionary:
	return e.get("definition",ENEMY_DEFS[e.kind])

func _spawn_wave() -> void:
	if not _zone_entered:
		if hero.position.distance_squared_to(ZONES[zone])>18.0*18.0:return
		_zone_entered=true;_record("zone_entered");_emit("zone_entered",ZONES[zone],{"zone":zone})
	if not seals[zone].champion_spawned and zone_kills>=SEAL_KILLS[zone]:
		if _spawn("elite",_spawn_point(8,9)):
			seals[zone].champion_spawned=true;_champion_id=_enemy_sequence
			var e: Dictionary=enemies[_champion_id]
			e.chapter_boss=zone==2;e.title=["잿불의 문지기","서리의 성가대장","회랑의 파수왕"][zone]
			e.definition.hp=[1400,2200,4500][zone];e.definition.windup=[54,48,54][zone]
			e.definition.recover=[96,84,90][zone];e.definition.damage=[12,14,18][zone]
			e.definition.xp=[20,30,60][zone];e.hp_raw=int(e.definition.hp)*UNIT;e.max_hp_raw=e.hp_raw
			_boss_phase=1 if zone==2 else 0;_next_ward=tick+3*HZ
			_record("boss_spawned" if zone==2 else "champion_spawned")
			_emit("chapter_champion",e.position,{"zone":zone,"target_id":e.id,"name":e.title})
	if tick<_next_spawn:return
	# Frequent weak bodies provide sweepable packs, mixed with bounded specialists.
	var amount := 1 if tick<10*HZ else (3 if tick<30*HZ else (6 if zone==0 else (8 if zone==1 else 10)))
	var interval := 48 if zone==0 else 42
	if zone==2 and _champion_id>0:amount=4;interval=60
	_next_spawn=tick+interval
	var count := alive_count()
	for i in amount:
		if count>=MAX_ALIVE-2:break
		var roll := _spawn_rng.randi_range(0,99)
		var kind := "walker"
		if tick>=12*HZ and roll>=(94-zone*3):kind="charger"
		elif tick>=10*HZ and roll>=(82-zone*3):kind="ranged"
		if _spawn(kind,_spawn_point(9.0,12.0)):count+=1

func _step_enemies() -> void:
	# The second champion trades the sentinel's close circle for a paid frost
	# cross. The exact same four capsules are used by telegraph and resolution.
	if zone==1 and _champion_id>0 and enemies.has(_champion_id):
		var e: Dictionary=enemies[_champion_id]
		if e.hp_raw>0 and e.state=="move" and tick>=int(e.frozen_until) and int(e.attack_index)%2==0 and e.position.distance_squared_to(hero.position)<=36:
			e.attack_direction=(hero.position-e.position).normalized()
			e.attack_kind="frost_cross";e.state="windup";e.state_until=tick+int(e.definition.windup)
			var direction: Vector2=e.attack_direction
			e.telegraph={"shape":"line","direction":direction,"radius":5.7,"length":4.8,"width":1.8,"rays":[direction,-direction,direction.orthogonal(),-direction.orthogonal()],"remaining_ticks":int(e.definition.windup)}
	super._step_enemies()

func _resolve_elite_attack(e: Dictionary,definition: Dictionary,distance: float) -> void:
	if e.attack_kind!="frost_cross":super._resolve_elite_attack(e,definition,distance);return
	for direction in [e.attack_direction,e.attack_direction.orthogonal()]:
		if _segment_distance_sq(hero.position,e.position-direction*4.8,e.position+direction*4.8)<=.9*.9:
			_hero_damage(int(definition.damage)*UNIT,e.position);break

func _emit(type: String,position: Vector2,details: Dictionary={}) -> void:
	super._emit(type,position,details)
	if type=="death" and _zone_entered and position.distance_squared_to(ZONES[zone])<26.0*26.0:
		zone_kills+=1;seals[zone].kills=zone_kills
		for def in RITUALS:
			if rituals.has(def.id) and rituals[def.id].state=="active" and def.kind=="kill" and position.distance_squared_to(def.position)<10.0*10.0:
				rituals[def.id].progress+=1
		if not details.get("elite",false) and _loot_rng.randi_range(0,89)==0:_drop_potion(position)

func _on_elite_defeated(e: Dictionary) -> void:
	seals[zone].cleared=true;_record("seal_cleared");_elite_killed=false;_champion_id=-1
	if zone==2:
		chapter_hazards.clear();_boss_phase=0
		super._on_elite_defeated(e)
		_record("chapter_completed")
	else:
		_drop_potion(e.position);_drop_potion(e.position+Vector2(.4,0))
		zone+=1;zone_kills=0;_zone_entered=false
		_emit("gate_opened",ZONES[zone]-Vector2(24,0),{"zone":zone,"name":ZONE_NAMES[zone]})
		_record("gate_opened")

func _maybe_drop_item(e: Dictionary) -> void:
	var forced_slots := ["weapon","body","charm","ring"]
	var thresholds := [6,35,90,160]
	var forced: bool=_guaranteed_drops<thresholds.size() and kills>=thresholds[_guaranteed_drops]
	if not e.elite and not forced and _loot_rng.randi_range(0,99)>=1:return
	if not e.elite and (items.size()>=MAX_GROUND_ITEMS or inventory.size()>=MAX_INVENTORY):return
	var item: Dictionary
	if e.get("chapter_boss",false):
		var primary_: String=growth.snapshot().primary
		item=Items.unique(["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"].find(primary_),growth.snapshot().level)
	else:
		item=Items.roll(_loot_rng,growth.snapshot().level,"rare" if e.elite else ("magic" if forced else ""),forced_slots[_guaranteed_drops] if forced else "")
	if forced:_guaranteed_drops+=1
	_publish_item(item,e.position,e.elite,e.get("chapter_boss",false))

func _publish_item(item: Dictionary,point: Vector2,direct: bool,boss_reward: bool=false) -> void:
	_item_sequence+=1;item.uid=_item_sequence;item.position=point;item.collected=direct;item.drop_tick=tick
	item.objective_reward=boss_reward;metrics.dropped_items+=1
	_emit("item_drop",point,{"item":item.duplicate(true)})
	if direct:
		if inventory.size()<MAX_INVENTORY or (boss_reward and inventory.size()<MAX_INVENTORY+1):
			inventory.append(item);metrics.picked_items+=1
			if boss_reward:_elite_reward_uid=item.uid
			_emit("item_pickup",hero.position,{"item":item.duplicate(true)})
		else:
			# Two champions + two optional trials fit four deferred ordinary rewards.
			assert(pending_rewards.size()<4);pending_rewards.append(item)
			_emit("reward_pending",hero.position,{"item":item.duplicate(true)})
	else:items.append(item)

func effective_skill(id_: String) -> Dictionary:
	var value: Dictionary=super.effective_skill(id_)
	if value.is_empty():return value
	var effect: Dictionary=value.effects
	var extra_pierce := int(_gear_stats.get("pierce",0))
	effect.pierce=mini(8,int(effect.pierce)+extra_pierce)
	effect.hit_budget=mini(128,int(effect.hit_budget)+extra_pierce*maxi(1,int(effect.projectiles)))
	if id_ in ["chapter1.skill.ember","chapter1.skill.arc"] and int(effect.radius_cm)>0:effect.radius_cm=mini(650,int(effect.radius_cm)+int(_gear_stats.get("radius_cm",0)))
	if id_=="chapter1.skill.ember":
		effect.damage_raw=int(effect.damage_raw)*(10000+int(_gear_stats.get("fire_damage_bps",0)))/10000
		if _gear_stats.get("fire_burst",0)>0:
			effect.death_burst=1;effect.proc_depth=1;effect.radius_cm=maxi(200,int(effect.radius_cm));effect.hit_budget=maxi(32,int(effect.hit_budget))
	elif id_=="chapter1.skill.frost":
		effect.slow_bps=mini(8500,int(effect.slow_bps)+int(_gear_stats.get("slow_bps",0)))
		if _gear_stats.get("frost_threshold",0)>0:
			effect.freeze_stacks=maxi(2,int(effect.freeze_stacks)-1) if effect.freeze_stacks>0 else 2
			effect.shatter_count=mini(16,maxi(2,int(effect.shatter_count)))
			effect.hit_budget=maxi(12,int(effect.hit_budget))
	elif id_=="chapter1.skill.arc":
		effect.branches=mini(3,int(effect.branches)+int(_gear_stats.get("arc_branches",0)))
		if _gear_stats.get("arc_branches",0)>0:effect.hit_budget=mini(128,maxi(int(effect.hit_budget),int(effect.branches)*int(effect.chain_targets)))
		effect.damage_raw=int(effect.damage_raw)*(10000+int(_gear_stats.get("arc_damage_bps",0)))/10000
	return value

func import_starting_gear(gear: Array[Dictionary]) -> bool:
	if mode!="playing" or tick!=0 or not inventory.is_empty() or gear.size()>4:return false
	var slots := {}
	for item in gear:
		if not Items.validate(item).is_empty() or not item.has("storage_id") or slots.has(item.slot):return false
		slots[item.slot]=true
	for source in gear:
		var item: Dictionary=source.duplicate(true);_item_sequence+=1;item.uid=_item_sequence;item.collected=true;item.drop_tick=0;item.position=hero.position
		inventory.append(item);equipped[item.slot]=item.uid
	_recompute_gear()
	# Full health only at a fresh run boundary. Mid-run equipment never heals.
	hero.hp_raw=hero.max_hp_raw
	return true

func _drop_potion(point: Vector2) -> void:
	if potion_pickups.size()>=16:return
	_potion_sequence+=1;potion_pickups.append({"uid":_potion_sequence,"position":point,"tick":tick})
	_emit("potion_drop",point,{})

func drink_potion() -> bool:
	if mode!="playing" or potions<=0 or tick<_next_potion or hero.hp_raw>=hero.max_hp_raw:return false
	potions-=1;_next_potion=tick+4*HZ
	var amount: int=maxi(1,int(hero.max_hp_raw)*35/100)
	hero.hp_raw=mini(int(hero.max_hp_raw),int(hero.hp_raw)+amount)
	_emit("potion_used",hero.position,{"amount_raw":amount,"remaining":potions})
	return true

func activate_ritual(id_: String) -> bool:
	if mode!="playing" or not rituals.has(id_) or rituals[id_].state!="ready":return false
	for def in RITUALS:
		if def.id==id_ and def.zone==zone and hero.position.distance_squared_to(def.position)<=3.0*3.0:
			rituals[id_].state="active";rituals[id_].started_tick=tick;_record("ritual_started:"+id_)
			_emit("ritual_started",def.position,{"id":id_,"name":def.name});return true
	return false

func _step_rituals() -> void:
	for def in RITUALS:
		var state: Dictionary=rituals[def.id]
		if state.state!="active":continue
		if def.zone!=zone:state.state="abandoned";continue
		var close_: bool=hero.position.distance_squared_to(def.position)<5.0*5.0
		if def.kind=="hold" and close_:state.progress+=1
		if close_ and tick>=_ritual_spawn_tick:
			_ritual_spawn_tick=tick+3*HZ
			for i in 8:
				if alive_count()<MAX_ALIVE-2:_spawn("walker" if i<6 else "charger",_spawn_point(7,9))
		var target := 25*HZ if def.kind=="hold" else 60
		if state.progress>=target:
			state.state="completed";state.completed_tick=tick;_record("ritual_completed:"+def.id)
			_publish_item(Items.roll(_loot_rng,growth.snapshot().level,"rare"),def.position,true)
			_drop_potion(def.position);_emit("ritual_completed",def.position,{"id":def.id,"name":def.name})

func _step_chapter_hazards() -> void:
	if _champion_id<=0 or not enemies.has(_champion_id) or zone!=2:return
	var boss: Dictionary=enemies[_champion_id]
	if boss.hp_raw<=0:return
	if _boss_phase==1 and int(boss.hp_raw)*2<=int(boss.max_hp_raw):
		_boss_phase=2;boss.definition.recover=65;_next_ward=mini(_next_ward,tick+HZ)
		_record("boss_phase2");_emit("boss_phase",boss.position,{"phase":2})
	if tick>=_next_ward:
		_next_ward=tick+(4*HZ if _boss_phase==1 else 3*HZ)
		var centers: Array[Vector2]=[hero.position]
		if _boss_phase==2:
			centers.append(_clamp_point(hero.position+hero.direction.rotated(PI*.5)*3.8))
			centers.append(_clamp_point(hero.position-hero.direction.rotated(PI*.5)*3.8))
		for center in centers:
			_hazard_sequence+=1
			chapter_hazards.append({"uid":_hazard_sequence,"position":center,"radius":1.8,"started":tick,"expires":tick+72,"damage_raw":20*UNIT})
			_emit("chapter_warning",center,{"radius":1.8,"duration_ticks":72})
	var live: Array[Dictionary]=[]
	for hazard in chapter_hazards:
		if tick<hazard.expires:live.append(hazard);continue
		if hero.position.distance_squared_to(hazard.position)<=pow(float(hazard.radius),2):_hero_damage(hazard.damage_raw,hazard.position)
		_emit("chapter_burst",hazard.position,{"radius":hazard.radius})
	chapter_hazards=live

func step(move: Vector2=Vector2.ZERO) -> void:
	if mode!="playing":return
	super.step(move)
	if mode!="playing":return
	_step_chapter_hazards()
	if mode!="playing":return
	_step_rituals()
	var live: Array[Dictionary]=[]
	for pickup in potion_pickups:
		if potions<5 and hero.position.distance_squared_to(pickup.position)<1.6*1.6:
			potions+=1;_emit("potion_pickup",pickup.position,{"remaining":potions})
		elif tick-pickup.tick<180*HZ:live.append(pickup)
	potion_pickups=live

func objective() -> Dictionary:
	var title: String=ZONE_NAMES[zone]
	var text := "봉인 주변 처치 %d / %d"%[mini(zone_kills,SEAL_KILLS[zone]),SEAL_KILLS[zone]]
	var destination: Vector2=ZONES[zone]
	if not _zone_entered:text="열린 동쪽 회랑을 따라 다음 마당으로 이동"
	elif _champion_id>0 and enemies.has(_champion_id):
		var e: Dictionary=enemies[_champion_id];title=e.get("title",title);text="%d / %d"%[ceili(float(e.hp_raw)/UNIT),ceili(float(e.max_hp_raw)/UNIT)]
	return {"zone":zone,"title":title,"text":text,"destination":destination,"boss_phase":_boss_phase,"entered":_zone_entered}

func snapshot() -> Dictionary:
	var result: Dictionary=super.snapshot()
	result.chapter={"zone":zone,"zone_kills":zone_kills,"seals":seals.duplicate(true),"potions":potions,"pending_rewards":pending_rewards.duplicate(true),"rituals":rituals.duplicate(true),"history":history.duplicate(true),"boss_phase":_boss_phase,"hazards":chapter_hazards.duplicate(true)}
	return result
