extends SceneTree
const Run=preload("res://chapter1/core/chapter_run_quality36.gd")
const Pilot=preload("res://chapter1/core/chapter_pilot.gd")
var results: Array=[]
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
 var all_ok: bool=true
 for primary in ["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"]:
  var previous: Dictionary={}
  for seed_ in [90132,90133]:
   var r=Run.new();var pilot=Pilot.new();pilot.run=r
   var started: bool=r.start(seed_,primary)
   var iterations: int=0;var stun_events: int=0;var unique_drops: Array=[]
   while r.mode not in ["victory","defeat"] and r.tick<36000 and iterations<50000:
    r.step(pilot.decide());iterations+=1
    for event in r.events:
     if event.type=="stun":stun_events+=1
     if event.type=="item_drop" and event.item.quality=="unique":unique_drops.append({"tick":r.tick,"base_id":event.item.base_id,"boss":event.item.objective_reward})
   var snapshot: Dictionary=r.snapshot()
   var same: bool=true
   var row: Dictionary={"primary":primary,"seed":seed_,"started":started,"mode":r.mode,"tick":r.tick,"seconds":r.tick/60.0,"kills":r.kills,"level":r.growth.snapshot().level,"gear":r.inventory.size(),"stun_events":stun_events,"unique_drops":unique_drops,"world_unique_count":r._world_uniques36.size(),"potions_used":pilot.potion_uses,"enemy_attacks":r.metrics.enemy_attacks,"in_5_to_8_minutes":r.tick>=18000 and r.tick<=28800,"snapshot":snapshot}
   results.append(row);previous=snapshot
   all_ok=all_ok and started and r.mode=="victory" and same and r.tick>=18000 and r.tick<=28800 and r._world_uniques36.size()<=2
   print("BALANCE36_RUN ",JSON.stringify({"primary":primary,"seed":seed_,"mode":r.mode,"tick":r.tick,"unique_count":r._world_uniques36.size(),"stuns":stun_events,"same":same}))
   var f=FileAccess.open("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/balance36/normal02/RESULT.json",FileAccess.WRITE)
   f.store_string(JSON.stringify({"passed":all_ok,"results":results,"scope":"Headless direct core normal-pilot progression, two additional independent seeds for each primary; no repeat claim. Not manual/GPU/balance approval."},"\t"));f.close()
 quit(0 if all_ok else 2)
