extends SceneTree
var folder := ""
var view: Node3D
var target := -1
var checkpoint := -1
var ready_ := false
var ending := false
var seen: Dictionary={}
var states: Array=[]
var paid := false
func _initialize() -> void:call_deferred("_boot")
func capture(name_: String) -> void:
 seen[name_]=true
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png(folder.path_join(name_+".png"))
func _boot() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--role32-dir="):folder=arg.trim_prefix("--role32-dir=")
 if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
 DirAccess.make_dir_recursive_absolute(folder)
 view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
 var limit := 0
 while target<0 and view.run.tick<20000 and limit<60000:
  limit+=1
  for e in view.run.enemies.values():
   if bool(e.elite) and e.hp_raw>0 and view.run.zone<2 and e.state=="windup":
    var duration: int=e.get("definition",{}).get("windup",view.run.ENEMY_DEFS[e.kind].windup)
    if int(e.state_until)-view.run.tick<=roundi(duration*.35):target=e.id;break
  if target<0:view.run.step(view.full_pilot.decide())
 if target<0:push_error("No normal earned elite windup found");quit(1);return
 checkpoint=view.run.tick
 view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear();view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
 var e: Dictionary=view.run.enemies[target];states.append({"phase":"checkpoint","tick":view.run.tick,"target":e.duplicate(true),"zone":view.run.zone})
 await capture("windup");ready_=true
func _process(_delta: float) -> bool:
 if not ready_ or ending:return false
 var e: Dictionary=view.run.enemies.get(target,{})
 if view.actors._demon19_attacks.has(target):paid=true
 if not e.is_empty():
  if e.state=="recover" and not seen.has("release"):
   states.append({"phase":"release","tick":view.run.tick,"target":e.duplicate(true)});capture("release")
  if e.state=="recover" and view.actors._demon19_attacks.has(target) and not seen.has("recover"):
   var record: Dictionary=view.actors._demon19_attacks[target]
   var duration: int=e.get("definition",{}).get("recover",view.run.ENEMY_DEFS[e.kind].recover)
   if view.run.tick-int(record.tick)>=maxi(2,duration/3):
    states.append({"phase":"recover","tick":view.run.tick,"target":e.duplicate(true)});capture("recover")
 if view.run.tick>=checkpoint+300:
  ending=true;view.set_process(false);view.set_physics_process(false);call_deferred("_finish")
 return false
func _finish() -> void:
 var reference=load("res://chapter1/core/chapter_run_quality16.gd").new();var policy=load("res://chapter1/core/chapter_pilot.gd").new();policy.run=reference
 var started: bool=reference.start(view.seed_,view.primary)
 while reference.tick<view.run.tick:reference.step(policy.decide())
 var same: bool=started and reference.snapshot()==view.run.snapshot()
 await capture("end")
 var passed: bool=same and paid and seen.has("windup") and seen.has("release") and seen.has("recover") and view.actors.get_script().resource_path=="res://chapter1/view/chapter_actors_quality32b.gd" and view._profile_off
 var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"passed":passed,"complete_core_equal":same,"paid_attack_seen":paid,"captures":seen,"states":states,"start_tick":checkpoint,"end_tick":view.run.tick,"actor_script":view.actors.get_script().resource_path,"motion32_samples":view.actors.motion32_samples,"scope":"Actual32 EXE/PCK normally earned first nonfinal elite mid-windup checkpoint, then original live controllers300ticks, independent complete core equality. No injected enemy/state/combat rule. Not whole/manual/hearing/formal performance."},"\t"));f.close()
 view.audio.reset();view.queue_free()
 for i in 6:await process_frame
 quit(0 if passed else 1)
