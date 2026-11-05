extends SceneTree
const Run=preload("res://chapter1/core/chapter_run_quality36.gd")
var checks: Array=[]
func check(ok: bool,label: String) -> void:checks.append({"ok":ok,"label":label})
func sandbox() -> RefCounted:
 var r=Run.new();check(r.start(90131,"chapter1.skill.arc"),"start")
 r.enemies.clear();r._enemy_sequence=0;r.events.clear();r._next_spawn=1000000;r.tick=100
 return r
func context(r: RefCounted,skill: String) -> Dictionary:
 var fx: Dictionary={}
 for definition in r._catalog.snapshot().skills:
  if definition.id==skill:fx=definition.ranks[0].duplicate(true)
 fx.damage_raw=1;fx.death_burst=0;fx.shatter_count=0;fx.hit_budget=8
 return {"uid":100,"skill_id":skill,"effects":fx,"remaining_hits":8,"hit_ids":[],"evolved":false}
func _initialize() -> void:
 var r=sandbox();r._spawn("walker",Vector2(4,0));var e: Dictionary=r.enemies[1]
 e.hp_raw=1000000;e.max_hp_raw=1000000
 var c: Dictionary=context(r,"chapter1.skill.arc");r._damage_enemy(1,c,0)
 check(e.stunned_until==118 and e.shock_ready_tick==220,"normal .3sec stun /2sec immunity")
 check(e.frozen_until==0 and e.freeze_stacks==0,"shock is not cold")
 var hp: int=e.hp_raw;r._damage_enemy(1,c,0);check(e.hp_raw==hp,"chain duplicate cannot rehit")
 r.tick=110;r._damage_enemy(1,context(r,"chapter1.skill.arc"),0);check(e.stunned_until==118 and e.shock_ready_tick==220,"immune hit cannot extend control")
 e.state="windup";e.state_until=120;e.telegraph={"remaining_ticks":10}
 var pos: Vector2=e.position
 for t in range(110,118):r.tick=t;r._step_enemies()
 check(e.position==pos and e.state_until==128 and r.metrics.enemy_attacks==0,"stun preserves paid windup and anchors position")
 r.tick=118;r._step_enemies();check(e.state=="windup" and r.metrics.enemy_attacks==0,"no surprise release on stun end")
 r.tick=220;r._damage_enemy(1,context(r,"chapter1.skill.arc"),0);check(e.stunned_until==238,"stun reapplies after immunity")
 r._spawn("elite",Vector2(7,0));var elite: Dictionary=r.enemies[2];elite.hp_raw=1000000
 r._damage_enemy(2,context(r,"chapter1.skill.arc"),0)
 check(elite.stunned_until==226 and elite.shock_ready_tick==400,"elite .1sec stun /3sec immunity")
 r._spawn("walker",Vector2(9,0));var third: Dictionary=r.enemies[3];third.hp_raw=1000000
 r._damage_enemy(3,context(r,"chapter1.skill.arc"),1);check(not third.has("stunned_until"),"death explosion does not stun")
 r._damage_enemy(3,context(r,"chapter1.skill.ember"),0);check(not third.has("stunned_until"),"fire does not apply shock")
 var cold: Dictionary=context(r,"chapter1.skill.frost");cold.effects.freeze_stacks=1
 r._damage_enemy(3,cold,0);check(third.frozen_until==295 and third.slow_until==320,"cold freeze and slow retained")
 var frozen: int=third.frozen_until;r._damage_enemy(3,context(r,"chapter1.skill.arc"),0);check(third.frozen_until==frozen,"shock does not rewrite cold clock")
 var catalog=load("res://chapter1/core/growth_catalog.gd").new();check(catalog.load_file("res://chapter1/data/growth_quality36.json"),"growth36 validates")
 var skills: Array=catalog.snapshot().skills
 check(skills[0].ranks[1].radius_cm>0 and skills[0].ranks[2].death_burst==1,"fire propagation grows before evolution")
 check(skills[1].ranks[1].freeze_stacks==4 and skills[1].ranks[2].shatter_count==2 and skills[1].evolution.shatter_count==6,"cold control to shatter progression")
 check(skills[2].ranks[2].branches==2 and skills[2].ranks[3].branches==3 and skills[2].evolution.chain_targets==8,"arc branching progression")
 var ok: bool=true
 for row in checks:ok=ok and row.ok
 var f=FileAccess.open("res://balance36-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"passed":ok,"checks":checks,"scope":"Headless rule fixtures only. No balance/visual/manual approval."},"\t"));f.close()
 quit(0 if ok else 1)
