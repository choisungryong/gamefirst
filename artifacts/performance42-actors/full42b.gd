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
   v.actors.consume(v.run.events)
   v.actors.sync(v.run,1.0/60.0)
  if views[0].actors.actors.keys()!=views[1].actors.actors.keys():print("FULL_FAIL keys step=",step);quit(2);return
  for key in views[0].actors.actors:
   var dif=V.differences(V.snapshot(views[0].actors.actors[key]),V.snapshot(views[1].actors.actors[key]));count+=1
   if not dif.is_empty():print("FULL_FAIL ",step," ",key," ",dif);quit(2);return
 print("FULL_PASS comparisons=",count)
 for v in views:v.audio.reset();v.queue_free()
 for i in 4:await process_frame
 quit()
