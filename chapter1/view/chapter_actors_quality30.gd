extends "res://chapter1/view/chapter_actors_quality29.gd"
## Unconnected crowd silhouette study. Stable entity identity, no simulation RNG.
## Preserve each role's height/width hierarchy, paid poses and shared mesh batch.
var variants30_enabled := true
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
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
	_apply_variant30(actor)
	super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast)
