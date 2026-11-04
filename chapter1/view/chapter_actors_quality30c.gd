extends "res://chapter1/view/chapter_actors_quality29.gd"
## Unconnected crowd silhouette study. Stable entity identity, no simulation RNG.
## Preserve each role's height/width hierarchy, paid poses and shared mesh batch.
var variants30_enabled := true
const BONES30 := ["Head","Shoulder.L","Shoulder.R","Arm.L","Arm.R"]
const HEAD30 := [Vector3(.82,.94,.88),Vector3(1.15,1.06,1.12),Vector3.ONE,Vector3(.93,1.12,.94)]
const SHOULDER30 := [Vector3(.92,1.03,.92),Vector3(1.09,1.13,1.09),Vector3.ONE,Vector3(.94,.91,.94)]
const ARM30 := [Vector3(.91,1.10,.91),Vector3(1.13,.94,1.13),Vector3.ONE,Vector3(.97,1.04,.97)]
const WALKER30 := [Vector3(.49,.56,.49),Vector3(.57,.50,.55),Vector3(.52,.52,.52),Vector3(.49,.51,.57)]
const RANGED30 := [Vector3(.42,.60,.42),Vector3(.46,.56,.45),Vector3(.44,.58,.44),Vector3(.43,.59,.46)]
const CHARGER30 := [Vector3(.75,.46,.73),Vector3(.69,.50,.70),Vector3(.72,.48,.72),Vector3(.74,.47,.69)]
func _apply_variant30(actor: Node3D) -> void:
	if not actor.has_meta("minion19"):return
	var kind: String=actor.get_meta("kind","")
	if kind not in ["walker","ranged","charger"]:return
	var entity := _entity(actor)
	if entity.is_empty():return
	var state: Dictionary=actor.get_meta("minion19")
	var identity := "%d:%d:%s"%[entity.generation,entity.id,str(variants30_enabled)]
	if actor.get_meta("variant30_identity","")==identity:return
	var variant := posmod(int(entity.id)*17+int(entity.generation)*7,4)
	var scale_ := Vector3.ONE*.52
	if kind=="ranged":scale_=Vector3(.44,.58,.44)
	elif kind=="charger":scale_=Vector3(.72,.48,.72)
	if variants30_enabled:
		match kind:
			"walker":scale_=WALKER30[variant]
			"ranged":scale_=RANGED30[variant]
			"charger":scale_=CHARGER30[variant]
	state.model.scale=scale_
	if state.has("staff21"):
		state.staff21.scale=scale_
		state.staff21.position=actor.to_local(_bone_point(state.skeleton,"Hand.R"))
	actor.set_meta("variant30_identity",identity)
	actor.set_meta("variant30_index",variant if variants30_enabled else -1)
var _bones30: Array[int]=[]
func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	var rig: Skeleton3D=_pool25.walker[0].get_meta("minion19").skeleton
	for name_ in BONES30:
		var index := rig.find_bone(name_)
		assert(index>=0)
		_bones30.append(index)
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	var shaped := actor.has_meta("shape30_base")
	var state: Dictionary=actor.get_meta("minion19",{})
	if shaped and actor.get_meta("shape30_active",false) and (playing or dead):
		var rig: Skeleton3D=state.skeleton
		var base: Array=actor.get_meta("shape30_base")
		for i in _bones30.size():rig.set_bone_pose_scale(_bones30[i],base[i])
		actor.set_meta("shape30_active",false)
	_apply_variant30(actor)
	super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast)
	if not actor.has_meta("variant30_index") or actor.get_meta("shape30_active",false):return
	var variant: int=actor.get_meta("variant30_index")
	if variant<0:return
	var rig: Skeleton3D=state.skeleton
	var base: Array
	if shaped:base=actor.get_meta("shape30_base")
	else:
		base.resize(_bones30.size())
		actor.set_meta("shape30_base",base)
	for i in _bones30.size():
		base[i]=rig.get_bone_pose_scale(_bones30[i])
		var shape: Vector3=HEAD30[variant] if i==0 else (SHOULDER30[variant] if i<3 else ARM30[variant])
		rig.set_bone_pose_scale(_bones30[i],base[i]*shape)
	actor.set_meta("shape30_active",true)
	if state.has("staff21"):state.staff21.position=actor.to_local(_bone_point(rig,"Hand.R"))
