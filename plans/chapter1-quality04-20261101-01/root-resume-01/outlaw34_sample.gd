extends SceneTree
var actor: Node3D
func _initialize() -> void:call_deferred("_sample")
func _sample() -> void:
 actor=load("res://art/skeleton_outlaw.glb").instantiate();root.add_child(actor)
 var player: AnimationPlayer=actor.find_child("AnimationPlayer",true,false)
 var rig: Skeleton3D=actor.find_child("Skeleton3D",true,false)
 player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
 var markers := ["ORG-hips","ORG-head","ORG-hand_R","ORG-hand_L","ORG-foot_R","ORG-foot_L"]
 var indices: Array[int]=[]
 for name_ in markers:
  var index := rig.find_bone(name_)
  if index<0:push_error("Missing bone "+name_);quit(1);return
  indices.append(index)
 var clips: Dictionary={}
 for name_ in player.get_animation_list():
  if name_=="RESET":continue
  var clip := player.get_animation(name_)
  var frames: Array=[]
  for sample in range(0,300):
   var at := minf(float(sample)/60,clip.length)
   player.play(name_,0);player.seek(at,true);player.advance(0)
   rig.force_update_all_bone_transforms()
   var points: Array=[];var rotations: Array=[]
   for index in indices:
    var point: Vector3=rig.global_transform*rig.get_bone_global_pose(index).origin
    points.append([point.x,point.y,point.z])
   for bone in rig.get_bone_count():
    var q := rig.get_bone_pose_rotation(bone)
    rotations.append([q.x,q.y,q.z,q.w])
   frames.append({"time":at,"points":points,"rotations":rotations})
  clips[String(name_)]={"length":clip.length,"frames":frames}
 var meshes: Array=[]
 _mesh_report(actor,meshes)
 var f := FileAccess.open("res://SAMPLES.json",FileAccess.WRITE)
 f.store_string(JSON.stringify({"bones":rig.get_bone_count(),"markers":markers,"clips":clips,"meshes":meshes,"scope":"Read-only CC0 author GLB pose samples60Hz across full clips. No attack timing/adoption/visual approval yet."}));f.close()
 actor.queue_free()
 for i in 6:await process_frame
 quit(0)
func _mesh_report(node: Node,rows: Array) -> void:
 if node is MeshInstance3D:
  var mesh: MeshInstance3D=node
  rows.append({"name":String(mesh.name),"surfaces":mesh.mesh.get_surface_count(),"binds":mesh.skin.get_bind_count() if mesh.skin else 0,"transform":mesh.global_transform,"bounds":mesh.get_aabb()})
 for child in node.get_children():_mesh_report(child,rows)
