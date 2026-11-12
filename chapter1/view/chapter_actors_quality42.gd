extends "res://chapter1/view/chapter_actors_quality36.gd"
## Unconnected successor: preserve Actor36 sampling; avoid identical walker commands.
## Engine equivalence/performance gate must pass before product assembly adoption.
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
 if not _is34(actor):
  super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast);return
 if not dead:
  var entity := _entity(actor)
  if not entity.is_empty() and entity.hp_raw>0 and tick<int(entity.get("stunned_until",0)):
   stun36_pose_holds+=1
   return
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
 var target_scale := Vector3.ONE*(.60+float(posmod(int(e.id)*17+int(e.generation)*7,4))*.015)
 if state.model.scale!=target_scale:state.model.scale=target_scale
 # Read actual player state: setup/pool reuse can leave state.clip stale.
 # seek(update=true) evaluates every paid sample, including hit restoration.
 if state.player.current_animation!=clip or not state.player.is_playing():state.player.play(clip,0)
 state.player.seek(time_,true)
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

## This override becomes active for Demon19/Role21 only after explicit parent
## candidate adoption. Legacy parents never call this hook.
func _sample_actor42(player: AnimationPlayer,clip: String,time_: float) -> void:
 if player.current_animation!=clip or not player.is_playing():player.play(clip,0)
 player.seek(time_,true)

var _overlap42_active := false
var _overlap42_ready := false
var _overlap42_camera_id := 0
var _overlap42_hero_a := Vector2.ZERO
var _overlap42_hero_b := Vector2.ZERO
var _overlap42_hero_radius := 0.0
func sync(run: RefCounted,delta: float) -> void:
 # Lazy fill occurs after Cloister.sync writes the interpolated hero position.
 _overlap42_ready=false
 _overlap42_camera_id=0
 _overlap42_active=true
 super.sync(run,delta)
 _overlap42_active=false
 _overlap42_ready=false
 _overlap42_camera_id=0
func _overlaps_hero(actor: Node3D,camera: Camera3D) -> bool:
 # Preserve all boss/sprite paths and out-of-sync calls verbatim.
 if not _overlap42_active or not actor.has_meta("minion19"):return super._overlaps_hero(actor,camera)
 if camera==null or (actor.global_position-hero.global_position).dot(camera.global_basis.z)<=.04:return false
 if _overlap42_ready and _overlap42_camera_id!=camera.get_instance_id():return super._overlaps_hero(actor,camera)
 var state: Dictionary=actor.get_meta("minion19")
 var rig: Skeleton3D=state.skeleton
 var walker := _is34(actor)
 var a := camera.unproject_position(_bone_point(rig,"ORG-spine" if walker else "Spine1"))
 var b := camera.unproject_position(_bone_point(rig,"ORG-head" if walker else "Head"))
 if not _overlap42_ready:
  _overlap42_hero_a=camera.unproject_position(hero.global_position+Vector3.UP*.32)
  _overlap42_hero_b=camera.unproject_position(hero.global_position+Vector3.UP*1.95)
  _overlap42_hero_radius=_screen_radius(camera,hero.global_position+Vector3.UP,.32)
  _overlap42_camera_id=camera.get_instance_id()
  _overlap42_ready=true
 var nearest := Geometry2D.get_closest_points_between_segments(a,b,_overlap42_hero_a,_overlap42_hero_b)
 var radius := _screen_radius(camera,actor.global_position+Vector3.UP,.36 if walker else .42)+_overlap42_hero_radius
 return nearest[0].distance_squared_to(nearest[1])<radius*radius

func reset() -> void:
 _overlap42_active=false
 _overlap42_ready=false
 _overlap42_camera_id=0
 super.reset()

func _set_color42(material: StandardMaterial3D,color: Color) -> void:
 if material.albedo_color!=color:material.albedo_color=color
