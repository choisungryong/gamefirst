extends SceneTree
var checks: Array=[]
func check(ok: bool,label: String) -> void:checks.append({"ok":ok,"label":label})
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
 var view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
 view.set_process(false);view.set_physics_process(false);DisplayServer.window_set_size(Vector2i(1920,1080))
 DirAccess.make_dir_recursive_absolute("res://crowd36-shots")
 var reference=load("res://chapter1/core/chapter_run_quality36.gd").new();var pilot=load("res://chapter1/core/chapter_pilot.gd").new();pilot.run=reference;reference.start(90131,"chapter1.skill.arc")
 var records: Array=[]
 for primary in ["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"]:
  view.run.start(90131,primary)
  reference.start(90131,primary)
  while view.run.tick<15880:view.run.step(view.full_pilot.decide())
  while reference.tick<view.run.tick:reference.step(pilot.decide())
  view.actors.reset();view.effects.reset();view.hud.reset();view.world.update_camera(view.run.hero.position,10)
  var peak: Dictionary={"arcs":0,"shards":0,"stun":0,"alive":0,"plumes":0}
  var all_same: bool=true;var caps: bool=true
  for frame in 300:
   view.run.step(view.full_pilot.decide());reference.step(pilot.decide())
   view.effects.consume(view.run.events);view.actors.consume(view.run.events)
   view.world.update_camera(view.run.hero.position,1.0/60.0);view.world.sync(view.run,1.0/60.0);view.actors.sync(view.run,1.0/60.0);view.effects.sync(view.run,1.0/60.0);view.hud.sync(view.run,1.0/60.0)
   if reference.snapshot()!=view.run.snapshot() and all_same:
    var differing: Array=[]
    for key in reference.snapshot():
     if reference.snapshot()[key]!=view.run.snapshot().get(key):differing.append(key)
    print("FIRST_CORE_MISMATCH ",JSON.stringify({"primary":primary,"tick":view.run.tick,"keys":differing}))
   all_same=all_same and reference.snapshot()==view.run.snapshot()
   peak.arcs=maxi(peak.arcs,view.effects.arc_links.size());peak.shards=maxi(peak.shards,view.effects.ice_fragment_batch.multimesh.visible_instance_count);peak.stun=maxi(peak.stun,view.effects.stun36_visible);peak.alive=maxi(peak.alive,view.run.alive_count());peak.plumes=maxi(peak.plumes,view.effects.plumes.multimesh.visible_instance_count)
   caps=caps and peak.arcs<=64 and peak.shards<=128 and peak.stun<=48 and view.actors.pool25_created<=224
   await process_frame
   if frame in [149,209,299]:
    await RenderingServer.frame_post_draw
    root.get_texture().get_image().save_png("res://crowd36-shots/%s-%d.png"%[primary.get_slice(".",2),frame-119])
  check(all_same,"all300frame cores same "+primary);check(caps,"effect and pool caps "+primary)
  records.append({"primary":primary,"first_tick":15881,"last_tick":view.run.tick,"frames":300,"warmup_frames":120,"captured_frames":[30,90,180],"peaks":peak,"level":view.run.growth.snapshot().level,"evolved":view.run.growth.snapshot().evolved})
 view.audio.reset();var passed: bool=true
 for c in checks:passed=passed and c.ok
 var f=FileAccess.open("res://crowd36-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"passed":passed,"checks":checks,"records":records,"scope":"Three normal earned36 primary builds,16000tick onward3simsec after2simsec presenter warmup,300 rendered iterations each. Offline observer-driven frames, not realtime performance/manual/audio."},"\t"));f.close();quit(0 if passed else 2)
