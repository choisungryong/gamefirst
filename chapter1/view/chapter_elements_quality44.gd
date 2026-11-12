extends "res://chapter1/view/chapter_elements_quality43.gd"
## Unconnected arc candidate: paid segments/widths/ages and stun markers unchanged.
func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	var ribbon := ShaderMaterial.new()
	ribbon.shader=preload("res://chapter1/view/arc_core_quality44.gdshader")
	arc_surface.material_override=ribbon
	var contact := ShaderMaterial.new()
	contact.shader=preload("res://chapter1/view/arc_contact_quality44.gdshader")
	contact_batch.material_override=contact
