extends "res://chapter1/view/chapter_actors_quality32b.gd"
## Unconnected walker-family study. Original actor roots, core, pool and paid events.
const OUTLAW34=preload("res://chapter1/art/skeleton_outlaw/v02/skeleton_outlaw_merged.glb")
const WALK34 := 56.0/60.0
const SWING34 := 68.0/60.0
const STRIKE34 := 25.0/60.0
const HIT34 := ["ORG-spine","ORG-chest","ORG-neck","ORG-head","ORG-shoulder_L","ORG-upper_arm_L","ORG-forearm_L","ORG-shoulder_R","ORG-upper_arm_R","ORG-forearm_R"]
var _hit34_indices: Array[int]=[]
var _hit34_frames: Array=[]
var _head34 := -1
var hit34_blends := 0
var motion34_samples := 0
var replacements34 := 0
func _is34(actor: Node3D) -> bool:
 return actor.has_meta("minion19") and bool(actor.get_meta("minion19").get("family34",false))
func setup(owner_view: Node3D) -> void:
 # Existing Mophs pose caches are built before replacing only the walker models.
 super.setup(owner_view)
 for actor in _pool25.walker:_replace34(actor)
 var state: Dictionary=_pool25.walker[0].get_meta("minion19")
 var rig: Skeleton3D=state.skeleton
 _head34=rig.find_bone("ORG-head")
 assert(_head34>=0)
 for name_ in HIT34:
  var index := rig.find_bone(name_);assert(index>=0);_hit34_indices.append(index)
 for sample in 13:
  state.player.play("hit",0);state.player.seek(float(sample)/12.0*(46.0/60.0),true);state.player.advance(0)
  var poses: Array[Transform3D]=[]
  for index in _hit34_indices:poses.append(rig.get_bone_pose(index))
  _hit34_frames.append(poses)
 state.player.play("idle",0);state.player.seek(0,true);state.player.advance(0)
func _replace34(actor: Node3D) -> void:
 if _is34(actor):return
 var old: Dictionary=actor.get_meta("minion19")
 var model: Node3D=OUTLAW34.instantiate();actor.add_child(model);model.scale=Vector3.ONE*.62
 var rig: Skeleton3D=model.find_child("Skeleton3D",true,false)
 var player: AnimationPlayer=model.find_child("AnimationPlayer",true,false)
 player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
 var materials: Array[StandardMaterial3D]=[];_materials34(model,materials)
 var state := {"family34":true,"model":model,"player":player,"skeleton":rig,"materials":materials,"fade":1.0,"death_age":0.0,"clip":"","bucket":-1}
 actor.set_meta("minion19",state)
 _disarm34(old.model);old.model.get_parent().remove_child(old.model);old.model.queue_free()
 player.play("idle",0);player.seek(0,true);player.advance(0);replacements34+=1
func _materials34(node: Node,materials: Array[StandardMaterial3D]) -> void:
 if node is MeshInstance3D:
  node.layers=2;node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON
  for surface in node.mesh.get_surface_count():
   var material: StandardMaterial3D=node.get_active_material(surface).duplicate()
   material.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
   var tint := Color(.76,.76,.69)
   material.albedo_color=tint;material.set_meta("demon19_tint",tint)
   material.rim_enabled=true;material.rim=.18;material.rim_tint=.12
   node.set_surface_override_material(surface,material);materials.append(material)
 for child in node.get_children():_materials34(child,materials)
