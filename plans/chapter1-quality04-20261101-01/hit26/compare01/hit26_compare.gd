extends SceneTree
var view: Node3D
var output := ""
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--compare-output="):output=arg.trim_prefix("--compare-output=")
 assert(not output.is_empty() and not DirAccess.dir_exists_absolute(output));DirAccess.make_dir_recursive_absolute(output)
 view=load("res://chapter1/ChapterOne.tscn").instantiate();view.actors=load("res://chapter1/view/chapter_actors_quality26.gd").new();root.add_child(view)
 view.set_process(false);view.set_physics_process(false);view.hud.root.visible=false;view.actors.hero.visible=false
 var original: Dictionary=view.run.snapshot().duplicate(true)
 var enemies: Dictionary=view.run.enemies
 var tick: int=view.run.tick
 var source: Dictionary=enemies.values()[0]
 var fixture: Dictionary={}
 var roles := ["walker","ranged","charger","elite"]
 for i in roles.size():
  var e: Dictionary=source.duplicate(true);e.id=100000+i;e.kind=roles[i];e.elite=roles[i]=="elite";e.position=Vector2(-3+i*2,-4);e.state="move";e.hp_raw=1000;e.frozen_until=0;e.direction=Vector2.DOWN;e.attack_direction=Vector2.DOWN
  fixture[e.id]=e
 view.run.enemies=fixture;view.run.tick=100;view.actors.reset();view.actors.sync(view.run,.016);view.actors.hero.visible=false
 var camera := root.get_camera_3d();camera.position=Vector3(10,15,9);camera.look_at(Vector3(0,.8,-4));camera.size=9.0
 var cached: Array=view.actors._hit26_frames
 var records: Array=[]
 var sequence := 1000000
 for pair in [{"name":"north","direction":Vector2.UP},{"name":"east","direction":Vector2.RIGHT},{"name":"south","direction":Vector2.DOWN},{"name":"west","direction":Vector2.LEFT}]:
  for e in fixture.values():
   e.direction=pair.direction;e.attack_direction=pair.direction
   view.actors.consume([{"seq":sequence,"type":"hit","target_id":e.id,"tick":94,"position":e.position}]);sequence+=1
  for enabled in [false,true]:
   view.actors._hit26_frames=cached if enabled else []
   for actor in view.actors.actors.values():actor.rotation.y=atan2(pair.direction.x,pair.direction.y)
   var before: Dictionary=view.run.snapshot().duplicate(true)
   view.actors.sync(view.run,.016);view.actors.hero.visible=false
   for i in 2:await process_frame
   await RenderingServer.frame_post_draw
   var image_ := root.get_texture().get_image()
   var filename: String=pair.name+("-after.png" if enabled else "-before.png")
   image_.save_png(output.path_join(filename))
   records.append({"file":filename,"direction":pair.name,"enabled":enabled,"same_fixture_core":before==view.run.snapshot(),"size":str(image_.get_size())})
 view.actors._hit26_frames=cached;view.run.enemies=enemies;view.run.tick=tick;view.actors.reset()
 var restored: bool=original==view.run.snapshot()
 var file := FileAccess.open(output.path_join("RESULT.json"),FileAccess.WRITE)
 file.store_string(JSON.stringify({"records":records,"complete_original_core_restored":restored,"scope":"Closeup copied-role presenter fixture, same camera/controlled hit age. Before disables new upper-body blend in26; after enables it. Not normal combat/manual/performance."},"\t"));file.close()
 view.audio.reset()
 for i in 4:await process_frame
 quit(0 if restored else 1)
