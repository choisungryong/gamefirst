extends "res://chapter1/view/chapter_world_quality31d.gd"
## Unconnected study:37b geometry, rear-only weathered material; proxies unchanged.
const Geometry37b=preload("res://chapter1/view/chapter_world_quality37b.gd")
var _stone_geometry37=Geometry37b.new()
func _voussoir22() -> ArrayMesh:
 return _stone_geometry37._voussoir22()
func _batch22(records: Array[Dictionary],shape: Mesh,label: String) -> void:
 var rear: bool=label in ["RearMasonry22","RearArches22"]
 if label=="RearMasonry22":
  var points: Array[Vector3]=[]
  for z in [-.5,.5]:
   for x in [-.5,.5]:
    for y in [-.5,.5]:points.append(Vector3(x,y,z))
  shape=_stone_geometry37._chamfer37(points,.07)
 super._batch22(records,shape,label)
 if not rear:return
 var material := ShaderMaterial.new()
 material.shader=preload("res://chapter1/view/chapter_masonry_quality37c.gdshader")
 material.set_shader_parameter("flagstone",_texture(ART_BASE+"ground_flagstone_v01.png"))
 material.set_shader_parameter("soil",_texture(ART_BASE+"ground_soil_v01.png"))
 var node: MultiMeshInstance3D=root.get_node(NodePath(label))
 node.material_override=material
