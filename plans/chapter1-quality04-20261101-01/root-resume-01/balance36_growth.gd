extends SceneTree
var checks: Array=[]
func check(ok: bool,label: String) -> void:checks.append({"ok":ok,"label":label})
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
 var view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
 view.set_process(false);view.set_physics_process(false);DisplayServer.window_set_size(Vector2i(1280,720))
 DirAccess.make_dir_recursive_absolute("res://growth36-shots")
 var records: Array=[]
 for primary in ["chapter1.skill.ember","chapter1.skill.frost","chapter1.skill.arc"]:
  view.run.start(90131,primary)
  while view.run.mode=="playing" and view.run.tick<3000:view.run.step(Vector2.ZERO)
  check(view.run.mode=="choice","earned first growth choice "+primary)
  view.actors.reset();view.effects.reset();view.hud.reset()
  view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,0)
  var frozen: Dictionary=view.run.snapshot().duplicate(true)
  var descriptions: Array=[]
  for card in view.run.get_offer().cards:descriptions.append(view.hud._card_description(card,view.run))
  for i in 4:await process_frame
  await RenderingServer.frame_post_draw
  var image=root.get_texture().get_image();image.save_png("res://growth36-shots/%s.png"%primary.get_slice(".",2))
  check(view.run.snapshot()==frozen,"UI preserves core "+primary)
  records.append({"primary":primary,"tick":view.run.tick,"image":[image.get_width(),image.get_height()],"descriptions":descriptions})
 view.audio.reset();var passed: bool=true
 for c in checks:passed=passed and c.ok
 var f=FileAccess.open("res://growth36-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"passed":passed,"checks":checks,"records":records,"scope":"Source HUD36 first naturally earned growth choices, stationary hero, explicit 720p captures. Not manual selection/whole package."},"\t"));f.close();quit(0 if passed else 2)
