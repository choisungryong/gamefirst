extends RefCounted
## A ruined cloister composition. All props are decorative 2.5D art, not collision.
## ArrayMesh follows the documented 4.5 array/UV/color surface pattern:
## https://docs.godotengine.org/en/4.5/classes/class_arraymesh.html
const CAMERA_OFFSET := Vector3(11,19,14)
const ART_BASE := "res://chapter1/art/quality03/"
var root: Node3D
var camera: Camera3D
var art_status: Dictionary={"ground":[],"props":0,"raw_texture_fallbacks":[]}
var _rng := RandomNumberGenerator.new()
var _prop_defs: Dictionary={}
var _prop_texture: Texture2D
var _prop_textures: Dictionary={}
var _prop_entries: Array[Dictionary]=[]
var _prop_materials: Array[ShaderMaterial]=[]
var _warm_lights: Array[OmniLight3D]=[]
var _warm_base: Array[float]=[]
var _age := 0.0
var _camera_trauma := 0.0
var _reduced_motion := false
var _camera_base := CAMERA_OFFSET

func material(color: Color, emission: float=0.0) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.albedo_color=color;mat.roughness=.96
	if emission>0:
		mat.emission_enabled=true;mat.emission=color;mat.emission_energy_multiplier=emission
	return mat

func setup(view: Node3D) -> void:
	_rng.seed=730113
	root=Node3D.new();root.name="CloisterWorldQuality03";view.add_child(root)
	var environment := Environment.new()
	environment.background_mode=Environment.BG_COLOR
	environment.background_color=Color("0e141a")
	environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color=Color("8594a6")
	environment.ambient_light_energy=.34
	environment.tonemap_mode=Environment.TONE_MAPPER_FILMIC
	environment.glow_enabled=true;environment.glow_intensity=.45;environment.glow_bloom=.13
	environment.fog_enabled=true;environment.fog_light_color=Color("162027");environment.fog_density=.0025
	var environment_node := WorldEnvironment.new();environment_node.environment=environment;view.add_child(environment_node)
	var moon := DirectionalLight3D.new()
	moon.rotation_degrees=Vector3(-54,-34,0);moon.light_color=Color("b7c5d7");moon.light_energy=.88
	# There are no solid 3D casters in this decorative impostor scene. Actors use
	# their bounded contact-shadow batch; props retain their authored shading.
	moon.shadow_enabled=false;view.add_child(moon)
	var floor_mesh := PlaneMesh.new();floor_mesh.size=Vector2(82,82)
	var floor_node := MeshInstance3D.new();floor_node.mesh=floor_mesh;floor_node.position.y=-.05
	floor_node.material_override=_ground_material();floor_node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	root.add_child(floor_node)
	_load_props()
	_compose_cloister()
	_bake_props()
	_bake_contact_shadows()
	camera=Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=24.0
	view.add_child(camera);camera.position=CAMERA_OFFSET;camera.look_at(Vector3.ZERO);camera.current=true
	print("CHAPTER1_WORLD_ART ",JSON.stringify(art_status))

func _texture(path: String) -> Texture2D:
	var result: Texture2D
	if ResourceLoader.exists(path,"Texture2D"):result=ResourceLoader.load(path,"Texture2D") as Texture2D
	if result==null and FileAccess.file_exists(path):
		var source := Image.load_from_file(ProjectSettings.globalize_path(path))
		if source:
			result=ImageTexture.create_from_image(source)
			art_status.raw_texture_fallbacks.append(path)
	if result:
		var image := result.get_image()
		if image and not image.has_mipmaps():
			if image.is_compressed():image.decompress()
			image.generate_mipmaps();result=ImageTexture.create_from_image(image)
	return result

