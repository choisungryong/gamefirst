from pathlib import Path
h=Path('plans/chapter1-quality04-20261101-01/root-resume-01')
s='''extends SceneTree
var view: Node3D
var observer: Node
var first_victory: Dictionary={}
var victory_wall := -1.0
var shots: Dictionary={}
class Observer25 extends Node:
 var view: Node3D
 var epoch := -1
 var seq := -1
 var shatters := 0
 var cold_deaths := 0
 var zones: Dictionary={}
 var mismatches: Array=[]
 var last_tick := -1
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
  var z := str(view.run.zone)
  if not zones.has(z):zones[z]={"samples":0,"peak_active":0,"peak_pooled":0,"peak_created":0,"latest_hits":0,"first_tick":view.run.tick}
  var row: Dictionary=zones[z];row.samples+=1;row.last_tick=view.run.tick
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
 observer=Observer25.new();observer.view=view;observer.process_physics_priority=100;root.add_child(observer)
 view.tree_exiting.connect(_save)
 print("OBSERVER25B_BOOT ",JSON.stringify({"actor_script":view.actors.get_script().resource_path,"pool_created":view.actors.pool25_created,"scope":"Actual25b normal full policy lifecycle observer; captures included. Not formal performance/manual/audio."}))
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
 var report := {"first_victory":first_victory,"counts":{"epoch":observer.epoch,"shatters":observer.shatters,"cold_death_cause":observer.cold_deaths,"tick":view.run.tick,"mode":view.run.mode},"zones":observer.zones,"mismatches":observer.mismatches,"actor_script":view.actors.get_script().resource_path,"pool_created":view.actors.pool25_created,"pool_hits":view.actors.pool25_hits,"pool_size":view.actors._pool25_size(),"scope":"Actual25b release normal earned-policy whole run with captures; half-second core-tick sampling of presenter ownership. No frame pacing/manual/audio/final art approval."}
 print("PACKAGED25B_GPU_OBSERVER ",JSON.stringify(report))
'''
(h/'packaged_gpu25b.gd').write_text(s,encoding='utf-8')
s=(h/'run_packaged_gpu19_01.py').read_text(encoding='utf-8').replace('full19','full25b').replace('packaged_gpu19.gd','packaged_gpu25b.gd').replace('PACKAGED19_GPU_OBSERVER','PACKAGED25B_GPU_OBSERVER').replace('Actual packaged19','Actual packaged25b').replace('PASS GPU19','PASS GPU25B')
s=s.replace("write(OUT/'RESULT.json',", "assert not obs['mismatches'] and obs['pool_hits']>1000 and obs['pool_size']<=224\nwrite(OUT/'RESULT.json',").replace("'observer':obs['counts']","'observer':obs")
(h/'run_packaged_gpu25b_01.py').write_text(s,encoding='utf-8')
