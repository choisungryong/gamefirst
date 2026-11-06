extends "res://chapter1/view/chapter_world_quality31d.gd"
## Chamfer existing rear stones; keep all instance anchors, openings and batches.
var masonry37_faces := 0
const FACES37 := [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]
func _batch22(records: Array[Dictionary],shape: Mesh,label: String) -> void:
 if label=="RearMasonry22":
  var points: Array[Vector3]=[]
  for z in [-.5,.5]:
   for x in [-.5,.5]:
    for y in [-.5,.5]:points.append(Vector3(x,y,z))
  shape=_chamfer37(points,.07)
 super._batch22(records,shape,label)
 var node: MultiMeshInstance3D=root.get_node(NodePath(label))
 var material: StandardMaterial3D=node.material_override
 material.roughness=.93;material.metallic_specular=.20
 for index in node.multimesh.instance_count:
  var color: Color=node.multimesh.get_instance_color(index)
  var grey: float=color.r*.299+color.g*.587+color.b*.114
  node.multimesh.set_instance_color(index,color.lerp(Color(grey,grey,grey,color.a),.35))
func _voussoir22() -> ArrayMesh:
 var angle: float=PI/15.0*.47
 var points: Array[Vector3]=[]
 for z in [-.55,.55]:
  for radius in [3.28,4.12]:
   for a in [-angle,angle]:points.append(Vector3(cos(a)*radius,sin(a)*radius,z))
 return _chamfer37(points,.055)
func _chamfer37(points: Array[Vector3],amount: float) -> ArrayMesh:
 var tool := SurfaceTool.new();tool.begin(Mesh.PRIMITIVE_TRIANGLES)
 var center := Vector3.ZERO
 for point in points:center+=point
 center/=float(points.size())
 var corners: Array=[]
 for index in points.size():corners.append([])
 var edges: Dictionary={}
 for face in FACES37:
  var inset: Dictionary={};var polygon: Array[Vector3]=[]
  for index in face.size():
   var id_: int=face[index]
   var position: Vector3=points[id_]*(1.0-2.0*amount)+points[face[(index+3)%4]]*amount+points[face[(index+1)%4]]*amount
   inset[id_]=position;polygon.append(position);corners[id_].append(position)
  _polygon37(tool,polygon,center)
  for index in face.size():
   var a: int=mini(face[index],face[(index+1)%4]);var b: int=maxi(face[index],face[(index+1)%4])
   var key: String="%d:%d"%[a,b]
   if not edges.has(key):edges[key]=[]
   edges[key].append([inset[a],inset[b]])
 for edge in edges.values():
  assert(edge.size()==2)
  _polygon37(tool,[edge[0][0],edge[0][1],edge[1][1],edge[1][0]],center)
 for corner in corners:
  var polygon: Array[Vector3]=[]
  for point in corner:polygon.append(point)
  _polygon37(tool,polygon,center)
 return tool.commit()
func _polygon37(tool: SurfaceTool,polygon: Array[Vector3],center: Vector3) -> void:
 var middle := Vector3.ZERO
 for point in polygon:middle+=point
 middle/=float(polygon.size())
 var normal: Vector3=(polygon[1]-polygon[0]).cross(polygon[2]-polygon[0]).normalized()
 if normal.dot(middle-center)<0:
  polygon.reverse();normal=-normal
 for index in range(1,polygon.size()-1):
  for at in [0,index+1,index]:
   tool.set_normal(normal);tool.add_vertex(polygon[at])
 masonry37_faces+=1
