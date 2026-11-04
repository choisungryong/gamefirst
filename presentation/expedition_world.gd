extends RefCounted
## Independent scene composition. All props are decorative: Sim owns movement.
## StaticBatch/WorldEnvironment patterns are copied from the approved baseline.
const StaticBatch = preload("res://presentation/static_batch.gd")
var view: Node3D
var elite_root: Node3D
var elite_key := ""
var elite_actor: WeakRef
var elite_original_scale := Vector3.ONE
var elite_original_materials: Array = []
var elite_label: Label3D
var elite_ring: MeshInstance3D
var elite_bar: MeshInstance3D
var hero_ring: MeshInstance3D
var floor_stats: Dictionary = {}

func setup(owner_view: Node3D) -> void:
	view = owner_view
	view.world = Node3D.new()
	view.world.name = "AshenCloister"
	view.add_child(view.world)
	var env_node := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("17232a")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("b4cbd3")
	env.ambient_light_energy = .43
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color("35434c")
	env.fog_density = .006
	env_node.environment = env
	view.add_child(env_node)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-54,-32,0)
	sun.light_color = Color("c8dbe5")
	sun.light_energy = 1.12
	sun.shadow_enabled = true
	view.add_child(sun)
	var floor_plane := PlaneMesh.new()
	floor_plane.size = Vector2(100,100)
	view.add_mesh(floor_plane,Vector3(0,-.12,0),view.material(Color("26353c")),view.world)
	var floor_roots: Array[Node3D] = []
	for x in range(-10,11):
		for z in range(-10,11):
			var tile_name := "floor_tile_large.gltf.glb" if absi(x) <= 3 or absi(z) <= 2 else "floor_dirt_large_rocky.gltf.glb"
			var tile: Node3D = view.load_model("res://assets/environment/"+tile_name,Vector3(x*2,-.04,z*2),view.world)
			tile.rotation.y = float((x*7+z*11)&3)*PI*.5
			var worn: int=absi(x*13+z*7)%3
			var stone_tones := [Color(.44,.51,.57),Color(.50,.57,.62),Color(.47,.54,.59)]
			var dirt_tones := [Color(.33,.40,.39),Color(.38,.44,.42),Color(.35,.41,.40)]
			view.tint_model(tile,stone_tones[worn] if tile_name.begins_with("floor_tile") else dirt_tones[worn])
			floor_roots.append(tile)
	floor_stats = StaticBatch.batch(view.world,floor_roots)
	# The collapsed cloister borders frame the arena without blocking its floor.
	for side in [-1,1]:
		for along in [-16,-10,-4,4,10,16]:
			var column: Node3D = view.load_model("res://assets/environment/column.gltf.glb",Vector3(along,0,side*20),view.world)
			view.tint_model(column,Color(.55,.61,.66))
			var wall: Node3D = view.load_model("res://assets/environment/wall_broken.gltf.glb",Vector3(side*20,0,along),view.world)
			wall.rotation.y = PI*.5
			view.tint_model(wall,Color(.45,.52,.57))
	for pos in [Vector3(-7,0,-6),Vector3(7,0,-6),Vector3(-7,0,7),Vector3(7,0,7)]:
		view.load_model("res://assets/environment/torch_lit.gltf.glb",pos,view.world)
		var light := OmniLight3D.new()
		light.position = pos+Vector3.UP*1.7
		light.light_color = Color("ffac61")
		light.light_energy = 1.5
		light.omni_range = 6
		view.world.add_child(light)
	# Broken bronze inlays make the central path recognizable from any heading.
	var slab := BoxMesh.new()
	slab.size = Vector3(.15,.015,1.05)
	var bronze: Material = view.material(Color("8f7b52"))
	for side in [-1,1]:
		for z in range(-12,13,2):
			view.add_mesh(slab,Vector3(side*3.2,.015,z),bronze,view.world)
	# A worn, flat sanctuary seal is the landmark; no collision or combat rules.
	var sanctuary:=Node3D.new()
	sanctuary.name="BrokenSanctuarySeal"
	view.world.add_child(sanctuary)
	view.add_mesh(ring(2.82,2.88),Vector3(0,.026,0),view.material(Color("696446"),.06),sanctuary)
	var seal_arm:=BoxMesh.new()
	seal_arm.size=Vector3(.10,.015,1.20)
	for i in range(8):
		var angle:=i*PI*.25
		var arm: MeshInstance3D=view.add_mesh(seal_arm,Vector3(sin(angle)*2.15,.027,cos(angle)*2.15),bronze,sanctuary)
		arm.rotation.y=angle
	var censer_light:=OmniLight3D.new()
	censer_light.position=Vector3(0,2.5,0)
	censer_light.light_color=Color("a8cbd0")
	censer_light.light_energy=.65
	censer_light.omni_range=7
	view.world.add_child(censer_light)
	view.hero = view.load_model("res://assets/actors/Mage.glb",Vector3.ZERO)
	view.hero.scale = Vector3.ONE*1.05
	view.tint_model(view.hero,Color(.94,.96,1.0))
	view.enemy_actor = view.load_model("res://assets/actors/Skeleton_Minion.glb",Vector3.ZERO)
	view.enemy_actor.scale = Vector3.ONE*1.12
	view.tint_model(view.enemy_actor,Color(.76,.81,.76))
	view.actor_registry.setup(view.enemy_actor,view.load_model,view.animate,view.tint_model)
	view.camera = Camera3D.new()
	view.camera.position = Vector3(12,18,15)
	view.camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	view.camera.size = 22.0
	view.add_child(view.camera)
	view.camera.look_at(Vector3(0,.35,0))
	view.camera.current = true
	hero_ring = view.add_mesh(ring(.29,.32),Vector3(0,.035,0),view.material(Color("bed6d7"),.25))
	elite_root = Node3D.new()
	view.add_child(elite_root)
	elite_ring = view.add_mesh(ring(.74,.82),Vector3(0,.045,0),view.material(Color("e3b270"),.5),elite_root)
	# A crown with four tall obelisks gives a silhouette cue, not only a tint.
	var spike := PrismMesh.new()
	spike.size = Vector3(.20,.55,.20)
	for i in range(4):
		var angle := i*PI*.5
		view.add_mesh(spike,Vector3(cos(angle)*.65,.3,sin(angle)*.65),view.material(Color("bd945c")),elite_root)
	elite_label = Label3D.new()
	elite_label.text = "쇠락한 수호자"
	elite_label.font_size = 36
	elite_label.pixel_size = .007
	elite_label.position.y = 2.7
	elite_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	elite_label.no_depth_test = true
	elite_label.modulate = Color("f0d19b")
	elite_root.add_child(elite_label)
	var hp_mesh := BoxMesh.new()
	hp_mesh.size = Vector3(1.3,.065,.06)
	elite_bar = view.add_mesh(hp_mesh,Vector3(0,2.42,0),view.material(Color("c35e49"),.1),elite_root)
	elite_root.hide()

