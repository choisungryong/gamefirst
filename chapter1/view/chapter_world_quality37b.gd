extends "res://chapter1/view/chapter_world_quality37.gd"
## Dressed inner/outer arch bands share the existing voussoir batch and material.
func _voussoir22() -> ArrayMesh:
 var tool := SurfaceTool.new();tool.begin(Mesh.PRIMITIVE_TRIANGLES)
 tool.append_from(super._voussoir22(),0,Transform3D.IDENTITY)
 var angle: float=PI/15.0*.47
 for radii in [[3.28,3.43],[3.96,4.12]]:
  var points: Array[Vector3]=[]
  for z in [.51,.69]:
   for radius in radii:
    for a in [-angle,angle]:points.append(Vector3(cos(a)*radius,sin(a)*radius,z))
  tool.append_from(_chamfer37(points,.12),0,Transform3D.IDENTITY)
 return tool.commit()
func _batch22(records: Array[Dictionary],shape: Mesh,label: String) -> void:
 super._batch22(records,shape,label)
 var node: MultiMeshInstance3D=root.get_node(NodePath(label))
 var material: StandardMaterial3D=node.material_override
 material.albedo_color=Color(1.12,1.12,1.12,1.0)
