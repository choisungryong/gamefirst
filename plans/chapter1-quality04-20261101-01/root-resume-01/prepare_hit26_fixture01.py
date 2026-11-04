from pathlib import Path
h=Path('plans/chapter1-quality04-20261101-01/root-resume-01')
s='''extends "res://chapter1/chapter_one_view.gd"
var checks: Dictionary={}
func _init() -> void:
 super._init();actors=preload("res://chapter1/view/chapter_actors_quality26.gd").new()
func _poses(rig: Skeleton3D) -> Array:
 var result: Array=[]
 for i in rig.get_bone_count():result.append(rig.get_bone_pose(i))
 return result
func _ready() -> void:
 super._ready();set_process(false);set_physics_process(false)
 var baseline: Dictionary=run.snapshot().duplicate(true)
 var original: Dictionary=run.enemies
 var saved_tick: int=run.tick
 var saved_mode: String=run.mode
 run.tick=100
 var seq := 900000
 checks.cached13poses=actors._hit26_frames.size()==13 and actors._hit26_indices.size()==9
 for role in ["walker","ranged","charger","elite"]:
  var e: Dictionary=original.values()[0].duplicate(true)
  e.kind=role;e.elite=role=="elite";e.hp_raw=1000;e.state="move";e.frozen_until=0;e.direction=Vector2.RIGHT;e.attack_direction=Vector2.RIGHT;e.position=run.hero.position+Vector2(2,-2);e.attack_kind="fan" if role=="ranged" else "line"
  run.enemies={e.id:e};actors.reset();actors.sync(run,.016)
  var actor: Node3D=actors.actors.values()[0];var rig: Skeleton3D=actor.get_meta("minion19").skeleton
  var base: Array=_poses(rig)
  actors.consume([{"seq":seq,"type":"hit","target_id":e.id,"tick":run.tick-6,"position":e.position}]);seq+=1;actors.sync(run,.016)
  var hit_pose: Array=_poses(rig);var changed := 0;var lower_same := true
  for i in base.size():
   if i in actors._hit26_indices:
    if not base[i].is_equal_approx(hit_pose[i]):changed+=1
   elif not base[i].is_equal_approx(hit_pose[i]):lower_same=false
  checks[role+"_upper_changes"]=changed>0 and actor.has_meta("hit26_base")
  checks[role+"_lower_unchanged"]=lower_same
  e.frozen_until=run.tick+60;actors.sync(run,.25)
  checks[role+"_freeze_holds_complete_pose"]=hit_pose==_poses(rig)
  e.frozen_until=0
  for modal in ["paused","choice","inventory","equipment"]:
   run.mode=modal;actors.sync(run,.25);checks[role+"_"+modal]=hit_pose==_poses(rig)
  run.mode="playing";e.state="windup";e.state_until=run.tick+40;actors.sync(run,.016)
  checks[role+"_attack_priority"]=not actor.has_meta("hit26_base") and actor.get_meta("minion19_pose").clip.begins_with("windup_")
  e.state="move";run.tick+=20;actors.sync(run,.016)
  checks[role+"_expired_restored"]=not actor.has_meta("hit26_base")
  actors.reset();var recycled: Node3D=actors._create(role)
  checks[role+"_reuse_no_hit_metadata"]=not recycled.has_meta("hit26_base") and not recycled.has_meta("hit26_weight")
  add_child(recycled);recycled.queue_free()
 run.tick=saved_tick;run.mode=saved_mode;run.enemies=original;actors.reset()
 checks.complete_core_restored=baseline==run.snapshot()
 var file := FileAccess.open("res://hit26-fixture.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"checks":checks,"blends":actors.hit26_blends,"scope":"Headless presenter fixture: copied roles/controlled hit age then full original core restored. Not visual/normal/manual/performance proof."},"\\t"));file.close()
 audio.reset()
 for i in 4:await get_tree().process_frame
 var failed := false
 for value in checks.values():if not value:failed=true
 get_tree().quit(1 if failed else 0)
'''
(h/'hit26_fixture.gd').write_text(s,encoding='utf-8')
s=(h/'run_pool25_fixed_fixture01.py').read_text(encoding='utf-8').replace('pool25/fixed-fixture01','hit26/fixture01').replace('chapter1-pool25-fixed-fixture01','chapter1-hit26-fixture01').replace("old=Path(read(B/'full24/build/closure.json')['stage']);pins=read(B/'full24/build/staging-manifest.json')","old=Path(read(B/'full25b/build/closure.json')['stage']);pins=read(B/'full25b/build/staging-manifest.json')").replace('chapter_actors_quality25b.gd','chapter_actors_quality26.gd').replace('pool25_fixed_extended.gd','hit26_fixture.gd').replace("('gpu',['res://Compare.tscn'","('headless',['--headless','res://Compare.tscn'").replace('skin24-fixture.json','hit26-fixture.json').replace("read(B/'full24/FINAL-SOURCE-FREEZE.json')","read(B/'full25b/FINAL-SOURCE-FREEZE.json')")
(h/'run_hit26_fixture01.py').write_text(s,encoding='utf-8')
