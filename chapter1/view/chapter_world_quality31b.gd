extends "res://chapter1/view/chapter_world_quality31.gd"
## Keep authored ornate column sprites; reuse hidden solids as shadow-only proxies.
## No relocation of visible props, added light, collider or core state.
func setup(owner: Node3D) -> void:
	super.setup(owner)
	for node in _solid_columns31:
		var broken: bool=String(node.name).contains("Broken")
		var index := 0
		for column in columns31:
			if (column.id=="pillar_broken")!=broken:continue
			var transform: Transform3D=node.multimesh.get_instance_transform(index)
			transform.origin=column.at;node.multimesh.set_instance_transform(index,transform);index+=1
		assert(index==node.multimesh.instance_count)
		# Visible ornament and its existing near-foot contact are unchanged.
		node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_SHADOWS_ONLY
	clearance31.clear()
	art_status.column_shadow_only31b=true
	set_columns31(false)
func set_columns31(enabled: bool) -> void:
	for node in _old_columns31:node.visible=true
	for node in _solid_columns31:node.visible=enabled
