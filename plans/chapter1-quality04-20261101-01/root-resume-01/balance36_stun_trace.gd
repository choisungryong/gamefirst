extends SceneTree
func _initialize() -> void:
 var r=load("res://chapter1/core/chapter_run_quality36.gd").new();var pilot=load("res://chapter1/core/chapter_pilot.gd").new();pilot.run=r;r.start(90131,"chapter1.skill.arc")
 var found: Dictionary={}
 while r.mode not in ["victory","defeat"] and r.tick<12000:
  r.step(pilot.decide())
  for e in r.enemies.values():
   if e.hp_raw>0 and int(e.get("stunned_until",0))-r.tick>=12:
    found={"tick":r.tick,"id":e.id,"kind":e.kind,"elite":e.elite,"remaining":int(e.stunned_until)-r.tick,"hp_raw":e.hp_raw};break
  if not found.is_empty():break
 var f=FileAccess.open("C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/balance36/stun-trace01/RESULT.json",FileAccess.WRITE);f.store_string(JSON.stringify(found,"\t"));f.close()
 print("FIRST_LIVING_STUN ",JSON.stringify(found));quit(0 if not found.is_empty() else 1)