func _create(kind: String) -> Node3D:
 var actor := super._create(kind)
 if kind=="walker" and actor.has_meta("minion19"):_replace34(actor)
 return actor
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
 if not _is34(actor):
  super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast);return
 var e := _entity(actor)
 if e.is_empty():return
 var state: Dictionary=actor.get_meta("minion19")
 if not playing and not dead and not String(state.clip).is_empty():return
 if e.state=="recover":direction=e.attack_direction
 if playing and direction.length_squared()>.001:actor.rotation.y=lerp_angle(actor.rotation.y,atan2(direction.x,direction.y),1-exp(-_render_delta*18))
 var fraction := clampf(Engine.get_physics_interpolation_fraction(),0,1) if playing else 0.0
 var clip := "idle";var time_ := 0.0
 if dead:
  clip="death"
  if view.run.mode not in ["paused","choice","inventory","equipment"]:state.death_age=maxf(float(state.death_age)+_render_delta,float(tick-int(e.dead_tick))/60.0)
  time_=minf(float(state.death_age),1.60)
 elif e.state=="windup":
  var duration: int=e.get("definition",{}).get("windup",view.run.ENEMY_DEFS[e.kind].windup)
  var left := maxf(0,float(int(e.state_until)-tick)-fraction)
  clip="attack_slam";time_=clampf(1-left/float(maxi(1,duration)),0,1)*STRIKE34
 elif e.state=="recover" and _demon19_attacks.has(e.id):
  var paid: Dictionary=_demon19_attacks[e.id]
  var extension := maxi(0,int(e.state_until)-int(paid.end))
  var duration: int=e.get("definition",{}).get("recover",view.run.ENEMY_DEFS[e.kind].recover)
  var progress := clampf((float(tick-int(paid.tick)-extension)+fraction)/float(maxi(1,duration)),0,1)
  clip="attack_slam";time_=STRIKE34+progress*(SWING34-STRIKE34)
 elif moving:
  clip="walk"
  var sample: Dictionary=actor.get_meta("motion_sample",{})
  time_=fposmod(float(sample.get("phase",0.0))+float((int(e.id)*37)%101)/101.0,1)*WALK34
 else:time_=fposmod(float(tick)/60.0+float(e.id)*.113,128.0/60.0)
 var near_: bool=e.position.distance_squared_to(view.run.hero.position)<30.25
 var bucket: int=tick/3
 if moving and not hit and not near_ and state.clip==clip and int(state.bucket)==bucket:return
 state.clip=clip;state.bucket=bucket
 state.model.scale=Vector3.ONE*(.60+float(posmod(int(e.id)*17+int(e.generation)*7,4))*.015)
 state.player.play(clip,0);state.player.seek(time_,true);state.player.advance(0)
 if playing and not dead and hit and e.state in ["move","idle"] and not _hit34_frames.is_empty():
  var age := clampf(float(tick-int(_enemy_hit_until.get(e.id,tick))+12)/12.0,0,1)
  var weight := .85*sin(PI*age);var sample_ := age*12.0;var a := mini(int(sample_),12);var b := mini(a+1,12)
  for i in _hit34_indices.size():
   var index: int=_hit34_indices[i]
   var pose: Transform3D=_hit34_frames[a][i].interpolate_with(_hit34_frames[b][i],sample_-float(a))
   state.skeleton.set_bone_pose(index,state.skeleton.get_bone_pose(index).interpolate_with(pose,weight))
  hit34_blends+=1
 if _head34>=0:state.skeleton.set_bone_pose_scale(_head34,Vector3.ONE*.72)
 actor.set_meta("minion19_pose",{"clip":clip,"time":time_,"dead":dead,"tick":tick,"family34":true});motion34_samples+=1
func _overlaps_hero(actor: Node3D,camera: Camera3D) -> bool:
 if not _is34(actor):return super._overlaps_hero(actor,camera)
 if camera==null or (actor.global_position-hero.global_position).dot(camera.global_basis.z)<=.04:return false
 var rig: Skeleton3D=actor.get_meta("minion19").skeleton
 var a := camera.unproject_position(_bone_point(rig,"ORG-spine"));var b := camera.unproject_position(_bone_point(rig,"ORG-head"))
 var ha := camera.unproject_position(hero.global_position+Vector3.UP*.32);var hb := camera.unproject_position(hero.global_position+Vector3.UP*1.95)
 var nearest := Geometry2D.get_closest_points_between_segments(a,b,ha,hb)
 var radius := _screen_radius(camera,actor.global_position+Vector3.UP,.36)+_screen_radius(camera,hero.global_position+Vector3.UP,.32)
 return nearest[0].distance_squared_to(nearest[1])<radius*radius

func _disarm34(node: Node) -> void:
 # Remove the render instance base before freeing its material overrides.
 if node is MeshInstance3D:node.mesh=null
 for child in node.get_children():_disarm34(child)
