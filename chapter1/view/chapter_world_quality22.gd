extends "res://chapter1/view/chapter_world_quality18.gd"
## Rear cloister masonry has real thickness, openings and cast shadows.
## Every new stone stays north of the legal arena; no collision/core changes.
var masonry22: Array[Dictionary]=[]
func _prop(id_: String,at: Vector3,height: float=0.0,tint: Color=Color.WHITE,mirror: bool=false) -> void:
	if id_=="arch":return
	super._prop(id_,at,height,tint,mirror)
func setup(view: Node3D) -> void:
	super.setup(view)
	# The inherited foundation batch contains both sides. Retain the south
	# foundations; the authored rear colonnade replaces its northern stones.
	for child in root.get_children():
		if not child is MultiMeshInstance3D:continue
		var old: MultiMesh=child.multimesh
		var keep: Array[int]=[]
		for i in old.instance_count:
			if old.get_instance_transform(i).origin.z>0:keep.append(i)
		for i in keep.size():
			old.set_instance_transform(i,old.get_instance_transform(keep[i]))
			old.set_instance_color(i,old.get_instance_color(keep[i]))
		old.visible_instance_count=keep.size()
	var blocks: Array[Dictionary]=[]
	var wedges: Array[Dictionary]=[]
	for zone in 3:
		var center := Vector3(zone*48,3.1,-22.8)
		var tint := Color("7b8279") if zone==0 else (Color("817a76") if zone==1 else Color("78818a"))
		for side in [-1,1]:
			for row in 6:
				var at := center+Vector3(side*3.7,-2.85+row*.5,0)
				_add22(blocks,at,Vector3(.83,.47,1.10),0,tint,zone)
			_add22(blocks,center+Vector3(side*3.7,-3.0,0),Vector3(1.2,.20,1.4),0,tint*.78,zone)
			_add22(blocks,center+Vector3(side*3.7,-.08,0),Vector3(1.12,.25,1.35),0,tint*1.12,zone)
		for segment in 15:
			# Missing voussoirs distinguish a collapsed garden from the nave
			# and the intact sanctuary, instead of repeating one sprite.
			if zone==0 and segment in [6,7,8]:continue
			if zone==1 and segment in [3,4]:continue
			var angle := (float(segment)+.5)*PI/15.0
			var record := {"transform":Transform3D(Basis(Vector3.BACK,angle),center),"tint":tint*(.90+.14*sin(segment*2.3)),"zone":zone}
			wedges.append(record)
		for side in [-1,1]:
			for index in 3:
				var x: float=side*(7.3+index*4.2)
				var height_ := 1.15+float(posmod(zone+index*2,4))*.48
				for row in int(ceil(height_/.46)):
					_add22(blocks,Vector3(zone*48+x,.23+row*.46,-22.5),Vector3(.85,.43,.95),sin(index+row)*.035,tint*.85,zone)
				_add22(blocks,Vector3(zone*48+x,.12,-22.5),Vector3(1.3,.24,1.5),0,tint*.73,zone)
			# Fallen stones lie behind the broken piers, outside walkable ground.
			for index in 4:
				_add22(blocks,Vector3(zone*48+side*(1.8+index*.9),.18,-24.1-index*.30),Vector3(.7,.34,.92),side*(.2+index*.31),tint*.86,zone)
	var box := BoxMesh.new();box.size=Vector3.ONE
	_batch22(blocks,box,"RearMasonry22")
	_batch22(wedges,_voussoir22(),"RearArches22")
	masonry22.append_array(blocks);masonry22.append_array(wedges)
	art_status.rear_masonry22=masonry22.size();art_status.rear_masonry_batches22=2
func _add22(records: Array[Dictionary],at: Vector3,size_: Vector3,angle: float,tint: Color,zone: int) -> void:
	records.append({"transform":Transform3D(Basis(Vector3.UP,angle).scaled(size_),at),"tint":tint,"zone":zone})
func _batch22(records: Array[Dictionary],shape: Mesh,label: String) -> void:
	var mm := MultiMesh.new();mm.transform_format=MultiMesh.TRANSFORM_3D;mm.use_colors=true;mm.mesh=shape;mm.instance_count=records.size()
	for i in records.size():
		mm.set_instance_transform(i,records[i].transform);mm.set_instance_color(i,records[i].tint*1.85)
	var material_ := StandardMaterial3D.new();material_.albedo_texture=_texture(ART_BASE+"ground_flagstone_v01.png")
	material_.vertex_color_use_as_albedo=true;material_.roughness=.97;material_.uv1_triplanar=true;material_.uv1_world_triplanar=true;material_.uv1_scale=Vector3.ONE*.7
	var node := MultiMeshInstance3D.new();node.name=label;node.multimesh=mm;node.material_override=material_;root.add_child(node)
func _voussoir22() -> ArrayMesh:
	var angle := PI/15.0*.47
	var points: Array[Vector3]=[]
	for z in [-.55,.55]:
		for radius in [3.28,4.12]:
			for a in [-angle,angle]:points.append(Vector3(cos(a)*radius,sin(a)*radius,z))
	var surface := SurfaceTool.new();surface.begin(Mesh.PRIMITIVE_TRIANGLES)
	for face in [[0,1,3,2],[4,6,7,5],[0,4,5,1],[2,3,7,6],[0,2,6,4],[1,5,7,3]]:
		var a: Vector3=points[face[0]];var b: Vector3=points[face[1]];var c: Vector3=points[face[2]]
		var normal := (b-a).cross(c-a).normalized()
		# Godot front faces use clockwise winding; retain outward normals.
		for index in [0,2,1,0,3,2]:
			surface.set_normal(normal);surface.add_vertex(points[face[index]])
	return surface.commit()
