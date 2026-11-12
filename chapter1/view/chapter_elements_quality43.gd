extends "res://chapter1/view/chapter_elements_quality39.gd"
## Unconnected fire presentation candidate. Same paid geometry, pools and ages.
## Shader replacements only: no events, damage, RNG, particles or timing added.
func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	var bolt := ShaderMaterial.new()
	bolt.shader=preload("res://chapter1/view/ember_core_quality43.gdshader")
	projectiles.material_override=bolt
	var plume := ShaderMaterial.new()
	plume.shader=preload("res://chapter1/view/ember_afterglow_quality43.gdshader")
	plumes.material_override=plume
	var contact := ShaderMaterial.new()
	contact.shader=preload("res://chapter1/view/ember_contact_quality43.gdshader")
	contact_batch.material_override=contact
