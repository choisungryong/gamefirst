extends RefCounted
## Bounded event-driven mesh/shard presentation; never owns damage.
var view: Node3D
var projectiles: MultiMeshInstance3D
var gems: MultiMeshInstance3D
var shards: MultiMeshInstance3D
var impacts: MultiMeshInstance3D
var plumes: MultiMeshInstance3D
var shadows: MultiMeshInstance3D
var telegraph: MeshInstance3D
var telegraph_fill: MeshInstance3D
var beams: MeshInstance3D
var debris: Array[Dictionary]=[]
var item_nodes: Dictionary={}
var strokes: Array[Dictionary]=[]
var _last_event := -1
var _rng := RandomNumberGenerator.new()
var _line_mesh := ImmediateMesh.new()
var _fill_mesh := ImmediateMesh.new()
var _beam_mesh := ImmediateMesh.new()
var _last_camera_tick := -100
const MAX_PARTICLES := 960
const MAX_STROKES := 96
const MAX_IMPACTS := 48
const MAX_HIT_ACCENTS_PER_CONSUME := 12
const COLORS={"chapter1.skill.ember":Color("ff943d"),"chapter1.skill.frost":Color("9ce7ef"),"chapter1.skill.arc":Color("b9caff")}

func setup(owner_view: Node3D) -> void:
	view=owner_view
	_rng.seed=97631
	var bolt := QuadMesh.new()
	bolt.size=Vector2(2.3,.82)
	projectiles=_batch(bolt,384)
	var comet := ShaderMaterial.new()
	comet.shader=preload("res://chapter1/view/comet.gdshader")
	projectiles.material_override=comet
	var gem := PrismMesh.new()
	gem.size=Vector3(.10,.16,.10)
	gems=_batch(gem,400)
	var gem_mat := _glow(Color.WHITE,0)
	gems.material_override=gem_mat
	var fragment := PrismMesh.new()
	fragment.size=Vector3(.06,.16,.035)
	shards=_batch(fragment,MAX_PARTICLES)
	var particle_mat := ShaderMaterial.new();particle_mat.shader=preload("res://chapter1/view/element_particle.gdshader")
	shards.material_override=particle_mat
	var impact := PlaneMesh.new();impact.size=Vector2(2,2)
	impacts=_batch(impact,MAX_IMPACTS)
	var impact_material := ShaderMaterial.new();impact_material.shader=preload("res://chapter1/view/impact.gdshader")
	impacts.material_override=impact_material
	var bloom := QuadMesh.new();bloom.size=Vector2(2,2.3)
	plumes=_batch(bloom,MAX_IMPACTS)
	var bloom_mat := ShaderMaterial.new();bloom_mat.shader=preload("res://chapter1/view/flame_bloom.gdshader")
	plumes.material_override=bloom_mat
	var shadow_plane := PlaneMesh.new();shadow_plane.size=Vector2(1.1,.75)
	shadows=_batch(shadow_plane,513)
	var shadow_material := ShaderMaterial.new();shadow_material.shader=preload("res://chapter1/view/foot_shadow.gdshader")
	shadows.material_override=shadow_material
	telegraph=MeshInstance3D.new()
	var line_mat := _glow(Color.WHITE,0)
	line_mat.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA
	telegraph.material_override=line_mat
	view.add_child(telegraph)
	telegraph_fill=MeshInstance3D.new()
	var warning := _glow(Color.WHITE,0)
	warning.transparency=BaseMaterial3D.TRANSPARENCY_ALPHA;warning.no_depth_test=false
	telegraph_fill.material_override=warning
	view.add_child(telegraph_fill)
	beams=MeshInstance3D.new()
	beams.material_override=particle_mat
	view.add_child(beams)

func _glow(color: Color, emission: float=1) -> StandardMaterial3D:
	var mat := StandardMaterial3D.new()
	mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
	mat.albedo_color=color
	mat.emission_enabled=emission>0
	mat.emission=color
	mat.emission_energy_multiplier=emission
	mat.vertex_color_use_as_albedo=true
	return mat

