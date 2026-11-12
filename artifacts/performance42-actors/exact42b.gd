extends SceneTree
const A=preload("res://chapter1/view/chapter_actors_quality36.gd")
const B=preload("res://chapter1/view/chapter_actors_quality42b.gd")
const V=preload("res://chapter1/view/chapter_actors_quality42_verify.gd")
class Owner extends Node3D:
 var run: RefCounted
class Run extends RefCounted:
 var mode="playing"
 var hero={"position":Vector2.ZERO}
 var ENEMY_DEFS={"walker":{"windup":30,"recover":30}}
var owners=[]
var controllers=[]
var actors=[]
var comparisons=0
func _initialize():call_deferred("go")
func go():
 for script in [A,B]:
  var o=Owner.new();o.run=Run.new();root.add_child(o);owners.append(o)
  var c=script.new();c.view=o;c._render_delta=1.0/60.0;controllers.append(c)
  var actor=Node3D.new();o.add_child(actor);actor.set_meta("entity_key","1:1");actors.append(actor)
  var model=c.OUTLAW34.instantiate();actor.add_child(model)
  var rig=model.find_child("Skeleton3D",true,false)
  var player=model.find_child("AnimationPlayer",true,false);player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
  var materials:Array[StandardMaterial3D]=[];c._materials34(model,materials)
  actor.set_meta("minion19",{"family34":true,"model":model,"player":player,"skeleton":rig,"materials":materials,"fade":1.0,"death_age":0.0,"clip":"","bucket":-1})
  c._head34=rig.find_bone("ORG-head")
  for name_ in c.HIT34:c._hit34_indices.append(rig.find_bone(name_))
  for sample in 13:
   player.play("hit",0);player.seek(float(sample)/12.0*(46.0/60.0),true);player.advance(0)
   var poses:Array[Transform3D]=[]
   for index in c._hit34_indices:poses.append(rig.get_bone_pose(index))
   c._hit34_frames.append(poses)
  player.play("idle",0);player.seek(0,true);player.advance(0)
 for mode in ["playing","paused","choice","inventory","equipment"]:
  for state in ["idle","move","windup","recover","dead","stunned","frozen"]:
   for far in [false,true]:
    for id_ in [1,9,31]:
     for generation in [1,2]:
      for step in 20:
       var tick=120+step
       var e={"id":id_,"generation":generation,"kind":"walker","hp_raw":0 if state=="dead" else 100,"position":Vector2(12,12) if far else Vector2.ONE,"state":state,"state_until":150,"dead_tick":120,"attack_direction":Vector2.RIGHT,"stunned_until":200 if state=="stunned" else 0}
       for i in 2:
        owners[i].run.mode=mode
        controllers[i]._entities["1:1"]=e.duplicate(true)
        controllers[i]._demon19_attacks[id_]={"tick":120,"end":150}
        controllers[i]._enemy_hit_until[id_]=132
        actors[i].set_meta("motion_sample",{"phase":float(step)/20})
        controllers[i]._update_pose(actors[i],Vector2.UP,state=="move",false,state=="dead",tick,mode=="playing",step%3==0)
       var dif=V.differences(V.snapshot(actors[0]),V.snapshot(actors[1]));comparisons+=1
       if not dif.is_empty():
        print("EXACT_FAIL ",JSON.stringify({"mode":mode,"state":state,"far":far,"id":id_,"generation":generation,"step":step,"differences":dif,"comparisons":comparisons}));quit(2);return
 print("EXACT_PASS comparisons=",comparisons)
 for o in owners:o.queue_free()
 for i in 3:await process_frame
 quit()
