extends RefCounted
## Presentation pools never change simulation state or consume gameplay RNG.
## Sprite atlas API: https://docs.godotengine.org/en/4.5/classes/class_sprite3d.html
const MAX_PROJECTILES := 512
const MAX_PARTICLES := 256
const SkillEffects = preload("res://presentation/skill_effect_presenter.gd")
var skill_effects = SkillEffects.new()
var projectile_nodes: Dictionary = {}
var projectile_pool: Array[Sprite3D] = []
var particles: Array = []
var particle_pool: Array[MeshInstance3D] = []
var meshes: Array[SphereMesh] = []
var materials: Dictionary = {}
var projectile_created := 0
var particle_created := 0
var projectile_reused := 0
var particle_reused := 0
var dropped_particles := 0
var dropped_projectiles := 0
var owner_node: Node3D
var mesh_callback: Callable
var material_callback: Callable
var camera_transform := Transform3D.IDENTITY
var camera_projection := -1
var camera_size := -1.0
var camera_fov := -1.0
var camera_epoch := 0
var direction_angles := [135.0,-135.0,-45.0,45.0,90.0,180.0,-90.0,0.0,112.5,157.5,-157.5,-112.5,-67.5,-22.5,22.5,67.5]

func setup(parent: Node3D, mesh: Callable, material: Callable) -> void:
	owner_node = parent
	mesh_callback = mesh
	material_callback = material
	skill_effects.setup(parent,material)
	for index in range(3):
		var sphere := SphereMesh.new()
		sphere.radius = .035+.012*index
		sphere.height = sphere.radius*2
		sphere.radial_segments = 8
		sphere.rings = 4
		meshes.append(sphere)

func burst(at: Vector3, color: Color, amount: int, duration: float) -> void:
	if duration <= 0 or not is_finite(duration) or amount <= 0: return
	var signature: String = color.to_html()
	if not materials.has(signature): materials[signature] = material_callback.call(color,1.1)
	for index in range(amount):
		if particles.size() >= MAX_PARTICLES:
			dropped_particles += amount-index
			break
		var node: MeshInstance3D
		if particle_pool.is_empty():
			node = mesh_callback.call(meshes[index%3],at,materials[signature])
			particle_created += 1
		else:
			node = particle_pool.pop_back()
			particle_reused += 1
			node.mesh = meshes[index%3]
			node.material_override = materials[signature]
			node.position = at
		node.scale = Vector3.ONE
		node.show()
		var direction := Vector3(sin(index*2.4),.4+float(index%4)*.25,cos(index*2.4))
		particles.append({"node":node,"velocity":direction*1.8,"life":duration,"max":duration})

func release_particle(node: MeshInstance3D) -> void:
	node.hide()
	node.scale = Vector3.ONE
	particle_pool.append(node)

func advance(delta: float) -> void:
	skill_effects.advance(delta)
	var keep: Array = []
	for particle in particles:
		particle.life -= delta
		if particle.life > 0:
			particle.node.position += particle.velocity*delta
			particle.node.scale = Vector3.ONE*maxf(.05,float(particle.life)/float(particle.max))
			keep.append(particle)
		else: release_particle(particle.node)
	particles = keep

func release_projectile(identity: int) -> void:
	var node: Sprite3D = projectile_nodes[identity]
	node.hide()
	node.frame_coords = Vector2i.ZERO
	projectile_pool.append(node)
	projectile_nodes.erase(identity)

func sync(sim: RefCounted, camera: Camera3D, atlas: Texture2D) -> void:
	skill_effects.sync(sim)
	if camera.global_transform != camera_transform or camera.projection != camera_projection or camera.size != camera_size or camera.fov != camera_fov:
		camera_transform = camera.global_transform
		camera_projection = camera.projection
		camera_size = camera.size
		camera_fov = camera.fov
		camera_epoch += 1
	var active: Dictionary = {}
	for index in range(mini(sim.bolts.size(),MAX_PROJECTILES)): active[sim.bolts[index].id] = true
	dropped_projectiles += maxi(0,sim.bolts.size()-MAX_PROJECTILES)
	for identity in projectile_nodes.keys():
		if not active.has(identity): release_projectile(identity)
	for index in range(mini(sim.bolts.size(),MAX_PROJECTILES)):
		var bolt: Dictionary = sim.bolts[index]
		if not projectile_nodes.has(bolt.id):
			var sprite: Sprite3D
			if projectile_pool.is_empty():
				sprite = Sprite3D.new()
				sprite.hframes = 5
				sprite.vframes = 16
				sprite.pixel_size = .019
				sprite.billboard = BaseMaterial3D.BILLBOARD_ENABLED
				sprite.shaded = false
				sprite.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST
				owner_node.add_child(sprite)
				projectile_created += 1
			else:
				sprite = projectile_pool.pop_back()
				projectile_reused += 1
			sprite.texture = atlas
			sprite.scale = Vector3.ONE
			sprite.show()
			sprite.set_meta("camera_epoch",-1)
			projectile_nodes[bolt.id] = sprite
		var visual: Sprite3D = projectile_nodes[bolt.id]
		var desired_position := Vector3(bolt.p.x,.9,bolt.p.y)
		if visual.position != desired_position: visual.position = desired_position
		var selected: int = visual.get_meta("atlas_direction",0)
		# Orthographic heading depends only on direction/camera. Perspective keeps
		# the per-frame projection because its screen heading changes with position.
		if visual.get_meta("camera_epoch",-1) != camera_epoch or visual.get_meta("atlas_direction_vector",Vector2.ZERO) != bolt.direction or camera.projection != Camera3D.PROJECTION_ORTHOGONAL:
			var start_screen: Vector2 = camera.unproject_position(visual.position)
			var end_screen: Vector2 = camera.unproject_position(visual.position+Vector3(bolt.direction.x,0,bolt.direction.y))
			var heading: float = (end_screen-start_screen).angle()
			var best := INF
			for direction_index in range(direction_angles.size()):
				var distance: float = absf(angle_difference(heading,deg_to_rad(direction_angles[direction_index])))
				if distance < best:
					best = distance
					selected = direction_index
			visual.set_meta("atlas_direction",selected)
			visual.set_meta("camera_epoch",camera_epoch)
			visual.set_meta("atlas_direction_vector",bolt.direction)
		var desired_frame := Vector2i(floori(float(bolt.age)*float(sim.params.atlas_playback_fps)/60.0)%5,selected)
		if visual.frame_coords != desired_frame: visual.frame_coords = desired_frame

func reset() -> void:
	skill_effects.reset()
	for identity in projectile_nodes.keys(): release_projectile(identity)
	for particle in particles: release_particle(particle.node)
	particles.clear()

func handle_skill_event(event: Dictionary) -> void:
	skill_effects.handle_event(event)