func _batch(shape: Mesh, capacity: int) -> MultiMeshInstance3D:
	var mm := MultiMesh.new()
	mm.transform_format=MultiMesh.TRANSFORM_3D
	mm.use_colors=true
	mm.use_custom_data=true
	mm.mesh=shape
	mm.instance_count=capacity
	mm.visible_instance_count=0
	var node := MultiMeshInstance3D.new()
	node.multimesh=mm
	node.material_override=_glow(Color.WHITE,1.1)
	node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	view.add_child(node)
	return node

func burst(at: Vector2, color: Color, count: int, force: float=1) -> void:
	for i in mini(count,MAX_PARTICLES-debris.size()):
		var direction := Vector3(_rng.randf_range(-1,1),_rng.randf_range(.2,1.3),_rng.randf_range(-1,1)).normalized()
		debris.append({"p":Vector3(at.x,.6,at.y),"v":direction*_rng.randf_range(1.5,4)*force,"life":_rng.randf_range(.16,.45),"color":color,"size":_rng.randf_range(.65,1.4)})

func move_marker(at: Vector2) -> void:
	if strokes.size()<96:strokes.append({"type":"ring","at":at,"radius":.32,"life":.35,"color":Color("9bbcb0")})

func consume(events: Array) -> void:
	var impact_budget := 8
	var hit_budget := MAX_HIT_ACCENTS_PER_CONSUME
	for event in events:
		if int(event.seq)<=_last_event: continue
		_last_event=int(event.seq)
		var color: Color=COLORS.get(event.get("skill_id",""),Color("e0c69d"))
		match String(event.type):
			"hit":
				burst(event.position,color,3 if not event.get("shatter",false) else 14)
				if hit_budget>0 and strokes.size()<MAX_STROKES:
					hit_budget-=1
					# A small .1s accent at the paid hit, never a screen-wide flash.
					strokes.append({"type":"hit","at":event.position,"life":.10,"duration":.10,"element":_element(event.get("skill_id","")),"color":color})
			"explosion","shatter":
				burst(event.position,color,16 if event.type=="explosion" else 30,1.35)
				if impact_budget>0 and strokes.size()<MAX_STROKES:
					impact_budget-=1
					strokes.append({"type":"impact","at":event.position,"radius":float(event.radius_cm)/100.0,"life":.48,"duration":.48,"element":_element(event.skill_id),"color":color})
				if event.get("evolved",false):_kick(.15,int(event.tick))
			"death": burst(event.position,color,7,1.2)
			"hero_hit":
				burst(event.position,Color("b94b26"),12,.8)
				_kick(.50,int(event.tick))
			"growth": burst(event.position,Color("d4bd7a"),38,1.5)
			"item_pickup": burst(event.position,Color("e2c17e"),12)
			"cast":
				if event.skill_id=="chapter1.skill.arc":
					var from: Vector2=event.position
					for target in event.targets:
						if strokes.size()<MAX_STROKES:strokes.append({"type":"arc","from":from,"to":target,"life":.18,"duration":.18,"color":color,"width":.065 if event.get("evolved",false) else .04})
						for i in 7:
							var at: Vector2=from.lerp(target,float(i)/7.0)
							if debris.size()<MAX_PARTICLES:debris.append({"p":Vector3(at.x,.8,at.y),"v":Vector3.ZERO,"life":.13,"color":color,"size":1.5})
						from=target
				else: burst(event.position,color,5,.6)

func _element(id_: String) -> float:
	return .5 if id_=="chapter1.skill.frost" else (1.0 if id_=="chapter1.skill.arc" else 0.0)

func _kick(strength: float, tick: int) -> void:
	if tick-_last_camera_tick<14:return
	_last_camera_tick=tick
	var camera_world: Variant=view.get("world")
	if camera_world!=null and camera_world.has_method("kick_camera"):camera_world.kick_camera(strength)

