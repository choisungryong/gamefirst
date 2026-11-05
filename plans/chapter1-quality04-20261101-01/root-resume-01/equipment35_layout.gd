extends SceneTree
var records: Array=[]
func _initialize() -> void:call_deferred("_study")
func _study() -> void:
 var view=load("res://chapter1/ChapterOne.tscn").instantiate()
 view.hud=load("res://chapter1/view/chapter_hud_quality35.gd").new()
 root.add_child(view)
 view.set_process(false);view.set_physics_process(false)
 while view.run.mode!="victory" and view.run.tick<25000:view.run.step(view.full_pilot.decide())
 assert(view.run.mode=="victory")
 view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear()
 view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0)
 var frozen: Dictionary=view.run.snapshot().duplicate(true)
 var reward: Dictionary={}
 for item in view.run.inventory:
  if item.uid==view.run._elite_reward_uid:reward=item.duplicate(true)
 assert(not reward.is_empty())
 DirAccess.make_dir_recursive_absolute("res://shots35")
 for resolution in [Vector2i(1920,1080),Vector2i(1280,720)]:
  DisplayServer.window_set_size(resolution)
  for i in 3:await process_frame
  for mode in ["discovery","victory","inventory"]:
   view.hud.reset()
   view.run.mode="playing" if mode=="discovery" else mode
   view.hud.sync(view.run,2.0)
   if mode=="discovery":
    view.hud._present_discovery20(reward)
    view.hud._discovery.visible=true;view.hud._discovery.modulate.a=1
   for i in 4:await process_frame
   await RenderingServer.frame_post_draw
   var image=root.get_texture().get_image()
   image.save_png("res://shots35/%s-%d.png"%[mode,resolution.x])
   records.append({"mode":mode,"requested":[resolution.x,resolution.y],"actual":[image.get_width(),image.get_height()],"discovery_rect":str(view.hud._discovery.get_global_rect())})
 view.run.mode="victory"
 assert(view.run.snapshot()==frozen)
 view.audio.reset()
 var f=FileAccess.open("res://result35.json",FileAccess.WRITE)
 f.store_string(JSON.stringify({"core_unchanged":true,"tick":view.run.tick,"records":records,"scope":"HUD35 source layout fixture on earned frost victory; explicit UI modes, not manual or package"},"\t"));f.close()
 quit()
