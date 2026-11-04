extends SceneTree
var folder := ""
var variant := "26"
var view: Node3D
var checks: Dictionary={}
var records: Array=[]
func _initialize() -> void:call_deferred("_study")
func capture(name_: String) -> void:
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png(folder.path_join(name_+".png"))
func _study() -> void:
 for arg in OS.get_cmdline_user_args():
  if arg.begins_with("--loot33-dir="):folder=arg.trim_prefix("--loot33-dir=")
  if arg.begins_with("--loot33-fx="):variant=arg.trim_prefix("--loot33-fx=")
 if folder.is_empty() or DirAccess.dir_exists_absolute(folder):quit(1);return
 DirAccess.make_dir_recursive_absolute(folder)
 view=load("res://chapter1/ChapterOne.tscn").instantiate();view.effects=load("res://chapter1/view/chapter_elements_quality%s.gd"%variant).new();root.add_child(view);view.set_process(false);view.set_physics_process(false)
 var found := false
 while view.run.tick<18000:
  view.run.step(view.full_pilot.decide())
  var qualities: Dictionary={}
  for item in view.run.items:
   if item.position.distance_squared_to(view.run.hero.position)<121:qualities[item.quality]=true
  if qualities.has("common") and qualities.has("magic") and qualities.has("rare"):found=true;break
 checks.normal_three_rarities_found=found
 view.actors.reset();view.effects.reset();view.hud.reset();view.run.events.clear();view.world.update_camera(view.run.hero.position,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.effects.sync(view.run,0);view.hud.sync(view.run,3)
 var normal: Dictionary=view.run.snapshot().duplicate(true)
 var reference=load("res://chapter1/core/chapter_run_quality16.gd").new();var policy=load("res://chapter1/core/chapter_pilot.gd").new();policy.run=reference;var started: bool=reference.start(view.seed_,view.primary)
 while reference.tick<view.run.tick:reference.step(policy.decide())
 checks.normal_complete_core=started and reference.snapshot()==view.run.snapshot()
 await capture("normal")
 var saved_items: Array=view.run.items;var saved_enemies: Dictionary=view.run.enemies;var saved_hero: Dictionary=view.run.hero.duplicate(true)
 var fixture: Array[Dictionary]=[];var rng := RandomNumberGenerator.new();rng.seed=777
 var items=load("res://chapter1/core/chapter_items.gd")
 for index in 4:
  var item: Dictionary=items.unique(0,8) if index==3 else items.roll(rng,8,["common","magic","rare"][index])
  item.uid=91000+index;item.position=Vector2(-4.5+float(index)*3,0);fixture.append(item)
 view.run.items=fixture;view.run.enemies={};view.run.hero.position=Vector2(0,-2)
 view.actors.reset();view.effects.reset();view.hud.root.visible=false;view.world.update_camera(Vector2.ZERO,10);view.world.sync(view.run,0);view.actors.sync(view.run,0);view.actors.hero.visible=false;view.actors.owner_mark.visible=false;view.effects.sync(view.run,0)
 var label := Label.new();label.position=Vector2(20,125);label.add_theme_font_size_override("font_size",22);label.text="QA four rarity display fixture · not natural unique drops · FX"+variant;root.add_child(label)
 var camera := root.get_camera_3d();camera.size=14
 view.effects.sync(view.run,0)
 await capture("fixture")
 var encoded := JSON.stringify(fixture)
 var heights: Array=[];var ring_counts: Array=[]
 for item in fixture:
  var node: Node3D=view.effects.item_nodes[item.uid];var beam: MeshInstance3D=node.get_child(0);var label3d: Label3D=node.get_child(1)
  var rings := 0
  for child in node.get_children():
   if String(child.name).begins_with("RareDropHalo33"):rings+=1
  heights.append(beam.mesh.height);ring_counts.append(rings)
  records.append({"quality":item.quality,"height":beam.mesh.height,"color":label3d.modulate,"rings":rings,"name":label3d.text})
 for repeat in 20:view.effects.sync(view.run,0)
 checks.item_data_unchanged=JSON.stringify(fixture)==encoded
 checks.no_extra_item_nodes=view.effects.item_nodes.size()==4
 if variant=="33b":
  checks.height_hierarchy=heights[0]<heights[1] and heights[1]<heights[2] and heights[2]<heights[3]
  checks.rare_halo_only=ring_counts==[0,0,1,1]
  checks.no_duplicate_halos=true
  for node in view.effects.item_nodes.values():checks.no_duplicate_halos=checks.no_duplicate_halos and node.get_child_count()<=3
 var keep: Array[Dictionary]=[fixture[2]];view.run.items=keep;view.effects.sync(view.run,0)
 await process_frame
 checks.removed_drops_release_nodes=view.effects.item_nodes.size()==1 and view.effects.item_nodes.has(fixture[2].uid)
 view.run.items=saved_items;view.run.enemies=saved_enemies;view.run.hero=saved_hero;view.effects.reset();view.actors.reset()
 checks.original_normal_restored=normal==view.run.snapshot()
 var passed := true
 for value in checks.values():passed=passed and bool(value)
 var f := FileAccess.open(folder.path_join("RESULT.json"),FileAccess.WRITE);f.store_string(JSON.stringify({"passed":passed,"checks":checks,"normal_core":normal,"normal_tick":view.run.tick,"fixture_records":records,"scope":"Normal earned common/magic/rare search checkpoint plus explicit four-rarity legal-item presentation fixture. Unique fixture is not a natural unique ground drop. Source FX26/33b, not package/manual/performance/hearing."},"\t"));f.close()
 view.audio.reset();view.queue_free()
 for i in 6:await process_frame
 quit(0 if passed else 1)
