extends "res://chapter1/core/chapter_run_stun36.gd"
## Independent full-chapter cold evolution rule. Original14 core remains intact.
## Evolved direct cold kills crystallize without requiring a surviving freeze.
## Secondary shards:50% normal/25%elite damage, same paid effects/hit budget,
## one proc depth. Other skills and non-evolved frozen shatter stay unchanged.
const ARC_STUN_TICKS36 := 18
const ARC_ELITE_STUN_TICKS36 := 6
const ARC_STUN_IMMUNITY36 := 120
const ARC_ELITE_IMMUNITY36 := 180
func _damage_enemy(id_: int,context: Dictionary,depth: int) -> void:
    if not _terminal_mode.is_empty() or not enemies.has(id_) or int(context.remaining_hits)<=0:return
    var e: Dictionary=enemies[id_]
    if e.hp_raw<=0 or e.generation!=_epoch:return
    if context.skill_id=="chapter1.skill.arc":
        if id_ in context.hit_ids:return
        context.hit_ids.append(id_)
    context.remaining_hits-=1
    var effect: Dictionary=context.effects
    var was_frozen: bool=tick<int(e.frozen_until)
    var damage: int=effect.damage_raw
    var evolved_cold: bool=context.skill_id=="chapter1.skill.frost" and bool(context.evolved)
    if evolved_cold and depth>0:
        var divisor := 4 if e.elite else 2
        damage=maxi(1,int((damage+divisor-1)/divisor))
    var result: Dictionary=Resolver.damage(damage,int(e.hp_raw))
    e.hp_raw=int(result.hp_after_raw);metrics.damage_raw+=int(result.total_raw)
    metrics.hits[context.skill_id]=int(metrics.hits.get(context.skill_id,0))+1
    if context.skill_id=="chapter1.skill.frost":
        e.slow_until=tick+100;e.slow_bps=int(effect.slow_bps)
        if int(effect.freeze_stacks)>0:
            e.freeze_stacks+=1;e.freeze_expires=tick+180
            if int(e.freeze_stacks)>=int(effect.freeze_stacks):
                e.frozen_until=tick+(12 if e.elite else 75);e.freeze_stacks=0
    var cold_death: bool=evolved_cold and e.hp_raw<=0 and depth==0 and int(effect.proc_depth)>0
    var shatter: bool=int(effect.shatter_count)>0 and (was_frozen or cold_death)
    _emit("hit",e.position,{"target_id":id_,"skill_id":context.skill_id,"damage_raw":int(result.total_raw),"frozen":tick<int(e.frozen_until),"shatter":shatter,
        "radius_cm":int(effect.radius_cm),"blast_radius_cm":int(effect.radius_cm)if context.skill_id=="chapter1.skill.ember"else 0,"cast_uid":context.uid,"evolved":context.evolved})
    # Shock is separate from cold: no freeze stacks, cold tint or shatter credit.
    # Primary chain contacts only; secondary death explosions cannot restun.
    if e.hp_raw>0 and context.skill_id=="chapter1.skill.arc" and depth==0 and tick>=int(e.get("shock_ready_tick",0)):
        var duration: int=ARC_ELITE_STUN_TICKS36 if e.elite else ARC_STUN_TICKS36
        e.stunned_until=tick+duration
        e.shock_ready_tick=tick+(ARC_ELITE_IMMUNITY36 if e.elite else ARC_STUN_IMMUNITY36)
        _emit("stun",e.position,{"target_id":id_,"skill_id":context.skill_id,"until_tick":e.stunned_until,"duration_ticks":duration,"elite":e.elite})
    if e.hp_raw>0:return
    e.state="dead";e.dead_tick=tick;e.telegraph={};kills+=1
    _emit("death",e.position,{"target_id":id_,"kind":e.kind,"elite":e.elite,"skill_id":context.skill_id})
    _drop_orb(e.position,int(_enemy_definition(e).xp));_maybe_drop_item(e)
    if depth<int(effect.proc_depth)and int(effect.death_burst)>0:
        var burst_radius := 3.0 if context.skill_id=="chapter1.skill.arc"else maxf(1.5,float(effect.radius_cm)/100.0)
        _emit("explosion",e.position,{"skill_id":context.skill_id,"radius_cm":int(burst_radius*100),"cast_uid":context.uid,"evolved":context.evolved,"proc":true})
        _area_hit(e.position,burst_radius,context,id_,depth+1)
    if shatter and depth==0:
        _emit("shatter",e.position,{"skill_id":context.skill_id,"radius_cm":350,"count":int(effect.shatter_count),"cast_uid":context.uid,"evolved":context.evolved,
            "cause":"cold_death"if cold_death and not was_frozen else"frozen","normal_damage_divisor":2 if evolved_cold else 1,"elite_damage_divisor":4 if evolved_cold else 1})
        var remaining: int=effect.shatter_count
        for other in _near(e.position,3.5):
            if other==id_ or remaining<=0:continue
            _damage_enemy(other,context,1);remaining-=1
    if e.elite:_on_elite_defeated(e)

var _world_uniques36: Dictionary={}
func start(seed_: int=1, primary: String="chapter1.skill.ember") -> bool:
 _world_uniques36.clear()
 return super.start(seed_,primary)
func _maybe_drop_item(e: Dictionary) -> void:
 var forced_slots := ["weapon","body","charm","ring"]
 var thresholds := [6,35,90,160]
 var forced: bool=_guaranteed_drops<thresholds.size() and kills>=thresholds[_guaranteed_drops]
 if not e.elite and not forced and _loot_rng.randi_range(0,99)>=1:return
 if not e.elite and (items.size()>=MAX_GROUND_ITEMS or inventory.size()>=MAX_INVENTORY):return
 var item: Dictionary
 var level: int=growth.snapshot().level
 if e.get("chapter_boss",false):
  item=Items.unique(["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"].find(growth.snapshot().primary),level)
 else:
  var chance: int=1200 if e.elite else 400
  var unique_drop: bool=not forced and level>=3 and _world_uniques36.size()<2 and _loot_rng.randi_range(0,9999)<chance
  if unique_drop:
   var available: Array[int]=[]
   for index in 3:
    if not _world_uniques36.has(index):available.append(index)
   var selected: int=available[_loot_rng.randi_range(0,available.size()-1)]
   item=Items.unique(selected,level);_world_uniques36[selected]=true
  else:item=Items.roll(_loot_rng,level,"rare" if e.elite else ("magic" if forced else ""),forced_slots[_guaranteed_drops] if forced else "")
 if forced:_guaranteed_drops+=1
 _publish_item(item,e.position,e.elite,e.get("chapter_boss",false))
func snapshot() -> Dictionary:
 var value: Dictionary=super.snapshot()
 value.world_uniques36=_world_uniques36.keys()
 value.world_uniques36.sort()
 return value
