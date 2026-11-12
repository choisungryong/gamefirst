extends SceneTree
const V=preload("res://chapter1/view/chapter_actors_quality42_verify.gd")
var views=[]
func _initialize():call_deferred("go")
func go():
 for path in ["res://chapter1/chapter_one_input21.gd","res://view42b.gd"]:
  var v=load(path).new();root.add_child(v);v.set_process(false);v.set_physics_process(false);v.start_run("chapter1.skill.frost");views.append(v)
 var count=0
 for step in 900:
  for v in views:
   v.run.step(Vector2.RIGHT if step%120<60 else Vector2.UP)
   if step%120<12:
    for e in v.run.enemies.values():e.frozen_until=v.run.tick+6
   if step%120>=20 and step%120<32:
    for e in v.run.enemies.values():e.stunned_until=v.run.tick+6
   if step in [300,600]:
    v.run.enemies.clear()
   v.actors.consume(v.run.events)
   v.actors.sync(v.run,1.0/60.0)
  if views[0].actors.actors.keys()!=views[1].actors.actors.keys():print("FULL_FAIL keys step=",step);quit(2);return
  for key in views[0].actors.actors:
   var dif=V.differences(snap(views[0].actors.actors[key]),snap(views[1].actors.actors[key]));count+=1
   if not dif.is_empty():print("FULL_FAIL ",step," ",key," ",dif);quit(2);return
 for mode in ["paused","choice","inventory","equipment","playing"]:
  for repeat in 10:
   for v in views:v.run.mode=mode;v.actors.sync(v.run,1.0/60.0)
   for key in views[0].actors.actors:
    var dif=V.differences(snap(views[0].actors.actors[key]),snap(views[1].actors.actors[key]));count+=1
    if not dif.is_empty():print("MODAL_FAIL ",mode," ",key," ",dif);quit(2);return
 print("FULL_EXTENDED_PASS comparisons=",count," pool_hits=",views[0].actors.pool25_hits,"/",views[1].actors.pool25_hits)
 for v in views:v.audio.reset();v.queue_free()
 for i in 4:await process_frame
 quit()

func snap(actor):
 var result=V.snapshot(actor)
 var meta={}
 for key in actor.get_meta_list():meta[key]=normalize(actor.get_meta(key))
 result["all_metadata"]=meta
 var nodes={}
 collect(actor,"",nodes)
 result["node_transforms"]=nodes
 return result
func normalize(value):
 if value is Node:return value.get_class()+":"+str(value.get_index())
 if value is Resource:return value.get_class()+":"+value.resource_path
 if value is Dictionary:
  var output={}
  for key in value:output[key]=normalize(value[key])
  return output
 if value is Array:
  var output=[]
  for item in value:output.append(normalize(item))
  return output
 return value
func collect(node,path,out):
 if node is Node3D:out[path]={"transform":node.transform,"visible":node.visible}
 if node is Skeleton3D:
  var poses=[]
  for index in node.get_bone_count():poses.append(node.get_bone_pose(index))
  out[path]["all_bones"]=poses
 for child in node.get_children():collect(child,path+"/"+str(child.get_index()),out)