func _ground_material() -> Material:
	var mat := ShaderMaterial.new();mat.shader=load("res://chapter1/view/cloister_ground_quality03.gdshader")
	for pair in [["flagstone","ground_flagstone_v01.png"],["soil","ground_soil_v01.png"]]:
		var texture := _texture(ART_BASE+pair[1])
		if texture:
			mat.set_shader_parameter(pair[0],texture);mat.set_shader_parameter("has_"+pair[0],true)
			art_status.ground.append(pair[1])
	return mat

func _load_props() -> void:
	_load_prop_doc(ART_BASE+"cloister_props_v01.json")
	_load_prop_doc(ART_BASE+"cloister_foliage_v01.json")

func _load_prop_doc(path: String) -> void:
	if not FileAccess.file_exists(path):return
	var doc: Variant=JSON.parse_string(FileAccess.get_file_as_string(path))
	if not doc is Dictionary:return
	var texture_path := String(doc.get("texture",ART_BASE+"cloister_props_v01.png"))
	var texture := _texture(texture_path)
	if texture==null:return
	if _prop_texture==null:_prop_texture=texture
	_prop_textures[texture_path]=texture
	for prop in doc.get("props",[]):
		if prop is Dictionary and prop.has("id") and prop.has("region") and prop.has("feet"):
			prop._atlas=texture_path;_prop_defs[String(prop.id)]=prop

func _prop(id_: String, at: Vector3, height: float=0.0, tint: Color=Color.WHITE, mirror: bool=false) -> void:
	if not _prop_defs.has(id_):return
	var record: Dictionary=_prop_defs[id_]
	_prop_entries.append({"id":id_,"at":at,"height":height if height>0 else float(record.get("height_m",1.0)),"tint":tint,"mirror":mirror})

func _compose_cloister() -> void:
	art_status.composition_revision="verge-ribbons-20261101-01"
	art_status.court_half_extents=[6.5,8.0]
	# The solid-looking architecture stays outside the ±19m combat square.
	# Its perspective is authored into the PNG; no invisible collision is implied.
	_prop("arch",Vector3(0,0,-21.6),6.2,Color(.75,.82,.9))
	for side in [-1.0,1.0]:
		for z in [-20.0,-11.0,-2.0,7.0,16.0,25.0]:
			_prop("pillar_whole" if int(z)%2==0 else "pillar_broken",Vector3(side*20.4,0,z),3.4,Color(.73,.79,.85),side<0)
			_prop("wall",Vector3(side*21.0,0,z+3.3),2.2,Color(.65,.72,.79),side<0)
		for z in [-17.0,-9.0,2.0,13.0,21.0]:
			_prop("grave_cross" if z<1 else "grave_slab",Vector3(side*19.9,0,z),1.35,Color(.72,.77,.79),side>0)
		_prop("tree",Vector3(side*26,0,-18),5.8,Color(.65,.71,.75),side<0)
		_prop("tree",Vector3(side*25,0,23),5.0,Color(.65,.71,.75),side>0)
		for z in [-14.0,2.0,18.0]:_brazier(Vector3(side*19.7,0,z))
	_compose_verges()
	for at in [Vector3(-15,0,-7),Vector3(14,0,10),Vector3(9,0,-17),Vector3(-16,0,15)]:
		_prop("roots",at,.42,Color(.65,.70,.67))
		_prop("rubble",at+Vector3(1.1,.005,.7),.28,Color(.75,.78,.78),true)

func _paving_distance(at: Vector2) -> float:
	# Match the three authored ground regions; keep the central paths open.
	var court := maxf(absf(at.x)-6.5,absf(at.y+1.0)-8.0)
	var nave := absf(at.x+sin(at.y*.16)*.45)-3.45
	var crossing := absf(at.y+2.0+sin(at.x*.14)*.3)-2.95
	return minf(court,minf(nave,crossing))

