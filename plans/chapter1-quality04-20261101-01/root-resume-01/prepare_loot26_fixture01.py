from pathlib import Path
h=Path('plans/chapter1-quality04-20261101-01/root-resume-01')
s='''extends "res://chapter1/chapter_one_input21.gd"
class ComparedFX extends "res://chapter1/view/chapter_elements_quality26.gd":
 var enabled := true
 func sync(run: RefCounted,delta: float) -> void:
  super.sync(run,delta)
  if enabled:return
  _loot26_leaders.visible=false
  for node in item_nodes.values():
   var label: Label3D=node.get_child(1)
   label.font=null;label.font_size=26;label.pixel_size=.0075;label.outline_size=12;label.no_depth_test=false;label.position=Vector3(0,1.5,0);label.remove_meta("loot26_ready")
var records: Array=[]
var checks: Dictionary={}
func _init() -> void:
 super._init();effects=ComparedFX.new()
func _ready() -> void:
 super._ready();set_process(false);set_physics_process(false)
 while run.tick<16000:run.step(full_pilot.decide())
 actors.reset();effects.reset();hud.reset();run.events.clear()
 world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);hud.sync(run,0)
 var baseline: Dictionary=run.snapshot().duplicate(true)
 effects.enabled=false;effects.sync(run,0);await _shot("normal-before")
 checks.normal_before_core=baseline==run.snapshot()
 effects.enabled=true;effects.sync(run,0);await _shot("normal-after");_check("normal")
 checks.normal_after_core=baseline==run.snapshot()
 var original_items: Array=run.items
 var fixture: Array[Dictionary]=[]
 for i in 12:
  var item: Dictionary=run.inventory[i%run.inventory.size()].duplicate(true)
  item.uid=100000+i;item.position=run.hero.position+Vector2(4.2+float(i%3)*.16,float(i/3)*.12-1.0);item.quality=["rare","magic","common"][i%3]
  item.name=["수확의 활력의 순례자의 로브","보호의 수확의 쇠실 흉의","불꽃의 박동의 마법봉"][i%3]
  fixture.append(item)
 run.items=fixture
 var fixture_core: Dictionary=run.snapshot().duplicate(true)
 for resolution in [Vector2i(1920,1080),Vector2i(1440,810),Vector2i(1280,720)]:
  get_window().size=resolution
  for i in 3:await get_tree().process_frame
  if resolution==Vector2i(1920,1080):
   effects.enabled=false;effects.sync(run,0);await _shot("dense-before")
  effects.enabled=true;effects.sync(run,0)
  var name_ := "dense-%d"%resolution.x
  await _shot(name_);_check(name_)
  checks[name_+"_core_untouched"]=fixture_core==run.snapshot()
 run.items=original_items;effects.reset();checks.original_core_restored=baseline==run.snapshot()
 var file := FileAccess.open("res://loot26-fixture.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"checks":checks,"records":records,"normal_tick":run.tick,"scope":"Normal earned16000tick display before/after plus copied12-item name-overlap fixture at3resolutions, no core stepping during display; complete original core restored. Before resets only label properties to25b defaults in the same26 presenter. Not manual/fullrun/performance."},"\\t"));file.close()
 audio.reset()
 for i in 4:await get_tree().process_frame
 var failed := false
 for value in checks.values():if not value:failed=true
 get_tree().quit(1 if failed else 0)
func _check(name_: String) -> void:
 var camera := get_viewport().get_camera_3d()
 var count := 0;var placed := true;var font_ok := true;var beams_ok := true;var inside := true;var separated := true
 var size_: Vector2=get_viewport().get_visible_rect().size
 var rects: Array[Rect2]=[];var names: Array=[]
 for record in effects.layout26_records:
  count+=1;placed=placed and record.placed
  var node: Node3D=effects.item_nodes[record.uid];var label: Label3D=node.get_child(1)
  var actual: float=camera.unproject_position(label.global_position+camera.global_basis.y*label.font_size*label.pixel_size).distance_to(camera.unproject_position(label.global_position))
  font_ok=font_ok and absf(actual-15)<.01
  var source: Dictionary={}
  for item in run.items:
   if item.uid==record.uid:source=item;break
  beams_ok=beams_ok and node.position.is_equal_approx(Vector3(source.position.x,0,source.position.y))
  var rect: Rect2=record.rect
  inside=inside and rect.position.x>=0 and rect.end.x<=size_.x and rect.position.y>=92 and rect.end.y<=size_.y-112
  for other in rects:separated=separated and not rect.intersects(other)
  rects.append(rect);names.append({"uid":record.uid,"font_nominal_projected":actual,"rect":[rect.position.x,rect.position.y,rect.size.x,rect.size.y],"shifted":record.shifted})
 checks[name_+"_font_readable"]=font_ok;checks[name_+"_no_overlap"]=separated;checks[name_+"_inside"]=inside;checks[name_+"_placed"]=placed;checks[name_+"_paid_beams"]=beams_ok
 if name_.begins_with("dense"):checks[name_+"_all12"]=count==12
 records.append({"case":name_,"logical_viewport":str(size_),"names":names})
func _shot(name_: String) -> void:
 for i in 2:await get_tree().process_frame
 await RenderingServer.frame_post_draw
 DirAccess.make_dir_recursive_absolute("res://loot26-shots")
 get_viewport().get_texture().get_image().save_png("res://loot26-shots/"+name_+".png")
'''
(h/'loot26_fixture.gd').write_text(s,encoding='utf-8')
s=(h/'run_hit26_fixture02.py').read_text(encoding='utf-8').replace('hit26/fixture02','loot26/fixture01').replace('chapter1-hit26-fixture02','chapter1-loot26-fixture01').replace('chapter_actors_quality26.gd','chapter_elements_quality26.gd').replace('hit26_fixture02.gd','loot26_fixture.gd').replace("('headless',['--headless','res://Compare.tscn'","('gpu',['res://Compare.tscn'").replace('hit26-fixture.json','loot26-fixture.json')
s=s.replace("shutil.copy2(S/'loot26-fixture.json',O/'RESULT.json')","shutil.copy2(S/'loot26-fixture.json',O/'RESULT.json');shutil.copytree(S/'loot26-shots',O/'shots')")
(h/'run_loot26_fixture01.py').write_text(s,encoding='utf-8')