func sync(run: RefCounted, delta: float) -> void:
	# Actor interpolation must carry its contact shadow with it. Gameplay and
	# telegraphs still read paid core coordinates; only contact shading follows
	# the visual transform produced immediately before this presenter is synced.
	var actor_view: Variant=view.get("actors")
	var hero_at := Vector3(run.hero.position.x,.006,run.hero.position.y)
	if actor_view!=null:hero_at=actor_view.hero.position;hero_at.y=.006
	shadows.multimesh.set_instance_transform(0,Transform3D(Basis.IDENTITY,hero_at))
	var shadow_count := 1
	for e in run.enemies.values():
		if e.hp_raw<=0 or shadow_count>=513:continue
		var size_ := 1.5 if e.elite else 1.0
		var at := Vector3(e.position.x,.005,e.position.y)
		var key: String="%d:%d" % [e.generation,e.id]
		if actor_view!=null and actor_view.actors.has(key):at=actor_view.actors[key].position;at.y=.005
		shadows.multimesh.set_instance_transform(shadow_count,Transform3D(Basis.IDENTITY.scaled(Vector3(size_,1,size_)),at))
		shadow_count+=1
	shadows.multimesh.visible_instance_count=shadow_count
	var mm: MultiMesh=projectiles.multimesh
	var index := 0
	var camera := view.get_viewport().get_camera_3d()
	var right := Vector2(camera.global_basis.x.x,camera.global_basis.x.z).normalized()
	var forward := Vector2(-camera.global_basis.z.x,-camera.global_basis.z.z).normalized()
	for p in run.projectiles:
		if index>=mm.instance_count: break
		var color: Color=Color("b94123") if p.hostile else COLORS.get(p.skill_id,Color.WHITE)
		var angle := atan2(p.direction.dot(forward),p.direction.dot(right))
		# Radius is immutable paid projectile data; current rank/gear is never reread.
		var evolved: bool=not p.hostile and float(p.radius)>.20
		var size_ := .68 if p.hostile else (1.28 if evolved else 1.0)
		mm.set_instance_transform(index,Transform3D(Basis.IDENTITY.scaled(Vector3.ONE*size_),Vector3(p.position.x,.75,p.position.y)))
		mm.set_instance_color(index,color)
		mm.set_instance_custom_data(index,Color((angle+PI)/TAU,.5 if p.skill_id=="chapter1.skill.frost" else (1.0 if p.hostile else 0.0),1.0 if evolved else .20,float(int(p.uid)%17)/17.0))
		index+=1
	mm.visible_instance_count=index
	mm=gems.multimesh
	index=0
	for orb in run.orbs:
		if index>=mm.instance_count: break
		var basis := Basis(Vector3.UP,float(run.tick)*.03)
		mm.set_instance_transform(index,Transform3D(basis,Vector3(orb.position.x,.18,orb.position.y)))
		mm.set_instance_color(index,Color("508c78"))
		index+=1
	mm.visible_instance_count=index
	var lines := _line_mesh;lines.clear_surfaces()
	lines.surface_begin(Mesh.PRIMITIVE_LINES)
	var vertices := 0
	var fill := _fill_mesh;fill.clear_surfaces();fill.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	var fill_vertices := 0
	for e in run.enemies.values():
		if e.telegraph.is_empty() or e.hp_raw<=0: continue
		var center := Vector3(e.position.x,.05,e.position.y)
		var direction: Vector2=e.telegraph.direction
		var imminent := 1.0-clampf(float(e.telegraph.get("remaining_ticks",40))/48.0,0,1)
		var danger_color := Color(.82,.25,.09,.78 if e.elite else .28+imminent*.28)
		lines.surface_set_color(danger_color)
		fill.surface_set_color(Color(.76,.13,.035,.060 if e.elite else .017+imminent*.010))
		if e.telegraph.shape=="fan":
			# Fill the convex hull of the paid projectile capsules. It conservatively
			# shows the volley region without a bright wireframe for every ray.
			var points := PackedVector2Array()
			var rays: Array=e.telegraph.rays
			var radius := float(e.telegraph.width)*.5/cos(PI/12.0)
			for ray in rays:
				for end_ in [Vector2.ZERO,ray*float(e.telegraph.length)]:
					for i in 12:points.append(end_+Vector2.from_angle(float(i)*TAU/12.0)*radius)
			var hull := Geometry2D.convex_hull(points)
			for i in range(1,hull.size()-1):
				for point in [hull[0],hull[i],hull[i+1]]:fill.surface_add_vertex(center+Vector3(point.x,0,point.y));fill_vertices+=1
			for ray in [rays.front(),rays.back()]:
				lines.surface_add_vertex(center);lines.surface_add_vertex(center+Vector3(ray.x,0,ray.y)*float(e.telegraph.length));vertices+=2
		elif e.telegraph.shape=="line":
			var rays: Array=e.telegraph.get("rays",[direction])
			for ray in rays:
				var end: Vector3=center+Vector3(ray.x,0,ray.y)*float(e.telegraph.length)
				var radius := float(e.telegraph.width)*.5
				var side := Vector3(-ray.y,0,ray.x)*radius
				for sign_ in [-1.0,1.0]:
					lines.surface_add_vertex(center+side*sign_)
					lines.surface_add_vertex(end+side*sign_)
					vertices+=2
				# Rounded ends match the core's capsule extent.
				for cap in [center,end]:
					vertices+=_circle(lines,cap,radius,16)
		else:
			vertices+=_circle(lines,center,float(e.telegraph.radius),40)
	if vertices==0:
		lines.surface_add_vertex(Vector3(0,-20,0));lines.surface_add_vertex(Vector3(0,-20,0))
	lines.surface_end()
	telegraph.mesh=lines
	if fill_vertices==0:
		for i in 3:fill.surface_add_vertex(Vector3(0,-20,0))
	fill.surface_end();telegraph_fill.mesh=fill
	var flash := _beam_mesh;flash.clear_surfaces()
	flash.surface_begin(Mesh.PRIMITIVE_TRIANGLES)
	var stroke_live: Array[Dictionary]=[]
	var stroke_vertices := 0
	var impact_count := 0
	var plume_count := 0
	for stroke in strokes:
		if run.mode=="playing":stroke.life-=delta
		if stroke.life<=0:continue
		flash.surface_set_color(stroke.color)
		if stroke.type=="ring":
			stroke_vertices+=_ribbon_circle(flash,Vector3(stroke.at.x,.09,stroke.at.y),stroke.radius,24,.012)
		elif stroke.type=="hit":
			var center := Vector3(stroke.at.x,.80,stroke.at.y)
			var fade := clampf(float(stroke.life)/float(stroke.duration),0,1)
			var cold: bool=float(stroke.element)>.3 and float(stroke.element)<.8
			var extent := .24 if cold else .18
			var accents := 3 if cold else 2
			var accent_color: Color=stroke.color;accent_color.a=fade*.80
			flash.surface_set_color(accent_color)
			for i in accents:
				var angle := PI*float(i)/float(accents)+.45
				var axis := camera.global_basis.x*cos(angle)+camera.global_basis.y*sin(angle)
				stroke_vertices+=_ribbon(flash,center-axis*extent,center+axis*extent,.016*fade)
		elif stroke.type=="impact":
			if impact_count<MAX_IMPACTS:
				impacts.multimesh.set_instance_transform(impact_count,Transform3D(Basis.IDENTITY.scaled(Vector3.ONE*float(stroke.radius)),Vector3(stroke.at.x,.10,stroke.at.y)))
				impacts.multimesh.set_instance_color(impact_count,stroke.color)
				var age := 1.0-float(stroke.life)/float(stroke.duration)
				impacts.multimesh.set_instance_custom_data(impact_count,Color(age,stroke.element,0,1))
				if float(stroke.element)<.25 and plume_count<MAX_IMPACTS:
					var scale_ := float(stroke.radius)*.70
					plumes.multimesh.set_instance_transform(plume_count,Transform3D(Basis.IDENTITY.scaled(Vector3.ONE*scale_),Vector3(stroke.at.x,scale_*.65,stroke.at.y)))
					plumes.multimesh.set_instance_custom_data(plume_count,Color(age,0,0,float(impact_count%7)/7.0))
					plume_count+=1
				impact_count+=1
		else:
			var from: Vector2=stroke.from
			var to: Vector2=stroke.to
			var side := Vector2(-(to-from).y,(to-from).x).normalized()
			for i in 9:
				var a: Vector2=from.lerp(to,float(i)/9.0)+side*sin(float(i)*2.7)*.18*sin(float(i)*PI/9.0)
				var b: Vector2=from.lerp(to,float(i+1)/9.0)+side*sin(float(i+1)*2.7)*.18*sin(float(i+1)*PI/9.0)
				stroke_vertices+=_ribbon(flash,Vector3(a.x,.85,a.y),Vector3(b.x,.85,b.y),float(stroke.width))
				if i in [2,5]:
					var branch := a+side*.50+Vector2(.15,-.15)
					stroke_vertices+=_ribbon(flash,Vector3(a.x,.85,a.y),Vector3(branch.x,.8,branch.y),float(stroke.width)*.42)
		stroke_live.append(stroke)
	if stroke_vertices==0:
		for i in 3:flash.surface_add_vertex(Vector3(0,-20,0))
	flash.surface_end();beams.mesh=flash;strokes=stroke_live
	impacts.multimesh.visible_instance_count=impact_count
	plumes.multimesh.visible_instance_count=plume_count
	var wanted: Dictionary={}
	for item in run.items:
		wanted[item.uid]=true
		if not item_nodes.has(item.uid):
			var root := Node3D.new()
			var beam := CylinderMesh.new()
			beam.top_radius=.012;beam.bottom_radius=.05;beam.height=1.3
			var loot_color: Color=Color("d2b46f") if item.quality=="rare" else (Color("8bb7c5") if item.quality=="magic" else Color("bab4a1"))
			var node := MeshInstance3D.new()
			node.mesh=beam;node.position.y=.65;node.material_override=_glow(loot_color,.4)
			root.add_child(node)
			var label := Label3D.new()
			label.text=item.name;label.font_size=26;label.pixel_size=.0075;label.position.y=1.5
			label.billboard=BaseMaterial3D.BILLBOARD_ENABLED;label.modulate=loot_color
			root.add_child(label);view.add_child(root);item_nodes[item.uid]=root
		item_nodes[item.uid].position=Vector3(item.position.x,0,item.position.y)
		item_nodes[item.uid].get_child(1).visible=item.position.distance_squared_to(run.hero.position)<64.0
	for uid in item_nodes.keys():
		if not wanted.has(uid): item_nodes[uid].queue_free();item_nodes.erase(uid)
	var live: Array[Dictionary]=[]
	mm=shards.multimesh
	index=0
	for particle in debris:
		if run.mode=="playing":
			particle.life-=delta
			particle.p+=particle.v*delta
			particle.v.y-=delta*5
		if particle.life<=0 or index>=MAX_PARTICLES: continue
		var basis := Basis(Vector3.UP,particle.life*15).scaled(Vector3.ONE*float(particle.size))
		mm.set_instance_transform(index,Transform3D(basis,particle.p))
		var faded: Color=particle.color;faded.a=clampf(float(particle.life)/.12,0,1)
		mm.set_instance_color(index,faded)
		index+=1;live.append(particle)
	debris=live
	mm.visible_instance_count=index