func _compose_verges() -> void:
	# Jittered ribbons grow from the paving edges instead of isolated green balls.
	# One clump per lattice cell bounds fill and keeps broad soil gaps between beds.
	var green_ids: Array[String]=[]
	for id_ in _prop_defs:
		if _prop_defs[id_]._atlas.ends_with("cloister_foliage_v01.png"):green_ids.append(id_)
	if green_ids.is_empty():return
	var candidates: Array[Dictionary]=[]
	for gx in range(-28,29):
		for gz in range(-28,29):
			var at := Vector2(float(gx)*.88+_rng.randf_range(-.11,.11),float(gz)*.88+_rng.randf_range(-.11,.11))
			var distance_ := _paving_distance(at)
			if distance_<.32 or distance_>5.0:continue
			# Broad winding gaps avoid a ruler-straight hedge around the court.
			var gap := sin(at.x*.42+at.y*.17)+cos(at.y*.57-at.x*.13)
			if gap<-.95 and distance_>1.45:continue
			candidates.append({"at":at,"priority":_rng.randf()+distance_*.075})
	candidates.sort_custom(func(a: Dictionary,b: Dictionary) -> bool:return a.priority<b.priority)
	var count := mini(620,candidates.size())
	for i in count:
		var at: Vector2=candidates[i].at
		var id_: String=green_ids[i%green_ids.size()]
		var height := _rng.randf_range(.63,.96)
		var shade := _rng.randf_range(.88,1.07)
		# Ferns and grasses share subdued olive values, not neon shrub highlights.
		_prop(id_,Vector3(at.x,.008,at.y),height,Color(.55,.63,.54)*shade,i%2==0)
	art_status.foliage_quads=count
	art_status.verge_candidates=candidates.size()

func _brazier(at: Vector3) -> void:
	_prop("brazier",at,2.0,Color(.88,.8,.67))
	var light := OmniLight3D.new();light.position=at+Vector3.UP*1.5
	light.light_color=Color("ffad66");light.light_energy=2.8;light.omni_range=7.0;light.shadow_enabled=false
	root.add_child(light);_warm_lights.append(light);_warm_base.append(2.8)

func _bake_props() -> void:
	if _prop_texture==null or _prop_entries.is_empty():return
	var surfaces := 0
	for path in _prop_textures:
		var group: Array[Dictionary]=[]
		for entry in _prop_entries:
			if _prop_defs[entry.id]._atlas==path:group.append(entry)
		if group.is_empty():continue
		_bake_prop_surface(group,_prop_textures[path],"AuthoredCloisterProps" if surfaces==0 else "AuthoredCloisterFoliage")
		surfaces+=1
	art_status.props=_prop_entries.size();art_status.prop_surfaces=surfaces;art_status.prop_types=_prop_defs.keys()

func _bake_prop_surface(entries: Array[Dictionary], texture: Texture2D, label: String) -> void:
	var verts := PackedVector3Array();var uvs := PackedVector2Array();var colors := PackedColorArray()
	var forward := CAMERA_OFFSET.normalized()
	var right := Vector3.UP.cross(forward).normalized()
	var up := forward.cross(right).normalized()
	var texture_size := Vector2(texture.get_width(),texture.get_height())
	for entry in entries:
		var record: Dictionary=_prop_defs[entry.id]
		var region: Array=record.region;var feet: Array=record.feet
		var scale_: float=float(entry.height)/float(region[3])
		var width: float=float(region[2])*scale_
		var left: float=-float(feet[0])*scale_;var bottom: float=-(float(region[3])-float(feet[1]))*scale_
		if entry.mirror:left=-width-left
		var corners := [entry.at+right*left+up*bottom,entry.at+right*(left+width)+up*bottom,entry.at+right*(left+width)+up*(bottom+float(entry.height)),entry.at+right*left+up*(bottom+float(entry.height))]
		var uv_min := (Vector2(region[0],region[1])+Vector2.ONE*.5)/texture_size
		var uv_max := (Vector2(region[0]+region[2],region[1]+region[3])-Vector2.ONE*.5)/texture_size
		var u0: float=uv_max.x if entry.mirror else uv_min.x
		var u1: float=uv_min.x if entry.mirror else uv_max.x
		var texcoords := [Vector2(u0,uv_max.y),Vector2(u1,uv_max.y),Vector2(u1,uv_min.y),Vector2(u0,uv_min.y)]
		for index in [0,1,2,0,2,3]:
			var tint: Color=entry.tint
			tint.a=1.0 if float(entry.height)>1.0 else 0.0
			verts.append(corners[index]);uvs.append(texcoords[index]);colors.append(tint)
	var arrays: Array=[];arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX]=verts;arrays[Mesh.ARRAY_TEX_UV]=uvs;arrays[Mesh.ARRAY_COLOR]=colors
	var shape := ArrayMesh.new();shape.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	var mat := ShaderMaterial.new();mat.shader=load("res://chapter1/view/cloister_props_quality03.gdshader");mat.set_shader_parameter("atlas_texture",texture)
	_prop_materials.append(mat)
	var node := MeshInstance3D.new();node.name=label;node.mesh=shape;node.material_override=mat
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF;root.add_child(node)

