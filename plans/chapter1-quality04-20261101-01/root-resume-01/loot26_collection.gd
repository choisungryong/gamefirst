extends "res://chapter1/chapter_one_input21.gd"
var armed26 := false
var checkpoint26 := 0
var target26 := -1
var picked26 := -1
var commands26: Array[Vector2]=[]
var clean26 := true
var seq26 := -1
func _init() -> void:
 super._init();effects=preload("res://chapter1/view/chapter_elements_quality26.gd").new()
func _ready() -> void:
 super._ready()
 while run.tick<16143:run.step(full_pilot.decide())
 for item in run.items:
  if item.position.distance_squared_to(run.hero.position)<64:target26=item.uid;break
 assert(target26>0)
 checkpoint26=run.tick;actors.reset();effects.reset();hud.reset();run.events.clear()
 world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);effects.sync(run,0);hud.sync(run,0)
 armed26=true;_shot26("before")
func _pilot_input() -> Vector2:
 if not armed26:return super._pilot_input()
 var movement := Vector2.ZERO
 for item in run.items:
  if item.uid==target26:movement=run.hero.position.direction_to(item.position);break
 commands26.append(movement)
 return movement
func _physics_process(delta: float) -> void:
 super._physics_process(delta)
 if not armed26:return
 for event in run.events:
  if int(event.seq)<=seq26:continue
  seq26=int(event.seq)
  if event.type=="item_pickup" and event.item.uid==target26 and picked26<0:
   picked26=run.tick;_quit_after=_wall_age+1.0;_shot26("collected")
func _process(delta: float) -> void:
 super._process(delta)
 if armed26 and picked26>=0:clean26=clean26 and not effects.item_nodes.has(target26) and effects.layout26_records.all(func(v):return int(v.uid)!=target26)
func _shot26(name_: String) -> void:
 await RenderingServer.frame_post_draw
 DirAccess.make_dir_recursive_absolute("res://loot26-shots")
 get_viewport().get_texture().get_image().save_png("res://loot26-shots/"+name_+".png")
func _print_result() -> void:
 super._print_result()
 if not armed26:return
 var reference=ChapterRun.new();var policy=ChapterPilot.new();policy.run=reference
 var started: bool=reference.start(seed_,primary);assert(started)
 while reference.tick<checkpoint26:reference.step(policy.decide())
 for movement in commands26:reference.step(movement)
 var same: bool=reference.snapshot()==run.snapshot()
 var trace: Array=[]
 for v in commands26:trace.append([v.x,v.y])
 var file := FileAccess.open("res://loot26-collection.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"checkpoint":checkpoint26,"target_uid":target26,"pickup_tick":picked26,"final_tick":run.tick,"same_complete_core":same,"name_and_node_removed":clean26,"movement_commands":trace,"scope":"Normal earned frost checkpoint then ordinary directional movement toward a real nearby drop, no position/item grant. Independent core replay of identical movement. Source GPU pickup/name cleanup, not manual/fullrun/performance."},"\t"));file.close()
 assert(same and picked26>=0 and clean26)
