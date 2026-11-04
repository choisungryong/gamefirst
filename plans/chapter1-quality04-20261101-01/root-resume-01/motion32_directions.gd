extends SceneTree
var folder := ""
var view: Node3D
var checks: Dictionary={}
var rows: Array=[]
func _initialize() -> void:call_deferred("_test")
func poses(actor: Node3D) -> Array:
 var rig: Skeleton3D=actor.get_meta("minion19").skeleton
 var out: Array=[]
 for i in rig.get_bone_count():out.append(rig.get_bone_pose(i))
 return out
func shot(name_: String) -> void:
 if DisplayServer.get_name()=="headless":return
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png(folder.path_join(name_+".png"))
func _test() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--directions-dir="):folder=arg.trim_prefix("--directions-dir=")
 if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
 DirAccess.make_dir_recursive_absolute(folder)
 view=load("res://chapter1/ChapterOne.tscn").instantiate();view.actors=load("res://chapter1/view/chapter_actors_quality32b.gd").new();root.add_child(view);view.set_process(false);view.set_physics_process(false)
 while view.run.tick<2800:view.run.step(view.full_pilot.decide())
 var normal: Dictionary=view.run.snapshot().duplicate(true)
 var saved_enemies: Dictionary=view.run.enemies;var saved_hero: Dictionary=view.run.hero.duplicate(true);var saved_tick: int=view.run.tick;var saved_zone: int=view.run.zone;var saved_mode: String=view.run.mode
 var template: Dictionary=saved_enemies.values()[0]
 var fixture: Dictionary={};var roles := ["walker","ranged","charger","elite"];var directions := [Vector2.RIGHT,Vector2.UP,Vector2.LEFT,Vector2.DOWN]
 view.run.zone=0;view.run.tick=100000;view.run.hero.position=Vector2.ZERO
 for role in 4:
  for direction in 4:
   var e: Dictionary=template.duplicate(true);e.id=910000+role*4+direction;e.kind=roles[role];e.elite=e.kind=="elite";e.hp_raw=1000;e.frozen_until=0;e.position=Vector2(-6+direction*4,-6+role*4);e.direction=directions[direction];e.attack_direction=directions[direction];e.attack_kind="fan" if e.kind=="ranged" else "line";e.definition=view.run.ENEMY_DEFS[e.kind].duplicate(true);e.state="windup";e.state_until=view.run.tick+roundi(float(e.definition.windup)*.35);fixture[e.id]=e
 view.run.enemies=fixture;view.actors.reset();view.effects.reset();view.run.events.clear();view.hud.root.visible=false
 view.actors.motion32_enabled=false;view.actors.sync(view.run,0);view.actors.hero.visible=false
 for actor in view.actors.actors.values():actor.rotation.y=atan2(view.actors._entity(actor).attack_direction.x,view.actors._entity(actor).attack_direction.y)
 for name_ in ["projectiles","shards","impacts","plumes","telegraph","telegraph_fill","beams","arc_surface","ice_batch","ice_fragment_batch","ward_rings","ward_fill","contact_batch","shadows"]:
  var node: GeometryInstance3D=view.effects.get(name_)
  if node:node.visible=false
 var camera := root.get_camera_3d();camera.position=Vector3(14,25,19);camera.look_at(Vector3(0,.5,0));camera.size=22
 var label := Label.new();label.position=Vector2(20,120);label.add_theme_font_size_override("font_size",22);root.add_child(label)
 var seq := 2000000
 for phase in ["windup","recover"]:
  if phase=="recover":
   view.run.tick=100100
   for e in fixture.values():
    var half := int(e.definition.recover)/2
    e.state="recover";e.direction=e.attack_direction.orthogonal();e.state_until=view.run.tick+half
    view.actors.consume([{"seq":seq,"type":"enemy_attack","target_id":e.id,"tick":view.run.tick-half,"attack_kind":e.attack_kind,"kind":e.kind,"position":e.position}]);seq+=1
  view.actors.motion32_enabled=false;view.actors.sync(view.run,0)
  var baseline: Dictionary={};var roots: Dictionary={}
  for actor in view.actors.actors.values():baseline[actor.name]=poses(actor);roots[actor.name]=actor.transform
  label.text="QA four roles x four directions · "+phase+" BEFORE (copied fixture)"
  await shot(phase+"-before")
  var core: Dictionary=view.run.snapshot().duplicate(true)
  view.actors.motion32_enabled=true;view.actors.sync(view.run,0)
  var stable := true;var lower := true;var changed := 0;var staff := true;var held: Dictionary={}
  for actor in view.actors.actors.values():
   var rig: Skeleton3D=actor.get_meta("minion19").skeleton
   var current := poses(actor);held[actor.name]=current
   var has_change := false
   for i in rig.get_bone_count():
    if i in view.actors._indices32:has_change=has_change or not current[i].is_equal_approx(baseline[actor.name][i])
    else:lower=lower and current[i].is_equal_approx(baseline[actor.name][i])
   if has_change:changed+=1
   var e: Dictionary=view.actors._entity(actor)
   for repeat in 20:view.actors._update_pose(actor,e.attack_direction,false,e.state=="windup",false,view.run.tick,true)
   var repeated := poses(actor)
   for i in current.size():stable=stable and current[i].is_equal_approx(repeated[i])
   var state: Dictionary=actor.get_meta("minion19")
   if state.has("staff21"):staff=staff and state.staff21.position.is_equal_approx(actor.to_local(view.actors._bone_point(rig,"Hand.R")))
  label.text="QA four roles x four directions · "+phase+" AFTER (copied fixture)"
  await shot(phase+"-after")
  checks[phase+"_16_upper_changed"]=changed==16;checks[phase+"_lower_body_preserved"]=lower;checks[phase+"_no_pose_accumulation"]=stable;checks[phase+"_staff_follows_hand"]=staff;checks[phase+"_core_unchanged"]=core==view.run.snapshot()
  view.run.mode="paused";view.actors.sync(view.run,.1)
  var modal := true
  for actor in view.actors.actors.values():
   var current := poses(actor)
   for i in current.size():modal=modal and current[i].is_equal_approx(held[actor.name][i])
  checks[phase+"_modal_holds_pose"]=modal
  view.run.mode="playing"
  for e in fixture.values():e.frozen_until=view.run.tick+60
  view.actors.sync(view.run,.1)
  var frozen := true
  for actor in view.actors.actors.values():
   var current := poses(actor)
   for i in current.size():frozen=frozen and current[i].is_equal_approx(held[actor.name][i])
  checks[phase+"_freeze_holds_pose"]=frozen
  for e in fixture.values():e.frozen_until=0
 view.run.enemies=saved_enemies;view.run.hero=saved_hero;view.run.tick=saved_tick;view.run.zone=saved_zone;view.run.mode=saved_mode;view.actors.reset()
 checks.normal_core_restored=normal==view.run.snapshot();checks.pool_cap=view.actors._pool25_size()<=224 and view.actors.pool25_created==224
 var passed := true
 for value in checks.values():passed=passed and bool(value)
 var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"passed":passed,"checks":checks,"scope":"Source32b copied four roles x four cardinal directions, mid-windup and mid-recover; no core step in fixture; normal2800tick restored. Not normal earned combat/manual/package/performance."},"\t"));f.close()
 view.audio.reset();view.queue_free()
 for i in 6:await process_frame
 quit(0 if passed else 1)
