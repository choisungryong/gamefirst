extends SceneTree
var folder := ""
var variant := "26"
var view: Node3D
var rows: Array=[]
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--flame33-dir="):folder=arg.trim_prefix("--flame33-dir=")
  if arg.begins_with("--flame33-fx="):variant=arg.trim_prefix("--flame33-fx=")
 if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
 DirAccess.make_dir_recursive_absolute(folder)
 view=load("res://chapter1/ChapterOne.tscn").instantiate();view.effects=load("res://chapter1/view/chapter_elements_quality%s.gd"%variant).new();root.add_child(view);view.set_process(false);view.set_physics_process(false)
 while view.run.tick<6077:view.run.step(view.full_pilot.decide())
 view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear();view.world.update_camera(view.run.hero.position,10);view.hud.sync(view.run,3)
 for frame in 121:
  if frame>0:view.run.events.clear();view.run.step(view.full_pilot.decide());view._consume_events()
  view.world.update_camera(view.run.hero.position,1.0/60);view.world.sync(view.run,1.0/60);view.actors.sync(view.run,1.0/60);view.effects.sync(view.run,1.0/60);view.hud.sync(view.run,1.0/60)
  var plume_data: Array=[]
  for i in view.effects.plumes.multimesh.visible_instance_count:
   var t: Transform3D=view.effects.plumes.multimesh.get_instance_transform(i)
   plume_data.append({"center_y":t.origin.y,"height":t.basis.y.length()*2.3})
  rows.append({"frame":frame,"tick":view.run.tick,"core_sha":JSON.stringify(view.run.snapshot()).sha256_text(),"plumes":plume_data})
  if frame in [0,20,37,49,70,110]:
   await RenderingServer.frame_post_draw
   root.get_texture().get_image().save_png(folder.path_join("frame-%03d.png"%frame))
 var reference=load("res://chapter1/core/chapter_run_quality16.gd").new();var policy=load("res://chapter1/core/chapter_pilot.gd").new();policy.run=reference;var started: bool=reference.start(view.seed_,view.primary)
 while reference.tick<view.run.tick:reference.step(policy.decide())
 var same: bool=started and reference.snapshot()==view.run.snapshot()
 var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"rows":rows,"same_complete_core":same,"end_tick":view.run.tick,"scope":"Normal earned fire6077 checkpoint,121 renderer samples across120 normal-policy core steps; six selected PNGs. Source FX26/33 comparison, not package/manual/performance/hearing."},"\t"));f.close()
 view.audio.reset();view.queue_free()
 for i in 6:await process_frame
 quit(0 if same else 1)
