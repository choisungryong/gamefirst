extends SceneTree
var folder := ""
var checks: Dictionary={}
func _initialize() -> void:call_deferred("_test")
func poses(actor: Node3D) -> Array:
 var result: Array=[];var rig: Skeleton3D=actor.get_meta("minion19").skeleton
 for i in rig.get_bone_count():result.append(rig.get_bone_pose(i))
 return result
func equal_poses(a: Array,b: Array) -> bool:
 if a.size()!=b.size():return false
 for i in a.size():
  if not a[i].is_equal_approx(b[i]):return false
 return true
func _test() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--regression34-dir="):folder=arg.trim_prefix("--regression34-dir=")
 if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
 DirAccess.make_dir_recursive_absolute(folder)
 var view=load("res://chapter1/ChapterOne.tscn").instantiate();view.actors=load("res://chapter1/view/chapter_actors_quality34b.gd").new();root.add_child(view);view.set_process(false);view.set_physics_process(false)
 while view.run.tick<2800:view.run.step(view.full_pilot.decide())
 view.run.events.clear();view.actors.sync(view.run,0)
 var original: Dictionary=view.run.snapshot().duplicate(true)
 var target: Node3D
 for actor in view.actors.actors.values():
  if view.actors._is34(actor):
   var e: Dictionary=view.actors._entity(actor)
   if e.hp_raw>0:target=actor;break
 if target==null:push_error("No normal live walker");quit(1);return
 var e: Dictionary=view.actors._entity(target);var saved: Dictionary=e.duplicate(true);var tick: int=view.run.tick;var mode: String=view.run.mode
 var state: Dictionary=target.get_meta("minion19");var rig: Skeleton3D=state.skeleton
 checks.new_rig_65=rig.get_bone_count()==65
 checks.independent_materials=state.materials.size()==2
 e.state="move";e.hp_raw=1000;e.frozen_until=0;e.position=view.run.hero.position+Vector2(2,0);view.run.tick=50000
 view.actors._update_pose(target,Vector2.DOWN,true,false,false,view.run.tick,true)
 var walking := poses(target)
 for repeat in 20:view.actors._update_pose(target,Vector2.DOWN,true,false,false,view.run.tick,true)
 checks.repeated_sampling_stable=equal_poses(walking,poses(target))
 checks.head_scale72=rig.get_bone_pose_scale(view.actors._head34).is_equal_approx(Vector3.ONE*.72)
 view.actors._update_pose(target,Vector2.LEFT,true,false,false,view.run.tick,false)
 checks.modal_holds_pose=equal_poses(walking,poses(target))
 e.frozen_until=view.run.tick+60;view.actors.sync(view.run,.1)
 checks.freeze_holds_pose=equal_poses(walking,poses(target));e.frozen_until=0
 view.actors._update_pose(target,Vector2.DOWN,true,false,false,view.run.tick,true,false)
 var base := poses(target);view.actors._enemy_hit_until[e.id]=view.run.tick+6
 view.actors._update_pose(target,Vector2.DOWN,true,false,false,view.run.tick,true,true)
 var struck := poses(target);var upper := false;var lower := true
 for i in base.size():
  if i in view.actors._hit34_indices:upper=upper or not base[i].is_equal_approx(struck[i])
  else:lower=lower and base[i].is_equal_approx(struck[i])
 checks.hit_changes_upper=upper;checks.hit_preserves_lower=lower
 var duration: int=e.get("definition",{}).get("windup",view.run.ENEMY_DEFS[e.kind].windup)
 e.state="windup";e.state_until=view.run.tick+duration/2;e.attack_direction=Vector2.RIGHT
 view.actors._update_pose(target,e.attack_direction,false,true,false,view.run.tick,true)
 var sample: Dictionary=target.get_meta("minion19_pose")
 checks.windup_first_cycle=sample.clip=="attack_slam" and absf(float(sample.time)-view.actors.STRIKE34*.5)<.04
 var recover: int=e.get("definition",{}).get("recover",view.run.ENEMY_DEFS[e.kind].recover)
 e.state="recover";e.direction=Vector2.UP;e.state_until=view.run.tick+recover/2;target.rotation.y=PI*.5
 view.actors._demon19_attacks[e.id]={"tick":view.run.tick-recover/2,"end":e.state_until,"kind":"circle"}
 view.actors._update_pose(target,e.direction,false,false,false,view.run.tick,true)
 sample=target.get_meta("minion19_pose")
 checks.recover_first_cycle=sample.clip=="attack_slam" and float(sample.time)>=view.actors.STRIKE34 and float(sample.time)<=view.actors.SWING34
 checks.recover_paid_facing=absf(angle_difference(target.rotation.y,PI*.5))<.001
 e.hp_raw=0;e.dead_tick=view.run.tick-180
 view.actors._update_pose(target,e.direction,false,false,true,view.run.tick,true)
 sample=target.get_meta("minion19_pose");checks.death_holds_before_source_reset=sample.clip=="death" and is_equal_approx(float(sample.time),1.60)
 e.clear();e.merge(saved);view.run.tick=tick;view.run.mode=mode;view.actors.reset()
 checks.pool_restored224=view.actors._pool25_size()==224
 view.actors.sync(view.run,0)
 var families := true;var aliases: Dictionary={}
 for key in view.actors.actors:
  var actor: Node3D=view.actors.actors[key]
  if actor.get_meta("kind")=="walker":families=families and view.actors._is34(actor)
  elif actor.has_meta("minion19"):families=families and not view.actors._is34(actor)
  if aliases.has(actor.get_instance_id()):families=false
  aliases[actor.get_instance_id()]=true
 checks.recheckout_family_and_no_alias=families
 checks.pool_created224=view.actors.pool25_created==224
 checks.normal_complete_core_restored=original==view.run.snapshot()
 var passed := true
 for value in checks.values():passed=passed and bool(value)
 var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"passed":passed,"checks":checks,"scope":"Headless source34b normal2800 snapshot plus explicit reversible pose/paid/freeze/death/pool fixture. Not actual manual/whole/GPU/performance."},"\t"));f.close()
 view.audio.reset();view.queue_free()
 for i in 8:await process_frame
 quit(0 if passed else 1)