func _bake_contact_shadows() -> void:
	if _prop_entries.is_empty():return
	var verts := PackedVector3Array();var uvs := PackedVector2Array();var colors := PackedColorArray()
	for entry in _prop_entries:
		var record: Dictionary=_prop_defs[entry.id]
		var width: float=float(record.region[2])/float(record.region[3])*float(entry.height)
		var sx := clampf(width*.42,.16,1.4)
		var sz := clampf(float(entry.height)*.12,.12,.66)
		var at: Vector3=entry.at;at.y=.001
		var corners := [at+Vector3(-sx,0,-sz),at+Vector3(sx,0,-sz),at+Vector3(sx,0,sz),at+Vector3(-sx,0,sz)]
		var coordinates := [Vector2.ZERO,Vector2.RIGHT,Vector2.ONE,Vector2.DOWN]
		for index in [0,1,2,0,2,3]:
			verts.append(corners[index]);uvs.append(coordinates[index]);colors.append(Color(1,1,1,.38 if entry.height>1 else .2))
	var arrays: Array=[];arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX]=verts;arrays[Mesh.ARRAY_TEX_UV]=uvs;arrays[Mesh.ARRAY_COLOR]=colors
	var shape := ArrayMesh.new();shape.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	var node := MeshInstance3D.new();node.name="CloisterPropContactShadows";node.mesh=shape
	var mat := ShaderMaterial.new();mat.shader=load("res://chapter1/view/cloister_contact_quality03.gdshader");node.material_override=mat
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF;root.add_child(node)
	art_status.contact_shadows=_prop_entries.size()

func kick_camera(strength: float) -> void:
	if not _reduced_motion:_camera_trauma=minf(.9,_camera_trauma+clampf(strength,0,1)*.35)

func set_reduced_motion(value: bool) -> void:
	_reduced_motion=value
	if value:_camera_trauma=0

func update_camera(hero: Vector2, delta: float) -> void:
	_age+=delta
	_camera_trauma=maxf(0,_camera_trauma-delta*5)
	var target := Vector3(hero.x,0,hero.y)
	for mat in _prop_materials:mat.set_shader_parameter("hero_position",Vector2(hero.x,hero.y))
	var desired := target+CAMERA_OFFSET
	# Derive an unshaken base from the target; feedback never accumulates drift.
	_camera_base=_camera_base.lerp(desired,1.0-exp(-delta*8.0))
	var base: Vector3=_camera_base
	var displacement := Vector3(sin(_age*79.0),0,cos(_age*67.0))*.045*_camera_trauma
	camera.position=base+displacement;camera.look_at(base-CAMERA_OFFSET+displacement)
	for i in _warm_lights.size():
		_warm_lights[i].light_energy=_warm_base[i]*(.96+sin(_age*4.7+float(i)*2.1)*.025)
