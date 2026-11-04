extends "res://chapter1/view/cloister_world_quality03.gd"
## Three authored connected spaces. Decorative walls never occupy walkable cells.
var gates: Array[Node3D]=[]
var seals: Array[MeshInstance3D]=[]
var ritual_labels: Dictionary={}
var route: MeshInstance3D

func setup(view: Node3D) -> void:
	super.setup(view)
	var floor_: MeshInstance3D=root.get_child(0)
	(floor_.mesh as PlaneMesh).size=Vector2(160,70);floor_.position.x=48
	for i in 3:
		var ring := _ring(Vector3(i*48,.035,0),4.0,4.08,Color("648a9e"));seals.append(ring)
		_ring(Vector3(i*48,.035,0),3.5,3.53,Color("3e5867"))
		for side in [-1,1]:
			for step in 6:
				var marker := MeshInstance3D.new();var box := BoxMesh.new();box.size=Vector3(.12,.025,.35);marker.mesh=box
				marker.material_override=material(Color("927a52"),.15);marker.position=Vector3(i*48+side*3.9,.03,-2.0+step*.8);root.add_child(marker)
	for i in 2:
		var gate := Node3D.new();gate.position=Vector3(19+i*48,0,0);root.add_child(gate);gates.append(gate)
		for z in 7:
			var bar := MeshInstance3D.new();var mesh := BoxMesh.new();mesh.size=Vector3(.10,2.6,.045);bar.mesh=mesh;bar.material_override=material(Color("ae8750"),.7);bar.position=Vector3(0,1.3,-3+z);gate.add_child(bar)
		var text := Label3D.new();text.text="봉인을 해제하면 열립니다";text.position=Vector3(0,3.0,0);text.pixel_size=.009;text.font_size=32;text.billboard=BaseMaterial3D.BILLBOARD_ENABLED;gate.add_child(text)
	for def in view.run.RITUALS:
		_ring(Vector3(def.position.x,.04,def.position.y),2.2,2.28,Color("79604f"))
		var label := Label3D.new();label.position=Vector3(def.position.x,1.3,def.position.y);label.pixel_size=.008;label.font_size=30;label.billboard=BaseMaterial3D.BILLBOARD_ENABLED
		label.text=def.name+"\n[E] 의식 시작";root.add_child(label);ritual_labels[def.id]=label
	route=MeshInstance3D.new();var arrow := PrismMesh.new();arrow.size=Vector3(.45,.035,.7);route.mesh=arrow;route.material_override=material(Color("c5a367"),.3);root.add_child(route)

func _ground_material() -> Material:
	var mat := ShaderMaterial.new();mat.shader=load("res://chapter1/view/chapter_ground.gdshader")
	for pair in [["flagstone","ground_flagstone_v01.png"],["soil","ground_soil_v01.png"]]:
		var texture := _texture(ART_BASE+pair[1])
		if texture:mat.set_shader_parameter(pair[0],texture);mat.set_shader_parameter("has_"+pair[0],true);art_status.ground.append(pair[1])
	return mat

func _compose_cloister() -> void:
	art_status.composition_revision="full-chapter-three-courtyards-01"
	# Graveyard, broken nave, circular sanctuary use different silhouettes/layouts.
	_prop("arch",Vector3(0,0,-21),6.5,Color(.74,.80,.87))
	for side in [-1.0,1.0]:
		for x in [-16,-8,0,8,16]:
			_prop("grave_cross" if x<0 else "grave_slab",Vector3(x,0,side*20.2),1.35,Color(.75,.8,.83))
			_prop("wall",Vector3(x,0,side*22),2.0,Color(.61,.68,.73))
		_prop("tree",Vector3(-22,0,side*18),5.7,Color(.64,.72,.76),side>0)
		_prop("pillar_broken",Vector3(19.8,0,side*5.2),3.2)
		for x in [31,40,48,56,65]:
			_prop("pillar_whole" if x in [31,65] else "pillar_broken",Vector3(x,0,side*20.7),4.4,Color(.78,.75,.76))
			_prop("wall",Vector3(x,0,side*23),3.0,Color(.69,.67,.7))
		for x in [21,26,69,74]:_prop("pillar_broken",Vector3(x,0,side*4.6),2.5,Color(.75,.72,.72))
		for x in [48,60,84,108]:_brazier(Vector3(x,0,side*19.8))
	_prop("arch",Vector3(48,0,-23),8.2,Color(.73,.70,.75))
	for i in 14:
		var a := TAU*i/14.0;var at := Vector3(96+cos(a)*21.5,0,sin(a)*21.5)
		# Leave the west corridor visibly open.
		if at.x<77 and absf(at.z)<6:continue
		_prop("pillar_whole" if i%3 else "pillar_broken",at,5.2,Color(.69,.73,.81))
	_prop("arch",Vector3(96,0,-24),9.0,Color(.65,.71,.81))
	for at in [Vector3(33,0,-16),Vector3(63,0,15),Vector3(88,0,-17),Vector3(109,0,14),Vector3(-12,0,16)]:
		_prop("rubble",at,.65,Color(.77,.75,.72));_prop("roots",at+Vector3(1,0,.5),.50,Color(.59,.65,.61))
	_compose_verges()
	# Sparse growth in the nave; sanctuary leaves broad ash paving visible.
	for i in 100:
		var side := -1 if i%2 else 1
		_prop("grass_bent" if i%3 else "fern_moss",Vector3(_rng.randf_range(30,65),.005,side*_rng.randf_range(14,21)),_rng.randf_range(.28,.5),Color(.7,.68,.6),i%2==0)

func _ring(at: Vector3,inner: float,outer: float,color: Color) -> MeshInstance3D:
	var node := MeshInstance3D.new();var mesh := TorusMesh.new();mesh.inner_radius=inner;mesh.outer_radius=outer;mesh.rings=64;mesh.ring_segments=6
	node.mesh=mesh;node.scale.y=.12;node.position=at;node.material_override=material(color,.14);root.add_child(node);return node

func sync(run: RefCounted,_delta: float) -> void:
	if run.hero.is_empty():return
	for i in gates.size():gates[i].visible=run.zone<=i
	for i in seals.size():
		var mat: StandardMaterial3D=seals[i].material_override
		mat.albedo_color=Color("d6ac63") if run.seals[i].cleared else (Color("8eaaac") if i==run.zone else Color("3f4e57"))
	for def in run.RITUALS:
		var state: Dictionary=run.rituals[def.id];var label: Label3D=ritual_labels[def.id]
		var text: String=def.name
		if state.state=="ready":text+="\n[E] 의식 시작"
		elif state.state=="active":text+="\n%d / %d"%[state.progress/60 if def.kind=="hold" else state.progress,25 if def.kind=="hold" else 60]
		elif state.state=="completed":text+="\n의식 완료"
		else:text+="\n의식 종료"
		label.text=text;label.visible=run.hero.position.distance_squared_to(def.position)<12*12
	var objective: Dictionary=run.objective();route.visible=not objective.entered and run.mode=="playing"
	if route.visible:
		var direction: Vector2=(objective.destination-run.hero.position).normalized()
		route.position=Vector3(run.hero.position.x+direction.x*2.1,.08,run.hero.position.y+direction.y*2.1);route.rotation.y=atan2(direction.x,direction.y)
