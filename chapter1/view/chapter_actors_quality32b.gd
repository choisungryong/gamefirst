extends "res://chapter1/view/chapter_actors_quality30c.gd"
## Role-specific anticipation/recovery accents; original paid clip remains owner.
var motion32_enabled := true
const BONES32 := ["Spine1","Spine3","Shoulder.L","Shoulder.R","Arm.L","Arm.R","Head"]
var _indices32: Array[int]=[]
var _axes32: Array[Array]=[]
var motion32_samples := 0
func setup(owner_view: Node3D) -> void:
 super.setup(owner_view)
 var rig: Skeleton3D=_pool25.walker[0].get_meta("minion19").skeleton
 for name_ in BONES32:
  var index := rig.find_bone(name_)
  assert(index>=0)
  _indices32.append(index)
  var inverse := rig.get_bone_global_rest(index).basis.inverse()
  _axes32.append([(inverse*Vector3.RIGHT).normalized(),(inverse*Vector3.UP).normalized(),(inverse*Vector3.BACK).normalized()])
func _restore32(actor: Node3D) -> void:
 if not actor.has_meta("motion32_base"):return
 var rig: Skeleton3D=actor.get_meta("minion19").skeleton
 var base: Array=actor.get_meta("motion32_base")
 for i in _indices32.size():rig.set_bone_pose_rotation(_indices32[i],base[i])
 actor.remove_meta("motion32_base")
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
 if actor.has_meta("minion19") and (playing or dead):_restore32(actor)
 super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast)
 if not motion32_enabled or not playing or dead or not actor.has_meta("minion19"):return
 var entity := _entity(actor)
 if entity.is_empty() or entity.state not in ["windup","recover"]:return
 var weight := 0.0
 if entity.state=="windup":
  var duration: int=entity.get("definition",{}).get("windup",view.run.ENEMY_DEFS[entity.kind].windup)
  var left := float(int(entity.state_until)-tick)
  var progress := clampf(1.0-left/float(maxi(1,duration)),0,1)
  weight=smoothstep(.05,.65,progress)*(1.0-smoothstep(.82,1.0,progress))
 elif _demon19_attacks.has(entity.id):
  var paid: Dictionary=_demon19_attacks[entity.id]
  var extension := maxi(0,int(entity.state_until)-int(paid.end))
  var age := maxf(0,float(tick-int(paid.tick)-extension))/60.0
  var duration := float(entity.get("definition",{}).get("recover",view.run.ENEMY_DEFS[entity.kind].recover))/60.0
  weight=-.65*sin(PI*clampf(age/maxf(.05,duration),0,1))
 if absf(weight)<.001:return
 var angles: Array[Vector3]
 match String(entity.kind):
  "walker":angles=[Vector3(.10,.24,0),Vector3(0,.18,0),Vector3(.10,0,-.15),Vector3(-.24,0,.35),Vector3(.10,0,-.12),Vector3(-.64,0,.20),Vector3(-.06,-.16,0)]
  "charger":angles=[Vector3(.32,0,0),Vector3(.12,0,0),Vector3(.08,0,-.32),Vector3(.08,0,.32),Vector3(-.24,0,-.22),Vector3(-.24,0,.22),Vector3(-.20,0,0)]
  "ranged":angles=[Vector3(-.16,-.16,0),Vector3(-.12,-.12,0),Vector3(-.16,0,-.12),Vector3(-.40,0,.24),Vector3(-.30,0,-.14),Vector3(-.60,0,.08),Vector3(.10,.14,0)]
  "elite":angles=[Vector3(-.14,0,0),Vector3(-.18,0,0),Vector3(-.30,0,-.28),Vector3(-.30,0,.28),Vector3(-.48,0,-.18),Vector3(-.48,0,.18),Vector3(.16,0,0)]
  _:return
 var rig: Skeleton3D=actor.get_meta("minion19").skeleton
 var base: Array=[]
 for i in _indices32.size():
  var rotation := rig.get_bone_pose_rotation(_indices32[i]);base.append(rotation)
  var a: Vector3=angles[i]*weight*1.55
  rotation=rotation*Quaternion(_axes32[i][0],a.x)*Quaternion(_axes32[i][1],a.y)*Quaternion(_axes32[i][2],a.z)
  rig.set_bone_pose_rotation(_indices32[i],rotation.normalized())
 actor.set_meta("motion32_base",base);motion32_samples+=1
 _staff28(actor)