func ring(inner: float,outer: float) -> TorusMesh:
	var mesh := TorusMesh.new()
	mesh.inner_radius = inner
	mesh.outer_radius = outer
	mesh.rings = 32
	mesh.ring_segments = 4
	return mesh

func sync_elite(identity: Dictionary,registry: RefCounted) -> void:
	hero_ring.position = Vector3(view.sim.player.x,.035,view.sim.player.y)
	if identity.is_empty():
		restore_elite_actor()
		elite_root.hide()
		return
	var state: Dictionary = view.sim.entity(identity)
	var key := "%d:%d" % [int(identity.get("id",0)),int(identity.get("generation",0))]
	if state.is_empty() or String(state.state) == "dead":
		restore_elite_actor()
		elite_root.hide()
		return
	elite_root.show()
	elite_root.position = Vector3(state.p.x,0,state.p.y)
	elite_bar.scale.x = clampf(float(state.get("life_raw",0))/maxf(1,float(state.get("max_raw",54*256))),0,1)
	if registry.actors.has(key):
		var actor: Node3D = registry.actors[key]
		if elite_key != key or elite_actor == null or elite_actor.get_ref() != actor:
			restore_elite_actor()
			elite_actor=weakref(actor)
			elite_original_scale=actor.scale
			remember_and_tint(actor)
			actor.scale=Vector3.ONE*1.48
			elite_key = key
	else:
		restore_elite_actor()
		elite_root.hide()

func remember_and_tint(node: Node) -> void:
	if node is MeshInstance3D and node.mesh != null:
		var originals: Array = []
		for surface in range(node.mesh.get_surface_count()):
			originals.append(node.get_surface_override_material(surface))
			var active: Material=node.get_active_material(surface)
			if active is StandardMaterial3D:
				var tinted: StandardMaterial3D=active.duplicate()
				tinted.albedo_color*=Color(1.0,.77,.55)
				node.set_surface_override_material(surface,tinted)
		elite_original_materials.append({"mesh":weakref(node),"materials":originals})
	for child in node.get_children(): remember_and_tint(child)

func restore_elite_actor() -> void:
	# Registry nodes can be pooled, rebound to a new generation, or freed. Restore
	# only still-live weak references; never retain an actor or its old tint.
	if elite_actor != null:
		var actor=elite_actor.get_ref()
		if is_instance_valid(actor): actor.scale=elite_original_scale
	for entry in elite_original_materials:
		var mesh=entry.mesh.get_ref()
		if not is_instance_valid(mesh) or mesh.mesh == null: continue
		for surface in range(mini(entry.materials.size(),mesh.mesh.get_surface_count())):
			mesh.set_surface_override_material(surface,entry.materials[surface])
	elite_actor=null
	elite_original_materials.clear()
	elite_key=""
