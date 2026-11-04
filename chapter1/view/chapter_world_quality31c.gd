extends "res://chapter1/view/chapter_world_quality31b.gd"
## Narrower shadow silhouettes, retaining the original visible art and anchors.
func setup(owner: Node3D) -> void:
	super.setup(owner)
	for node in _solid_columns31:
		for index in node.multimesh.instance_count:
			var transform: Transform3D=node.multimesh.get_instance_transform(index)
			transform.basis=transform.basis.scaled(Vector3(.78,.88,.78))
			node.multimesh.set_instance_transform(index,transform)
	art_status.column_shadow_scale31c=Vector3(.78,.88,.78)
