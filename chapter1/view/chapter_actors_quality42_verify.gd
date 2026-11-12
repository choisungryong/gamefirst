extends RefCounted
## Read-only oracle for the separately authorized Actor36/42 engine stage.
## Call after each identical input on isolated, equally initialized actor owners.
static func snapshot(actor: Node3D) -> Dictionary:
 var state: Dictionary=actor.get_meta("minion19",{})
 var result := {"transform":actor.transform,"visible":actor.visible,"pose":actor.get_meta("minion19_pose",{})}
 if state.is_empty():return result
 var rig: Skeleton3D=state.skeleton
 var bones: Array[Transform3D]=[]
 for index in rig.get_bone_count():bones.append(rig.get_bone_pose(index))
 var colors: Array[Color]=[]
 for material in state.materials:colors.append(material.albedo_color)
 result.merge({"model_transform":state.model.transform,"model_visible":state.model.visible,"bones":bones,"colors":colors,"fade":state.fade,"death_age":state.death_age,"clip":state.clip,"bucket":state.bucket,"animation":state.player.current_animation,"animation_position":state.player.current_animation_position,"playing":state.player.is_playing()})
 return result
static func differences(reference: Dictionary,candidate: Dictionary) -> Array[String]:
 var mismatches: Array[String]=[]
 for key in reference:
  if not candidate.has(key) or reference[key]!=candidate[key]:mismatches.append(String(key))
 for key in candidate:
  if not reference.has(key):mismatches.append(String(key))
 return mismatches
