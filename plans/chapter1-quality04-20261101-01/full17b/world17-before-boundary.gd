extends "res://chapter1/view/chapter_world_quality10.gd"
## Solid foundations and broken piers outside the central combat lanes.
## Presentation only: no colliders, no changes to walkable cells or core RNG.
var depth_stones := 0
var _stones: Array[Dictionary]=[]
func setup(view: Node3D) -> void:
	super.setup(view)
	for zone in 3:
		for side in [-1,1]:
			for x in [-12,-4,5,13]:
				var at := Vector3(zone*48+x,0,side*(15.5 if zone!=1 else 17.0))
				_stone(at+Vector3(0,.14,0),Vector3(2.1,.28,1.7),Color("42484a"))
				_stone(at+Vector3(0,.38,0),Vector3(1.6,.22,1.3),Color("626762"))
				var height_ := .65+float(posmod(x+zone*3,4))*.26
				_stone(at+Vector3(0,.49+height_*.5,0),Vector3(.68,height_,.68),Color("585e59"))
				_stone(at+Vector3(.10,height_+.57,-.04),Vector3(.94,.16,.86),Color("72756a"))
			for x in [-9,0,9]:
				_stone(Vector3(zone*48+x,.18,side*20),Vector3(5.5,.36,1.1),Color("41484b"))
	art_status.depth_stones=depth_stones
	var column_shape := CylinderMesh.new();column_shape.top_radius=.43;column_shape.bottom_radius=.5;column_shape.height=1;column_shape.radial_segments=8;column_shape.rings=1
	var wall_shape := BoxMesh.new();wall_shape.size=Vector3.ONE
	var mat := StandardMaterial3D.new();mat.albedo_texture=_texture(ART_BASE+"ground_flagstone_v01.png")
	mat.vertex_color_use_as_albedo=true;mat.roughness=.96;mat.uv1_triplanar=true;mat.uv1_world_triplanar=true;mat.uv1_scale=Vector3.ONE*.7
	# Two bounded static batches per zone rather than a draw per stone.
	for zone in 3:
		for wall in [false,true]:
			var records: Array[Dictionary]=[]
			for i in 38:
				var record: Dictionary=_stones[zone*38+i]
				if record.wall==wall:records.append(record)
			var mm := MultiMesh.new();mm.transform_format=MultiMesh.TRANSFORM_3D;mm.use_colors=true;mm.mesh=wall_shape if wall else column_shape;mm.instance_count=records.size()
			for i in records.size():mm.set_instance_transform(i,records[i].transform);mm.set_instance_color(i,records[i].tint)
			var node := MultiMeshInstance3D.new();node.multimesh=mm;node.material_override=mat;root.add_child(node)
func _stone(at: Vector3,dimensions: Vector3,tint: Color) -> void:
	var angle := sin(float(depth_stones)*1.7)*.065
	_stones.append({"transform":Transform3D(Basis(Vector3.UP,angle).scaled(dimensions),at),"tint":Color(tint.r*1.65,tint.g*1.65,tint.b*1.65,1),"wall":dimensions.x>3});depth_stones+=1
