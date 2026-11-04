extends RefCounted
## Original mesh FX: no research atlas/texture is loaded. Visual lifetime only.
## Cylinder/Quaternion and bounded pooling match approved skill_effect_presenter.
const MAX_TRANSIENTS:=160
const MAX_PROJECTILES:=128
var view: Node3D
var active: Array=[]
var pool: Array[MeshInstance3D]=[]
var projectiles: Dictionary={}
var projectile_pool: Array[MeshInstance3D]=[]
var created:=0
var projectile_created:=0
var dropped:=0
var sphere: SphereMesh
var ring: TorusMesh
var beam: CylinderMesh
var materials: Dictionary={}

func setup(owner_view: Node3D) -> void:
	view=owner_view
	sphere=SphereMesh.new()
	sphere.radius=.12
	sphere.height=.24
	sphere.radial_segments=10
	sphere.rings=5
	ring=TorusMesh.new()
	ring.inner_radius=.93
	ring.outer_radius=1.0
	ring.rings=40
	ring.ring_segments=4
	beam=CylinderMesh.new()
	beam.top_radius=.025
	beam.bottom_radius=.025
	beam.height=1
	beam.radial_segments=5
	for pair in [["fire","ffb46d"],["cold","89d8e3"],["lightning","c7b1fb"],["ash","bcc5bd"],["hurt","da6a52"]]:
		var mat: StandardMaterial3D=view.material(Color(pair[1]),1.15)
		mat.shading_mode=BaseMaterial3D.SHADING_MODE_UNSHADED
		materials[pair[0]]=mat

func acquire(mesh: Mesh,kind: String) -> MeshInstance3D:
	var node: MeshInstance3D
	if pool.is_empty():
		if created>=MAX_TRANSIENTS:
			dropped+=1
			return null
		node=view.add_mesh(mesh,Vector3.ZERO,materials.get(kind,materials.fire))
		node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		created+=1
	else: node=pool.pop_back()
	node.mesh=mesh
	node.material_override=materials.get(kind,materials.fire)
	node.transform=Transform3D.IDENTITY
	node.show()
	return node

func consume(events: Array,sim: RefCounted) -> void:
	for event in events:
		var kind:=String(event.get("kind",""))
		var element:=String(event.get("element","fire"))
		if kind=="hit": burst(point(event.p,.85),element,8,.3)
		elif kind=="release": burst(Vector3(sim.player.x,.9,sim.player.y),element,4,.2)
		elif kind=="enemy_dead":
			if event.has("p"): burst(point(event.p,.5),"ash",8,.5)
		elif kind=="player_hurt": burst(Vector3(sim.player.x,.8,sim.player.y),"hurt",6,.3)
		elif kind=="skill_effect":
			if event.get("effect_kind")=="area":
				for delay in [0.0,.12]:
					var node:=acquire(ring,"cold")
					if node:
						node.position=point(event.origin,.08+delay)
						active.append({"node":node,"life":.6+delay,"duration":.6+delay,"velocity":Vector3.ZERO,"kind":"ring","radius":float(event.radius_world)})
			elif event.get("effect_kind")=="chain":
				var points: Array=event.points
				for i in range(1,points.size()):
					var start:=point(points[i-1],1)
					var end:=point(points[i],1)
					var mid: Vector3=(start+end)*.5+Vector3(.17 if i%2==0 else -.17,.22,0)
					segment(start,mid)
					segment(mid,end)

func segment(start: Vector3,end: Vector3) -> void:
	var delta:=end-start
	if delta.length_squared()<.000001: return
	var node:=acquire(beam,"lightning")
	if node:
		node.position=(start+end)*.5
		node.quaternion=Quaternion(Vector3.UP,delta.normalized())
		node.scale=Vector3(1,delta.length(),1)
		active.append({"node":node,"life":.18,"duration":.18,"velocity":Vector3.ZERO,"kind":"beam"})

func burst(at: Vector3,kind: String,amount: int,duration: float) -> void:
	for i in range(amount):
		var node:=acquire(sphere,kind)
		if not node: return
		node.position=at
		node.scale=Vector3.ONE*(.24+float(i%3)*.13)
		var velocity:=Vector3(sin(i*2.4)*1.8,.4+float(i%4)*.3,cos(i*2.4)*1.8)
		active.append({"node":node,"life":duration,"duration":duration,"velocity":velocity,"kind":"spark"})

func point(value: Variant,height: float) -> Vector3:
	return Vector3(float(value[0]),height,float(value[1]))

func sync(sim: RefCounted,delta: float) -> void:
	var wanted: Dictionary={}
	for bolt in sim.bolts.slice(0,MAX_PROJECTILES):
		wanted[bolt.id]=true
		if not projectiles.has(bolt.id):
			var node: MeshInstance3D
			if projectile_pool.is_empty():
				if projectile_created>=MAX_PROJECTILES: continue
				node=view.add_mesh(sphere,Vector3.ZERO,materials.fire)
				node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
				projectile_created+=1
			else: node=projectile_pool.pop_back()
			node.show()
			projectiles[bolt.id]=node
		var node: MeshInstance3D=projectiles[bolt.id]
		node.position=Vector3(bolt.p.x,.92,bolt.p.y)
		node.rotation.y=atan2(bolt.direction.x,bolt.direction.y)
		node.scale=Vector3(.7,.7,2.6)
	for id_ in projectiles.keys():
		if not wanted.has(id_):
			projectiles[id_].hide()
			projectile_pool.append(projectiles[id_])
			projectiles.erase(id_)
	var keep: Array=[]
	for fx in active:
		fx.life-=delta
		if fx.life<=0:
			fx.node.hide()
			pool.append(fx.node)
			continue
		fx.node.position+=fx.velocity*delta
		if fx.kind=="ring":
			var radius: float=float(fx.radius)*(.2+.85*(1-float(fx.life)/float(fx.duration)))
			fx.node.scale=Vector3(radius,.6,radius)
		elif fx.kind=="spark": fx.node.scale*=maxf(.01,1-delta*4)
		keep.append(fx)
	active=keep

func reset() -> void:
	for fx in active:
		fx.node.hide()
		pool.append(fx.node)
	active.clear()
	for node in projectiles.values():
		node.hide()
		projectile_pool.append(node)
	projectiles.clear()
