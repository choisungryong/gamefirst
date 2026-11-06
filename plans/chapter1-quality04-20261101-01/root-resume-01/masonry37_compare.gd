extends SceneTree
var folder := ""
var variant := "31d"
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--masonry37-dir="):folder=arg.trim_prefix("--masonry37-dir=")
  if arg.begins_with("--masonry37-world="):variant=arg.trim_prefix("--masonry37-world=")
 if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
 DirAccess.make_dir_recursive_absolute(folder)
 var view=load("res://chapter1/ChapterOne.tscn").instantiate();view.world=load("res://chapter1/view/chapter_world_quality%s.gd"%variant).new();root.add_child(view)
 view.set_process(false);view.set_physics_process(false)
 while view.run.tick<9000:view.run.step(view.full_pilot.decide())
 view.actors.reset();view.effects.reset();view.hud.reset();view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
 var frozen: Dictionary=view.run.snapshot().duplicate(true)
 var cameras: Array=[Vector2(0,-14),Vector2(48,-14),Vector2(96,-14),view.run.hero.position]
 var records: Array=[];var same: bool=true
 for index in cameras.size():
  view.world.update_camera(cameras[index],10)
  for frame in 4:await process_frame
  await RenderingServer.frame_post_draw
  var image=root.get_texture().get_image();image.save_png(folder.path_join("view-%d.png"%index))
  same=same and frozen==view.run.snapshot();records.append({"view":index,"inspection_camera":index<3,"target":cameras[index],"image":[image.get_width(),image.get_height()]})
 var batches: Array=[]
 for name_ in ["RearMasonry22","RearArches22"]:
  var node: MultiMeshInstance3D=view.world.root.get_node(NodePath(name_));batches.append({"name":name_,"instances":node.multimesh.instance_count,"surfaces":node.multimesh.mesh.get_surface_count(),"aabb":str(node.multimesh.mesh.get_aabb())})
 var file=FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);file.store_string(JSON.stringify({"world":variant,"same_core_after_views":same,"snapshot":frozen,"anchors":view.world.masonry22,"batches":batches,"records":records,"scope":"Before31d vs isolated37, same earned normal arc9000 state. Three explicit rear inspection cameras and one original hero camera. Not normal camera walk/manual/performance."},"\t"));file.close();file=null
 view.audio.reset();view.queue_free()
 for frame in 4:await process_frame
 view=null;quit(0 if same else 2)
