extends "res://chapter1/view/chapter_world_quality22.gd"
## Unconnected surface study: recessed stone inlays, no geometry or core change.
func _ground_material() -> Material:
	var material_ := super._ground_material() as ShaderMaterial
	material_.shader=preload("res://chapter1/view/chapter_ground_quality27.gdshader")
	return material_
