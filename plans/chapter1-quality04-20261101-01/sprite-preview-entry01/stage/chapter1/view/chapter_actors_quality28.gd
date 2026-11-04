extends "res://chapter1/view/chapter_actors_quality25b.gd"
## Authored upper-body hit poses, sampled once before the menu.
## No new combat state; planted attacks, frozen poses and death retain priority.
const HIT28_BONES := ["Spine1","Spine2","Spine3","Shoulder.L","Shoulder.R","Arm.L","Arm.R","Neck.001","Head"]
const HIT28_SAMPLES := 13
var _hit28_indices: Array[int]=[]
var _hit28_frames: Array=[]
var hit28_blends := 0
func setup(owner_view: Node3D) -> void:
 super.setup(owner_view)
 var actor: Node3D=_pool25.walker[0]
 var state: Dictionary=actor.get_meta("minion19")
 var rig: Skeleton3D=state.skeleton
 var player: AnimationPlayer=state.player
 for name_ in HIT28_BONES:
  var index := rig.find_bone(name_)
  assert(index>=0)
  _hit28_indices.append(index)
 var length_: float=player.get_animation("hit").length
 for sample in HIT28_SAMPLES:
  player.play("hit",0);player.seek(float(sample)/float(HIT28_SAMPLES-1)*length_,true);player.advance(0)
  var poses: Array[Transform3D]=[]
  for index in _hit28_indices:poses.append(rig.get_bone_pose(index))
  _hit28_frames.append(poses)
 player.play("idle",0);player.seek(0,true);player.advance(0)
func _restore28(actor: Node3D) -> void:
 if not actor.has_meta("hit28_base"):return
 var rig: Skeleton3D=actor.get_meta("minion19").skeleton
 var poses: Array=actor.get_meta("hit28_base")
 for i in _hit28_indices.size():rig.set_bone_pose(_hit28_indices[i],poses[i])
 actor.remove_meta("hit28_base");actor.remove_meta("hit28_weight")
 _staff28(actor)
func _staff28(actor: Node3D) -> void:
 var state: Dictionary=actor.get_meta("minion19")
 if state.has("staff21"):state.staff21.position=actor.to_local(_bone_point(state.skeleton,"Hand.R"))
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
 if not actor.has_meta("minion19"):
  super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast);return
 # Recover retains the direction of the paid attack instead of stale travel.
 var facing_entity := _entity(actor)
 if playing and not dead and not facing_entity.is_empty() and facing_entity.state=="recover":
  direction=facing_entity.attack_direction
 # A modal or cold freeze holds the complete currently displayed pose.
 if playing or dead:_restore28(actor)
 super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast)
 if not playing or dead or not hit or _hit28_frames.is_empty():return
 var entity := _entity(actor)
 if entity.is_empty() or entity.state not in ["move","idle"]:return
 var age := clampf(float(tick-int(_enemy_hit_until.get(entity.id,tick))+12)/12.0,0,1)
 var weight := .85*sin(PI*age)
 if weight<.001:return
 var sample_ := age*float(HIT28_SAMPLES-1)
 var a := mini(int(sample_),HIT28_SAMPLES-1);var b := mini(a+1,HIT28_SAMPLES-1)
 var rig: Skeleton3D=actor.get_meta("minion19").skeleton
 var base: Array[Transform3D]=[]
 for i in _hit28_indices.size():
  var index: int=_hit28_indices[i]
  var original := rig.get_bone_pose(index);base.append(original)
  var pose: Transform3D=_hit28_frames[a][i].interpolate_with(_hit28_frames[b][i],sample_-float(a))
  var blended := original.interpolate_with(pose,weight)
  if HIT28_BONES[i]=="Spine1":
   var recoil_axis := (rig.get_bone_global_rest(index).basis.inverse()*Vector3.RIGHT).normalized()
   blended.basis=blended.basis*Basis(recoil_axis,-.28*weight)
  rig.set_bone_pose(index,blended)
 _staff28(actor)
 actor.set_meta("hit28_base",base);actor.set_meta("hit28_weight",weight);hit28_blends+=1
