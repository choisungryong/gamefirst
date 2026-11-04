extends Node3D
## Original modeled staff: tapered crooked wood, bronze bands/claws, cut crystal.
## Geometry only; no original-game assets or image-derived mesh are used.
var gem_material: StandardMaterial3D
var _wood_vertices := PackedVector3Array()
var _wood_normals := PackedVector3Array()
var _wood_colors := PackedColorArray()
var _wood_indices := PackedInt32Array()
var _metal_vertices := PackedVector3Array()
var _metal_normals := PackedVector3Array()
var _metal_colors := PackedColorArray()
var _metal_indices := PackedInt32Array()

func _ready() -> void:
	var path: Array[Vector3]=[];var radii: Array[float]=[]
	for i in 33:
		var t := float(i)/32;var y := lerpf(-1.05,1.13,t)
		path.append(Vector3(sin(t*5.8)*.025,y,cos(t*6.2)*.019));radii.append(lerpf(.017,.034,t))
	_tube(path,radii,false,0)
	for i in 9:
		var y := -.19+i*.042
		_band(y,.041,.009,false,Color("5b3e2b"))
	for y in [-.94,-.22,.18,.86,1.02]:_band(y,.043,.012,true,Color("9c7242"))
	for arm in 3:
		path=[];radii=[]
		var a := TAU*float(arm)/3
		for i in 17:
			var t := float(i)/16
			var radius := .025+.12*sin(PI*t)
			path.append(Vector3(cos(a+t*.65)*radius,.93+t*.42,sin(a+t*.65)*radius));radii.append(lerpf(.022,.006,t))
		_tube(path,radii,true,arm)
	var wood := _surface(_wood_vertices,_wood_normals,_wood_colors,_wood_indices,Color.WHITE,0,.87)
	var metal := _surface(_metal_vertices,_metal_normals,_metal_colors,_metal_indices,Color.WHITE,.72,.35)
	wood.name="CrookedAshWood";metal.name="BronzeBindingsAndClaws"
	_gem()

func _band(y: float,radius: float,thickness: float,metal: bool,color: Color) -> void:
	var points: Array[Vector3]=[];var radii: Array[float]=[]
	for i in 17:
		var a := TAU*i/16.0;points.append(Vector3(cos(a)*radius,y,sin(a)*radius));radii.append(thickness)
	_tube(points,radii,metal,0,color)

func _tube(points: Array[Vector3],radii: Array[float],metal: bool,seed_: int,color: Color=Color("61452e")) -> void:
	var vertices := _metal_vertices if metal else _wood_vertices
	var normals := _metal_normals if metal else _wood_normals
	var colors := _metal_colors if metal else _wood_colors
	var indices := _metal_indices if metal else _wood_indices
	var offset := vertices.size();var segments := 10
	for i in points.size():
		var tangent := (points[mini(i+1,points.size()-1)]-points[maxi(i-1,0)]).normalized()
		var side := tangent.cross(Vector3.RIGHT if absf(tangent.dot(Vector3.UP))>.9 else Vector3.UP).normalized()
		var across := tangent.cross(side).normalized()
		for j in segments:
			var angle := TAU*j/segments;var normal := side*cos(angle)+across*sin(angle)
			var grain := 1.0 if metal else .84+.16*sin(j*3.7+i*.51+seed_)
			vertices.append(points[i]+normal*radii[i]*(1 if metal else .94+.06*sin(i*.71+j)))
			normals.append(normal);colors.append((Color("b78b53") if metal else color)*grain)
			if i>0:
				var a := offset+(i-1)*segments+j;var b := offset+(i-1)*segments+(j+1)%segments;var c := offset+i*segments+j;var d := offset+i*segments+(j+1)%segments
				for index in [a,b,c,b,d,c]:indices.append(index)
	if metal:_metal_vertices=vertices;_metal_normals=normals;_metal_colors=colors;_metal_indices=indices
	else:_wood_vertices=vertices;_wood_normals=normals;_wood_colors=colors;_wood_indices=indices

func _surface(vertices: PackedVector3Array,normals: PackedVector3Array,colors: PackedColorArray,indices: PackedInt32Array,color: Color,metallic: float,roughness: float) -> MeshInstance3D:
	var arrays := [];arrays.resize(Mesh.ARRAY_MAX);arrays[Mesh.ARRAY_VERTEX]=vertices;arrays[Mesh.ARRAY_NORMAL]=normals;arrays[Mesh.ARRAY_COLOR]=colors
	if not indices.is_empty():arrays[Mesh.ARRAY_INDEX]=indices
	var mesh := ArrayMesh.new();mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	var node := MeshInstance3D.new();node.mesh=mesh;node.layers=2
	var mat := StandardMaterial3D.new();mat.albedo_color=color;mat.vertex_color_use_as_albedo=true;mat.metallic=metallic;mat.roughness=roughness;mat.cull_mode=BaseMaterial3D.CULL_DISABLED
	node.material_override=mat;add_child(node);return node

func _gem() -> void:
	var points := [Vector3(0,1.40,0),Vector3(.105,1.21,0),Vector3(0,1.21,.105),Vector3(-.105,1.21,0),Vector3(0,1.21,-.105),Vector3(0,1.05,0)]
	var vertices := PackedVector3Array();var normals := PackedVector3Array()
	for i in 4:
		for triangle in [[0,(i+1)%4+1,i+1],[5,i+1,(i+1)%4+1]]:
			var a: Vector3=points[triangle[0]];var b: Vector3=points[triangle[1]];var c: Vector3=points[triangle[2]];var n := (b-a).cross(c-a).normalized()
			for p in [a,b,c]:vertices.append(p);normals.append(n)
	var colors := PackedColorArray()
	for i in vertices.size():colors.append(Color.WHITE)
	var node := _surface(vertices,normals,colors,PackedInt32Array(),Color("b9dae1"),.15,.18)
	gem_material=node.material_override;gem_material.emission_enabled=true;gem_material.emission=Color("66c7eb");gem_material.emission_energy_multiplier=.65

func set_element(color: Color,release_strength: float) -> void:
	if gem_material==null:return
	gem_material.albedo_color=color.lightened(.3);gem_material.emission=color;gem_material.emission_energy_multiplier=.65+release_strength*2.3
