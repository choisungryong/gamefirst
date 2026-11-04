extends "res://chapter1/view/chapter_actors_quality28.gd"
## Unconnected study: existing moon casts ordinary-body silhouettes on ground.
## No extra light, mesh, actor, collision or simulation state.
func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	for actor in _pool25_root.get_children():_enable_actor29(actor)
	for actor in actors.values():_enable_actor29(actor)
func _create(kind: String) -> Node3D:
	var actor := super._create(kind)
	_enable_actor29(actor)
	return actor
func _enable_actor29(actor: Node3D) -> void:
	if actor.has_meta("minion19"):_enable_meshes29(actor.get_meta("minion19").model)
func _enable_meshes29(node: Node) -> void:
	if node is MeshInstance3D:node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	for child in node.get_children():_enable_meshes29(child)
