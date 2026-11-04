extends "res://chapter1/view/chapter_world.gd"
## Independent geometric grasses: narrow tapered blades, open paving and quiet values.
## Decorative only; all Chapter09 collision and objectives stay in the core.
var _grass_material: ShaderMaterial
var _grass_vertices := PackedVector3Array()
var _grass_normals := PackedVector3Array()
var _grass_colors := PackedColorArray()
var _grass_uv := PackedVector2Array()
var _grass_blades := 0

func setup(view: Node3D) -> void:
	super.setup(view)
	_bake_grass()
	for child in view.get_children():
		if child is DirectionalLight3D:child.shadow_enabled=true;child.light_cull_mask=3

func _ground_material() -> Material:
	var mat := ShaderMaterial.new();mat.shader=preload("res://chapter1/view/chapter_ground_quality10.gdshader")
	for pair in [["flagstone","ground_flagstone_v01.png"],["soil","ground_soil_v01.png"]]:
		var texture := _texture(ART_BASE+pair[1])
		if texture:mat.set_shader_parameter(pair[0],texture);mat.set_shader_parameter("has_"+pair[0],true);art_status.ground.append(pair[1])
	return mat

func _prop(id_: String,at: Vector3,height: float=0.0,tint: Color=Color.WHITE,mirror: bool=false) -> void:
	if _prop_defs.has(id_) and String(_prop_defs[id_]._atlas).ends_with("cloister_foliage_v01.png"):return
	super._prop(id_,at,height,tint,mirror)

func _compose_verges() -> void:
	var patches := 0
	for zone in 3:
		var candidates: Array[Dictionary]=[]
		for gx in range(-24,25):
			for gz in range(-24,25):
				var local := Vector2(gx*.93+_rng.randf_range(-.27,.27),gz*.93+_rng.randf_range(-.27,.27))
				var distance_ := _paving_distance(local)
				if zone==1:distance_=maxf(absf(local.x)-12.8,absf(local.y)-15.0)
				elif zone==2:distance_=local.length()-17.8
				if distance_<.45 or distance_>4.2:continue
				# Keep both horizontal passages and the breathing gaps between beds.
				if absf(local.y)<4.0 or sin(local.x*.47+local.y*.15)+cos(local.y*.51-local.x*.13)<-.75:continue
				candidates.append({"at":local+Vector2(zone*48,0),"priority":_rng.randf()+distance_*.08})
		candidates.sort_custom(func(a: Dictionary,b: Dictionary)->bool:return a.priority<b.priority)
		var limit := mini([330,125,90][zone],candidates.size())
		for i in limit:
			var center: Vector2=candidates[i].at
			var patch_height := _rng.randf_range(.50,.95) if zone==0 else _rng.randf_range(.32,.67)
			var tint := Color("5c6544") if zone==0 else (Color("615e43") if zone==1 else Color("515858"))
			for blade in _rng.randi_range(16,26):
				var angle := _rng.randf_range(0,TAU)
				var spread := sqrt(_rng.randf())*.38
				var foot := Vector3(center.x+cos(angle)*spread,.0,center.y+sin(angle)*spread*.72)
				_blade(foot,patch_height*_rng.randf_range(.48,1.14),_rng.randf_range(.022,.046),_rng.randf_range(0,TAU),tint*_rng.randf_range(.68,1.12))
			patches+=1
	art_status.foliage_quads=0;art_status.grass_patches=patches;art_status.grass_blades=_grass_blades
	art_status.composition_revision="full-chapter-tapered-grass-10"

func _blade(foot: Vector3,height: float,width: float,angle: float,tint: Color) -> void:
	var right := Vector3(cos(angle),0,sin(angle))
	var bend := Vector3(-sin(angle),0,cos(angle))*_rng.randf_range(.11,.32)
	for step in 3:
		var a := float(step)/3.0;var b := float(step+1)/3.0
		var p0 := foot+Vector3.UP*height*a+bend*a*a
		var p1 := foot+Vector3.UP*height*b+bend*b*b
		var wa := width*(1.0-a)*(.8+.4*sin(a*PI))
		var wb := width*(1.0-b)*(.8+.4*sin(b*PI))
		var corners := [p0-right*wa,p0+right*wa,p1+right*wb,p1-right*wb]
		var normal := right.cross((p1-p0).normalized()).normalized()
		for k in [0,1,2,0,2,3]:
			var t := a if k<2 else b
			_grass_vertices.append(corners[k]);_grass_normals.append(normal)
			_grass_colors.append((tint*lerpf(.48,1.06,t)).srgb_to_linear());_grass_uv.append(Vector2(0,t))
	_grass_blades+=1

func _bake_grass() -> void:
	if _grass_vertices.is_empty():return
	var arrays: Array=[];arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX]=_grass_vertices;arrays[Mesh.ARRAY_NORMAL]=_grass_normals;arrays[Mesh.ARRAY_COLOR]=_grass_colors;arrays[Mesh.ARRAY_TEX_UV]=_grass_uv
	var mesh := ArrayMesh.new();mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	_grass_material=ShaderMaterial.new();_grass_material.shader=preload("res://chapter1/view/chapter_grass_quality10.gdshader")
	var node := MeshInstance3D.new();node.name="TaperedGrass";node.mesh=mesh;node.material_override=_grass_material;node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF;root.add_child(node)
	_grass_vertices.clear();_grass_normals.clear();_grass_colors.clear();_grass_uv.clear()
	print("CHAPTER1_GRASS_ART ",JSON.stringify({"patches":art_status.grass_patches,"blades":_grass_blades,"surfaces":1,"collision":false,"source":"independent code geometry"}))

func update_camera(hero: Vector2,delta: float) -> void:
	super.update_camera(hero,delta)
	if _grass_material:_grass_material.set_shader_parameter("age",_age)
