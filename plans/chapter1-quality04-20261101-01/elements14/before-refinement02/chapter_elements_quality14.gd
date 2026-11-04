extends "res://chapter1/view/chapter_effects_quality10.gd"
## Cosmetic only: paid cast paths, actual frozen_until, actual shatter events.
const ARC_CAP := 64
const ICE_TARGET_CAP := 24
const ICE_STATE_CAP := 48
const ICE_SHARD_CAP := 128
var arc_links: Array[Dictionary]=[]
var ice_targets: Dictionary={}
var ice_fragments: Array[Dictionary]=[]
var arc_surface: MeshInstance3D
var ice_batch: MultiMeshInstance3D
var ice_fragment_batch: MultiMeshInstance3D
var _arc_mesh := ImmediateMesh.new()
var _element_seq := -1

func setup(owner_view: Node3D) -> void:
	super.setup(owner_view)
	var comet := ShaderMaterial.new();comet.shader=preload("res://chapter1/view/comet_quality14.gdshader");projectiles.material_override=comet
	var impact := ShaderMaterial.new();impact.shader=preload("res://chapter1/view/impact_quality14.gdshader");impacts.material_override=impact
	arc_surface=MeshInstance3D.new();arc_surface.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var ribbon := ShaderMaterial.new();ribbon.shader=preload("res://chapter1/view/arc_quality14.gdshader");arc_surface.material_override=ribbon;view.add_child(arc_surface)
	var crystal := _crystal_mesh()
	ice_batch=_batch(crystal,ICE_TARGET_CAP*4);ice_fragment_batch=_batch(crystal,ICE_SHARD_CAP)
	var ice := StandardMaterial3D.new();ice.vertex_color_use_as_albedo=true;ice.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA_DEPTH_PRE_PASS
	ice.albedo_color=Color(.72,.94,1,.85);ice.metallic=.12;ice.roughness=.24;ice.emission_enabled=true;ice.emission=Color(.10,.37,.50);ice.emission_energy_multiplier=.55
	ice_batch.material_override=ice;ice_fragment_batch.material_override=ice
	print("CHAPTER1_ELEMENTS14 ",JSON.stringify({"arc_links_cap":ARC_CAP,"ice_targets_cap":ICE_TARGET_CAP,"crystals_per_target":4,"ice_shards_cap":ICE_SHARD_CAP,"damage_owner":false,"scope":"Own code geometry/shaders; quality comparison"}))

func consume(events: Array) -> void:
	var shard_budget := 8
	for event in events:
		if int(event.seq)<=_element_seq:continue
		_element_seq=int(event.seq)
		if event.type=="cast" and event.skill_id=="chapter1.skill.arc":
			var from: Vector2=event.position
			for target in event.targets:
				if arc_links.size()<ARC_CAP:arc_links.append({"from":from,"to":target,"age":0.0,"duration":.20,"evolved":bool(event.get("evolved",false)),"seed":int(event.seq)*17+arc_links.size()*13})
				from=target
		elif event.type=="shatter" and shard_budget>0:
			shard_budget-=1
			for i in mini(6,ICE_SHARD_CAP-ice_fragments.size()):
				var angle := float((int(event.seq)*19+i*61)%360)*PI/180.0
				var at: Vector2=event.position
				ice_fragments.append({"position":Vector3(at.x,.62,at.y),"velocity":Vector3(cos(angle)*3.0,2.0+float(i%3)*.6,sin(angle)*3.0),"age":0.0,"duration":.42,"angle":angle,"size":.20+float(i%3)*.06})
	super.consume(events)
	# Replace only the old arc ribbons; retain paid impacts, fire, loot/debris.
	var keep: Array[Dictionary]=[]
	for stroke in strokes:
		if stroke.type!="arc":keep.append(stroke)
	strokes=keep

func sync(run: RefCounted,delta: float) -> void:
	super.sync(run,delta)
	_sync_arcs(run,delta);_sync_ice(run,delta);_sync_fragments(run,delta)

func _sync_arcs(run: RefCounted,delta: float) -> void:
	_arc_mesh.clear_surfaces();_arc_mesh.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	var live: Array[Dictionary]=[];var vertices := 0
	for link in arc_links:
		if run.mode=="playing":link.age+=delta
		if link.age>=link.duration:continue
		live.append(link)
		var progress: float=link.age/link.duration
		var fade := pow(1.0-progress,1.1)
		var from: Vector2=link.from;var to: Vector2=link.to
		var side := Vector2(-(to-from).y,(to-from).x).normalized()
		var amplitude := minf(.28,from.distance_to(to)*.10)
		var width := .15 if link.evolved else .11
		var points: Array[Vector3]=[]
		for i in 10:
			var ratio := float(i)/9.0
			var offset := sin(float(i)*2.73+float(link.seed))*amplitude*sin(ratio*PI)
			var at := from.lerp(to,ratio)+side*offset
			points.append(Vector3(at.x,.90,at.y))
		_arc_mesh.surface_set_color(Color(.40,.65,1,fade))
		for i in 9:vertices+=_arc_quad(points[i],points[i+1],width)
		_arc_mesh.surface_set_color(Color(.28,.45,.82,fade*.45))
		for i in [3,6]:
			var branch := points[i]+Vector3(side.x,.10,side.y)*(.42 if i==3 else -.56)
			vertices+=_arc_quad(points[i],branch,width*.45)
	if vertices==0:
		for i in 3:_arc_mesh.surface_add_vertex(Vector3(0,-20,0))
	_arc_mesh.surface_end();arc_surface.mesh=_arc_mesh;arc_links=live

