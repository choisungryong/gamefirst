extends "res://chapter1/view/chapter_elements_quality20.gd"
## Existing single projectile batch; paid positions, size and damage unchanged.
func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	var material := ShaderMaterial.new()
	material.shader=preload("res://chapter1/view/comet_hostile22.gdshader")
	projectiles.material_override=material
