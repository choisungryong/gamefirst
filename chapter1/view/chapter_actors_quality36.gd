extends "res://chapter1/view/chapter_actors_quality34b.gd"
## Shock holds the currently displayed paid pose; cold/death keep their own rules.
var stun36_pose_holds := 0
func _update_pose(actor: Node3D,direction: Vector2,moving: bool,casting: bool,dead: bool,tick: int,playing: bool,hit: bool=false,brief_cast: bool=false) -> void:
 if not dead:
  var entity := _entity(actor)
  if not entity.is_empty() and entity.hp_raw>0 and tick<int(entity.get("stunned_until",0)):
   stun36_pose_holds+=1
   return
 super._update_pose(actor,direction,moving,casting,dead,tick,playing,hit,brief_cast)