func _arc_quad(a: Vector3,b: Vector3,width: float) -> int:
	var normal := view.get_viewport().get_camera_3d().global_basis.z
	var side := (b-a).cross(normal).normalized()*width
	var corners := [a-side,a+side,b+side,b-side]
	var uvs := [Vector2(0,0),Vector2(0,1),Vector2(1,1),Vector2(1,0)]
	for i in [0,1,2,0,2,3]:_arc_mesh.surface_set_uv(uvs[i]);_arc_mesh.surface_add_vertex(corners[i])
	return 6

func _sync_ice(run: RefCounted,delta: float) -> void:
	var eligible: Array[Dictionary]=[]
	for e in run.enemies.values():
		if e.hp_raw>0 and run.tick<int(e.frozen_until):eligible.append(e)
	eligible.sort_custom(func(a: Dictionary,b: Dictionary)->bool:
		if bool(a.elite)!=bool(b.elite):return bool(a.elite)
		return a.position.distance_squared_to(run.hero.position)<b.position.distance_squared_to(run.hero.position))
	var wanted := {}
	for i in mini(ICE_TARGET_CAP,eligible.size()):
		var e: Dictionary=eligible[i];var key := "%d:%d"%[e.generation,e.id];wanted[key]=true
		if not ice_targets.has(key):ice_targets[key]={"age":0.0,"strength":0.0,"at":e.position,"elite":bool(e.elite)}
		var record: Dictionary=ice_targets[key];record.at=e.position
		if run.mode=="playing":record.age+=delta
		var remaining := float(int(e.frozen_until)-run.tick)/60.0
		record.strength=minf(clampf(record.age/.10,0,1),clampf(remaining/.10,0,1))
	for key in ice_targets.keys():
		if not wanted.has(key):
			if run.mode=="playing":ice_targets[key].strength=maxf(0,ice_targets[key].strength-delta*10)
			if ice_targets[key].strength<=0:ice_targets.erase(key)
	# During rapid target turnover, keep the batch strictly bounded, with live
	# frozen elites first. Fading stale records never displace a live target.
	var ordered: Array=[]
	for e in eligible:
		var key := "%d:%d"%[e.generation,e.id]
		if wanted.has(key):ordered.append(key)
	for key in ice_targets:
		if not wanted.has(key):ordered.append(key)
	if ice_targets.size()>ICE_STATE_CAP:
		for key in ordered.duplicate():
			if ice_targets.size()<=ICE_STATE_CAP:break
			if not wanted.has(key):ice_targets.erase(key);ordered.erase(key)
	var index := 0
	for key in ordered:
		if index>=ICE_TARGET_CAP*4:break
		var record: Dictionary=ice_targets[key];var strength: float=record.strength
		var big: bool=record.elite
		var size_ := 1.65 if big else 1.0
		for i in 4:
			var angle := float(i)*TAU/4.0+float(key.hash()%31)*.1
			var spread := .38*size_
			var at := Vector3(record.at.x+cos(angle)*spread,.02,record.at.y+sin(angle)*spread)
			var basis := Basis.from_euler(Vector3(sin(angle)*.18,angle,-cos(angle)*.18)).scaled(Vector3(.20,.80+float(i%3)*.23,.20)*size_*maxf(.01,strength))
			ice_batch.multimesh.set_instance_transform(index,Transform3D(basis,at))
			ice_batch.multimesh.set_instance_color(index,Color(.40,.78,1,strength*.72));index+=1
	ice_batch.multimesh.visible_instance_count=index

func _sync_fragments(run: RefCounted,delta: float) -> void:
	var live: Array[Dictionary]=[];var index := 0
	for shard in ice_fragments:
		if run.mode=="playing":shard.age+=delta;shard.position+=shard.velocity*delta;shard.velocity.y-=delta*8
		if shard.age>=shard.duration:continue
		live.append(shard)
		var fade := clampf((float(shard.duration)-float(shard.age))/.16,0,1)
		var basis := Basis.from_euler(Vector3(shard.age*7,shard.angle,shard.age*4)).scaled(Vector3(.55,1,.55)*float(shard.size))
		ice_fragment_batch.multimesh.set_instance_transform(index,Transform3D(basis,shard.position))
		ice_fragment_batch.multimesh.set_instance_color(index,Color(.58,.88,1,fade));index+=1
	ice_fragments=live;ice_fragment_batch.multimesh.visible_instance_count=index

func _crystal_mesh() -> ArrayMesh:
	var vertices := PackedVector3Array();var normals := PackedVector3Array();var colors := PackedColorArray()
	for face in 6:
		var a := Vector3(cos(float(face)*TAU/6.0),.16,sin(float(face)*TAU/6.0))
		var b := Vector3(cos(float(face+1)*TAU/6.0),.16,sin(float(face+1)*TAU/6.0))
		var top := Vector3(.10,1.0,-.08);var base := Vector3(0,0,0)
		for triangle in [[a,b,top],[b,a,base]]:
			var normal: Vector3=(triangle[1]-triangle[0]).cross(triangle[2]-triangle[0]).normalized()
			for point in triangle:vertices.append(point);normals.append(normal);colors.append(Color(.56+float(face%3)*.16,.80+float(face%2)*.12,1))
	var arrays: Array=[];arrays.resize(Mesh.ARRAY_MAX);arrays[Mesh.ARRAY_VERTEX]=vertices;arrays[Mesh.ARRAY_NORMAL]=normals;arrays[Mesh.ARRAY_COLOR]=colors
	var mesh := ArrayMesh.new();mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays);return mesh

func reset() -> void:
	super.reset();arc_links.clear();ice_targets.clear();ice_fragments.clear();_element_seq=-1
	if arc_surface:arc_surface.mesh=null
	if ice_batch:ice_batch.multimesh.visible_instance_count=0
	if ice_fragment_batch:ice_fragment_batch.multimesh.visible_instance_count=0
