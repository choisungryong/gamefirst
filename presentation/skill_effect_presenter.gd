extends RefCounted
## Output-only, bounded phase4 FX. Simulation ticks own status expiry and damage.
## Quaternion arc constructor and primitive meshes use the official 4.5 APIs:
## https://docs.godotengine.org/en/4.5/classes/class_quaternion.html
## https://docs.godotengine.org/en/4.5/classes/class_torusmesh.html
## https://docs.godotengine.org/en/4.5/classes/class_cylindermesh.html
const MAX_NODES := 64
var owner_node: Node3D
var pool: Array[MeshInstance3D] = []
var active: Array = []
var statuses: Dictionary = {}
var created := 0
var reused := 0
var dropped := 0
var ring_mesh: TorusMesh
var beam_mesh: CylinderMesh
var cold_material: Material
var chain_material: Material

func setup(parent: Node3D, material_callback: Callable) -> void:
	owner_node = parent
	ring_mesh = TorusMesh.new()
	ring_mesh.inner_radius = .965
	ring_mesh.outer_radius = 1.0
	ring_mesh.rings = 32
	ring_mesh.ring_segments = 6
	beam_mesh = CylinderMesh.new()
	beam_mesh.top_radius = .035
	beam_mesh.bottom_radius = .035
	beam_mesh.height = 1.0
	beam_mesh.radial_segments = 6
	beam_mesh.rings = 1
	cold_material = material_callback.call(Color("76d5dc"),1.2)
	chain_material = material_callback.call(Color("bcadff"),1.3)

func acquire(mesh: Mesh, mat: Material) -> MeshInstance3D:
	var node: MeshInstance3D
	if pool.is_empty():
		if created >= MAX_NODES:
			dropped += 1
			return null
		node = MeshInstance3D.new()
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		owner_node.add_child(node)
		created += 1
	else:
		node = pool.pop_back()
		reused += 1
	node.mesh = mesh
	node.material_override = mat
	node.transform = Transform3D.IDENTITY
	node.show()
	return node

func retire(node: MeshInstance3D) -> void:
	node.hide()
	node.transform = Transform3D.IDENTITY
	pool.append(node)

func point(value: Variant, height: float) -> Vector3:
	return Vector3(float(value[0]),height,float(value[1]))

func handle_event(event: Dictionary) -> void:
	if event.kind == "skill_effect":
		if event.effect_kind == "area":
			var radius: float = float(event.radius_world)
			if not is_finite(radius) or radius <= 0: return
			var node: MeshInstance3D = acquire(ring_mesh,cold_material)
			if node:
				node.position = point(event.origin,.1)
				node.scale = Vector3(radius*.25,1,radius*.25)
				active.append({"node":node,"kind":"area","life":.55,"duration":.55,"radius":radius})
		elif event.effect_kind == "chain":
			var points: Array = event.points
			for index in range(1,mini(points.size(),MAX_NODES+1)):
				var start: Vector3 = point(points[index-1],.85)
				var finish: Vector3 = point(points[index],.85)
				var segment: Vector3 = finish-start
				if segment.length_squared() < .000001: continue
				var node: MeshInstance3D = acquire(beam_mesh,chain_material)
				if not node: break
				node.position = (start+finish)*.5
				node.quaternion = Quaternion(Vector3.UP,segment.normalized())
				node.scale = Vector3(1,segment.length(),1)
				active.append({"node":node,"kind":"chain","life":.2,"duration":.2})
	elif event.kind == "status_applied" and event.get("status","") == "chill":
		var identity: Dictionary = event.entity
		var key_: String = "%d:%d" % [identity.id,identity.generation]
		if statuses.has(key_):
			statuses[key_].until_tick = int(event.until_tick)
		else:
			var node: MeshInstance3D = acquire(ring_mesh,cold_material)
			if node:
				node.position = point(event.p,.07)
				node.scale = Vector3(.43,1,.43)
				statuses[key_] = {"node":node,"entity":identity.duplicate(true),"until_tick":int(event.until_tick)}
	elif event.kind == "status_expired" and event.get("status","") == "chill":
		var identity: Dictionary = event.entity
		remove_status("%d:%d" % [identity.id,identity.generation])

func remove_status(identity: String) -> void:
	if not statuses.has(identity): return
	retire(statuses[identity].node)
	statuses.erase(identity)

func sync(sim: RefCounted) -> void:
	for identity in statuses.keys():
		var visual: Dictionary = statuses[identity]
		var state: Dictionary = sim.entity(visual.entity)
		if state.is_empty() or state.state == "dead" or sim.tick >= visual.until_tick:
			remove_status(identity)
		else:
			var position: Vector3 = Vector3(state.p.x,.07,state.p.y)
			if visual.node.position != position: visual.node.position = position

func advance(delta: float) -> void:
	var keep: Array = []
	for visual in active:
		visual.life -= delta
		if visual.life <= 0:
			retire(visual.node)
			continue
		if visual.kind == "area":
			var progress: float = 1.0-float(visual.life)/float(visual.duration)
			var radius: float = float(visual.radius)*(.25+.8*progress)
			visual.node.scale = Vector3(radius,1,radius)
		keep.append(visual)
	active = keep

func reset() -> void:
	for visual in active: retire(visual.node)
	active.clear()
	for identity in statuses.keys(): remove_status(identity)
