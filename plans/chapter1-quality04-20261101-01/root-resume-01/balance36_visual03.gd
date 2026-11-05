extends SceneTree
var checks: Array=[]
func check(ok: bool,label: String) -> void:checks.append({"ok":ok,"label":label})
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
 var view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
 view.set_process(false);view.set_physics_process(false)
 while view.run.tick<708:view.run.step(view.full_pilot.decide())
 var target: int=-1
 for step_ in 2:
  view.run.step(view.full_pilot.decide())
  for id_ in view.run.enemies:
   var e: Dictionary=view.run.enemies[id_]
   if e.hp_raw>0 and int(e.get("stunned_until",0))-view.run.tick>=12:target=id_;break
  if target>0:break
 check(target>0,"natural living stunned target")
 if target<0:quit(1);return
 view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,0)
 var frozen: Dictionary=view.run.snapshot().duplicate(true)
 var reference=load("res://chapter1/core/chapter_run_quality36.gd").new();var pilot=load("res://chapter1/core/chapter_pilot.gd").new();pilot.run=reference;reference.start(90131,"chapter1.skill.arc")
 while reference.tick<view.run.tick:reference.step(pilot.decide())
 check(reference.snapshot()==frozen,"independent normal core same")
 var actor: Node3D=null
 for key in view.actors.actors:
  var candidate: Node3D=view.actors.actors[key]
  if view.actors._entity(candidate).get("id",-1)==target:actor=candidate;break
 check(actor!=null,"target actor found")
 var rig: Skeleton3D=actor.get_meta("minion19").skeleton
 var poses: Array=[]
 for index in rig.get_bone_count():poses.append(rig.get_bone_pose(index))
 for repeat_ in 4:view.actors._update_pose(actor,Vector2.RIGHT,true,true,false,view.run.tick,true,true)
 var same: bool=true
 for index in rig.get_bone_count():same=same and poses[index]==rig.get_bone_pose(index)
 check(same,"shock holds displayed whole rig")
 check(view.effects.stun36_visible>0 and view.effects.stun36_visible<=48,"actual state cues bounded")
 check(view.effects._stun36_sparks.multimesh.visible_instance_count==view.effects.stun36_visible*3,"three cues per living stun")
 DirAccess.make_dir_recursive_absolute("res://shots36")
 for i in 4:await process_frame
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png("res://shots36/stun-active.png")
 check(view.run.snapshot()==frozen,"render does not mutate core")
 var until_tick: int=view.run.enemies[target].stunned_until
 while view.run.tick<=until_tick:
  view.run.step(view.full_pilot.decide());reference.step(pilot.decide())
 view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,0)
 check(view.run.snapshot()==reference.snapshot(),"normal core same after expiry")
 for i in 4:await process_frame
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png("res://shots36/stun-ended.png")
 view.effects.reset();check(view.effects._stun36_sparks.multimesh.visible_instance_count==0,"reset clears cues")
 view.audio.reset()
 var passed: bool=true
 for c in checks:passed=passed and c.ok
 var f=FileAccess.open("res://visual36-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"passed":passed,"checks":checks,"target":target,"tick":view.run.tick,"scope":"Source36 actual normal arc first living ranged-stun at709 checkpoint, static GPU active/expiry screens, whole-rig hold. Not live whole/manual/final performance."},"\t"));f.close()
 quit(0 if passed else 2)
