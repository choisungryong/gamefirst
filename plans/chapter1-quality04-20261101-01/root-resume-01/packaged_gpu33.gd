extends SceneTree
var view: Node3D
var observer: Node
var first_victory: Dictionary={}
var victory_wall := -1.0
var shots: Dictionary={}
class Observer33 extends Node:
 var view: Node3D
 var epoch := -1
 var seq := -1
 var shatters := 0
 var cold_deaths := 0
 var zones: Dictionary={}
 var mismatches: Array=[]
 var last_tick := -1
 var ground_rarities: Dictionary={}
 var plume_peak := 0
 func _physics_process(_delta: float) -> void:
  if view.run._epoch!=epoch:epoch=view.run._epoch;seq=-1;shatters=0;cold_deaths=0
  for event in view.run.events:
   if int(event.seq)<=seq:continue
   seq=int(event.seq)
   if event.type=="shatter":
    shatters+=1
    if event.get("cause","")=="cold_death":cold_deaths+=1
 func _process(_delta: float) -> void:
  if view.run.tick==last_tick or view.run.tick%30!=0:return
  last_tick=view.run.tick
  plume_peak=maxi(plume_peak,view.effects.plumes.multimesh.visible_instance_count)
  if view.effects.get_script().resource_path!="res://chapter1/view/chapter_elements_quality33b.gd" and mismatches.size()<8:mismatches.append({"tick":view.run.tick,"reason":"wrong_fx"})
  for item in view.run.items:
   var node: Node3D=view.effects.item_nodes.get(item.uid)
   if node==null or not node.has_meta("rarity33_ready"):
    if mismatches.size()<8:mismatches.append({"tick":view.run.tick,"reason":"missing_rarity_display","uid":item.uid})
   else:ground_rarities[item.uid]=String(item.quality)
  var z := str(view.run.zone)
  if not zones.has(z):zones[z]={"samples":0,"peak_active":0,"peak_pooled":0,"peak_created":0,"latest_hits":0,"first_tick":view.run.tick}
  var row: Dictionary=zones[z];row.world_script=view.world.get_script().resource_path;row.column_count=view.world.columns31.size();row.shadow_batches=view.world._solid_columns31.size();row.columns_enabled=true
  for node in view.world._solid_columns31:row.columns_enabled=row.columns_enabled and node.visible and node.cast_shadow==GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
  row.samples+=1;row.last_tick=view.run.tick
  row.peak_active=maxi(row.peak_active,view.actors.actors.size());row.peak_pooled=maxi(row.peak_pooled,view.actors._pool25_size());row.peak_created=maxi(row.peak_created,view.actors.pool25_created);row.latest_hits=view.actors.pool25_hits
  if view.actors._pool25_size()>224 and mismatches.size()<8:mismatches.append({"tick":view.run.tick,"reason":"pool_cap"})
  for key in view.actors.actors:
   var actor: Node3D=view.actors.actors[key]
   if actor.get_parent()!=view and mismatches.size()<8:mismatches.append({"tick":view.run.tick,"key":key,"reason":"active_parent"})
   if actor.has_meta("entity_key") and actor.get_meta("entity_key")!=key and mismatches.size()<8:mismatches.append({"tick":view.run.tick,"key":key,"reason":"stale_entity_key"})
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
 view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
 view.get_window().size=Vector2i(1920,1080);DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 observer=Observer33.new();observer.view=view;observer.process_physics_priority=100;root.add_child(observer)
 view.tree_exiting.connect(_save)
 print("OBSERVER33_BOOT ",JSON.stringify({"actor_script":view.actors.get_script().resource_path,"pool_created":view.actors.pool25_created,"scope":"Actual33 normal full policy lifecycle observer; captures included. Not formal performance/manual/audio."}))
func _process(_delta: float) -> bool:
 if not is_instance_valid(view):return false
 if view.run.mode=="victory" and first_victory.is_empty():first_victory=view.run.snapshot();victory_wall=view._wall_age;view._quit_after=view._wall_age+2.1
 if victory_wall>=0:
  for at in [.35,.9,1.6]:
   if view._wall_age-victory_wall>=at and not shots.has(str(at)):
    shots[str(at)]=true
    if not view._capture_dir.is_empty():view._capture_file("victory-after-%.2f.png"%at)
 return false
func _save() -> void:
 var report := {"first_victory":first_victory,"fx_script":view.effects.get_script().resource_path,"ground_rarities":observer.ground_rarities,"plume_peak":observer.plume_peak,"counts":{"epoch":observer.epoch,"shatters":observer.shatters,"cold_death_cause":observer.cold_deaths,"tick":view.run.tick,"mode":view.run.mode},"zones":observer.zones,"mismatches":observer.mismatches,"actor_script":view.actors.get_script().resource_path,"pool_created":view.actors.pool25_created,"pool_hits":view.actors.pool25_hits,"pool_size":view.actors._pool25_size(),"scope":"Actual33 release normal earned-policy whole run with captures; half-second core-tick sampling of presenter ownership. No frame pacing/manual/audio/final art approval."}
 print("PACKAGED33_GPU_OBSERVER ",JSON.stringify(report))
