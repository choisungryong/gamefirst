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
 DisplayServer.window_set_size(Vector2i(1280,720))
 for i in 3:await process_frame
 var slots: Array=["weapon","body","ring","charm"]
 for slot in slots:
  var item: Dictionary={}
  for candidate in view.run.inventory:
   if candidate.slot==slot:item=candidate.duplicate(true)
  assert(not item.is_empty())
  view.hud.reset();view.run.mode="playing";view.hud.sync(view.run,0)
  var long_name: Dictionary=item.duplicate(true)
  long_name.name="수호자의 서리와 잿불을 잇는 오래된 "+item.name
  view.hud._present_discovery20(long_name)
  view.hud._discovery.visible=true;view.hud._discovery.modulate.a=1
  for i in 4:await process_frame
  await RenderingServer.frame_post_draw
  root.get_texture().get_image().save_png("res://shots35/discovery-%s.png"%slot)
  view.run.mode="inventory";view.hud._selected_item=item.uid;view.hud.invalidate();view.hud.sync(view.run,0)
  for i in 4:await process_frame
  view.hud._gear_scroll.scroll_vertical=100000
  for i in 2:await process_frame
  var scroll_before: int=view.hud._gear_scroll.scroll_vertical
  assert(scroll_before>0)
  view.hud.invalidate();view.hud.sync(view.run,0)
  for i in 4:await process_frame
  assert(view.hud._gear_scroll.scroll_vertical==scroll_before)
  await RenderingServer.frame_post_draw
  root.get_texture().get_image().save_png("res://shots35/inventory-%s.png"%slot)
  records.append({"slot":slot,"scroll_preserved":scroll_before,"long_name_fixture":long_name.name,"actual_item_uid":item.uid})
 view.run.mode="victory"
 assert(view.run.snapshot()==frozen)
 view.audio.reset()
 var f=FileAccess.open("res://result35.json",FileAccess.WRITE)
 f.store_string(JSON.stringify({"core_unchanged":true,"tick":view.run.tick,"records":records,"scope":"HUD35 source layout fixture on earned frost victory; explicit UI modes, not manual or package"},"\t"));f.close()
 quit()