func _ribbon(mesh: ImmediateMesh, a: Vector3, b: Vector3, width: float) -> int:
	var normal := view.get_viewport().get_camera_3d().global_basis.z
	var side := (b-a).cross(normal).normalized()*width
	for vertex in [a-side,a+side,b+side,a-side,b+side,b-side]:mesh.surface_add_vertex(vertex)
	return 6

func _ribbon_circle(mesh: ImmediateMesh, at: Vector3, radius: float, count: int, width: float) -> int:
	for i in count:
		var a := at+Vector3(cos(float(i)*TAU/count),0,sin(float(i)*TAU/count))*radius
		var b := at+Vector3(cos(float(i+1)*TAU/count),0,sin(float(i+1)*TAU/count))*radius
		_ribbon(mesh,a,b,width)
	return count*6

func _circle(mesh: ImmediateMesh, at: Vector3, radius: float, count: int) -> int:
	for i in count:
		var a := float(i)*TAU/count
		var b := float(i+1)*TAU/count
		mesh.surface_add_vertex(at+Vector3(cos(a),0,sin(a))*radius)
		mesh.surface_add_vertex(at+Vector3(cos(b),0,sin(b))*radius)
	return count*2

func reset() -> void:
	_last_event=-1
	debris.clear()
	strokes.clear()
	_last_camera_tick=-100
	for node in item_nodes.values(): node.queue_free()
	item_nodes.clear()
