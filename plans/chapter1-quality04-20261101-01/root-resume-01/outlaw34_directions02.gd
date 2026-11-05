extends SceneTree
var folder := ""
var view: Node3D
var checks: Dictionary={}
var rows: Array=[]
func _initialize() -> void:call_deferred("_test")
func _test() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--directions34-dir="):folder=arg.trim_prefix("--directions34-dir=")
 if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
 DirAccess.make_dir_recursive_absolute(folder)
 view=load("res://chapter1/ChapterOne.tscn").instantiate();view.actors=load("res://chapter1/view/chapter_actors_quality34b.gd").new();root.add_child(view);view.set_process(false);view.set_physics_process(false)
 while view.run.tick<2800:view.run.step(view.full_pilot.decide())
 var normal: Dictionary=view.run.snapshot().duplicate(true)
 var saved_enemies: Dictionary=view.run.enemies;var saved_tick: int=view.run.tick;var saved_hero: Dictionary=view.run.hero.duplicate(true);var saved_zone: int=view.run.zone
 var template: Dictionary=saved_enemies.values()[0];var fixture: Dictionary={};var directions := [Vector2.RIGHT,Vector2.UP,Vector2.LEFT,Vector2.DOWN]
 view.run.zone=0;view.run.hero.position=Vector2.ZERO;view.run.tick=100000
 for index in 4:
  var e: Dictionary=template.duplicate(true);e.id=940000+index;e.kind="walker";e.elite=false;e.hp_raw=1000;e.frozen_until=0;e.position=Vector2(-4.5+float(index)*3,0);e.direction=directions[index];e.attack_direction=directions[index];e.attack_kind="circle";e.definition=view.run.ENEMY_DEFS.walker.duplicate(true);e.state="windup";e.state_until=view.run.tick+int(e.definition.windup)/2;fixture[e.id]=e
 view.run.enemies=fixture;view.run.events.clear();view.actors.reset();view.effects.reset();view.hud.root.visible=false;view.world.update_camera(Vector2.ZERO,10);view.world.sync(view.run,0)
 var camera := root.get_camera_3d();camera.position=Vector3(10,14,11);camera.look_at(Vector3(0,.6,0));camera.size=11
 var label := Label.new();label.position=Vector2(20,120);label.add_theme_font_size_override("font_size",22);root.add_child(label)
 var phases := ["windup","release","recover","death025","death060","death100"]
 var paid_seq := 7000000
 for phase in phases:
  view.run.tick=100000
  for e in fixture.values():
   e.hp_raw=1000;e.state="windup";e.state_until=view.run.tick+int(e.definition.windup)/2
   if phase in ["release","recover"]:
    e.state="recover";e.direction=e.attack_direction.orthogonal()
    var age: int=int(e.definition.recover)/2 if phase=="recover" else 0
    e.state_until=view.run.tick+int(e.definition.recover)-age
    view.actors.consume([{"seq":paid_seq,"type":"enemy_attack","target_id":e.id,"tick":view.run.tick-age,"attack_kind":"circle","kind":"walker","position":e.position}]);paid_seq+=1
   elif phase.begins_with("death"):
    e.hp_raw=0;e.state="dead"
    var age: int=15 if phase=="death025" else (36 if phase=="death060" else 60)
    e.dead_tick=view.run.tick-age
   else:e.direction=e.attack_direction
  view.actors.sync(view.run,0);view.actors.hero.visible=false;view.actors.owner_mark.visible=false
  var all_family: bool= view.actors.actors.size()==4;var facing := true;var expected := true;var samples: Array=[]
  for actor in view.actors.actors.values():
   var e: Dictionary=view.actors._entity(actor)
   actor.rotation.y=atan2(e.attack_direction.x,e.attack_direction.y)
   var state: Dictionary=actor.get_meta("minion19")
   var sample: Dictionary=actor.get_meta("minion19_pose")
   all_family=all_family and view.actors._is34(actor)
   facing=facing and absf(angle_difference(actor.rotation.y,atan2(e.attack_direction.x,e.attack_direction.y)))<.001
   if phase.begins_with("death"):expected=expected and sample.clip=="death" and float(sample.time)<=1.60
   elif phase=="windup":expected=expected and sample.clip=="attack_slam" and absf(float(sample.time)-view.actors.STRIKE34*.5)<.04
   elif phase=="release":expected=expected and sample.clip=="attack_slam" and absf(float(sample.time)-view.actors.STRIKE34)<.04
   else:expected=expected and sample.clip=="attack_slam" and float(sample.time)>view.actors.STRIKE34 and float(sample.time)<view.actors.SWING34
   samples.append({"id":e.id,"direction":e.attack_direction,"pose":sample,"alpha":state.materials[0].albedo_color.a})
  checks[phase+"_four_new_walkers"]=all_family;checks[phase+"_expected_authored_phase"]=expected
  label.text="QA four directions · "+phase+" · copied walker fixture, not earned combat"
  await RenderingServer.frame_post_draw
  var img := root.get_texture().get_image();img.save_png(folder.path_join(phase+".png"));rows.append({"phase":phase,"samples":samples,"image":[img.get_width(),img.get_height()]})
 view.run.enemies=saved_enemies;view.run.tick=saved_tick;view.run.hero=saved_hero;view.run.zone=saved_zone;view.actors.reset()
 checks.normal_core_restored=normal==view.run.snapshot()
 var passed := true
 for value in checks.values():passed=passed and bool(value)
 var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"passed":passed,"checks":checks,"rows":rows,"scope":"Four cardinal walker directions, mid-windup/release/mid-recover/death.25-.60-1.00s source GPU copied fixture, normal2800 core restored. Direction intentionally snapped for visual comparison. Not actual package/manual/whole/performance."},"\t"));f.close()
 view.audio.reset();view.queue_free()
 for i in 8:await process_frame
 quit(0 if passed else 1)
