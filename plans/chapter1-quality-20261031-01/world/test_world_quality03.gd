extends SceneTree
var checks := 0
var failures: Array[String]=[]
func check(value: bool, label: String) -> void:
	checks+=1
	if not value:failures.append(label)
func _initialize() -> void:call_deferred("_run")
func _run() -> void:
	var view := Node3D.new();root.add_child(view)
	var world=load("res://chapter1/view/cloister_world.gd").new()
	world.setup(view)
	check(world.camera.size==24.0,"camera size preserves the comparison")
	check(world.camera.projection==Camera3D.PROJECTION_ORTHOGONAL,"orthographic projection retained")
	check(world.art_status.ground.size()==2,"both authored terrain layers loaded")
	check(world.art_status.props>=100,"authored perimeter and verges are populated")
	check(world.art_status.prop_surfaces==world._prop_textures.size(),"each authored atlas shares one surface")
	var mesh_node=view.get_node("CloisterWorldQuality03/AuthoredCloisterProps")
	var arrays: Array=mesh_node.mesh.surface_get_arrays(0)
	var total_vertices: int=arrays[Mesh.ARRAY_VERTEX].size()
	var foliage=view.get_node_or_null("CloisterWorldQuality03/AuthoredCloisterFoliage")
	if foliage:total_vertices+=foliage.mesh.surface_get_arrays(0)[Mesh.ARRAY_VERTEX].size()
	check(total_vertices==world.art_status.props*6,"every prop quad has two triangles")
	check(arrays[Mesh.ARRAY_TEX_UV].size()==arrays[Mesh.ARRAY_VERTEX].size(),"every prop vertex has atlas UV")
	check(arrays[Mesh.ARRAY_COLOR].size()==arrays[Mesh.ARRAY_VERTEX].size(),"every prop vertex has its tint")
	check(world.art_status.contact_shadows==world.art_status.props,"every prop has a bounded soft contact patch")
	var tall_inside := 0
	for entry in world._prop_entries:
		if entry.height>1.0 and maxf(absf(entry.at.x),absf(entry.at.z))<19:tall_inside+=1
	check(tall_inside==0,"solid-looking tall art stays outside the playable square")
	var before: Vector3=world.camera.position
	world.set_reduced_motion(true);world.kick_camera(100.0);world.update_camera(Vector2.ZERO,1.0/60)
	check(world.camera.position.distance_to(before)<.00001,"reduced motion ignores impact feedback")
	world.set_reduced_motion(false);world.kick_camera(100.0);world.update_camera(Vector2.ZERO,1.0/60)
	check(world.camera.position.distance_to(before)<.06,"oversized cosmetic kick stays bounded")
	for i in 30:world.update_camera(Vector2.ZERO,1.0/60)
	check(world.camera.position.distance_to(before)<.00001,"impact decays without camera drift")
	check(view.find_children("*","CollisionObject3D",true,false).is_empty(),"decorative art adds no invisible collision")
	if OS.get_cmdline_user_args().has("--prove-failure"):check(false,"intentional fixture failure")
	print("WORLD_QUALITY03_TEST ",JSON.stringify({"checks":checks,"failures":failures,"art":world.art_status,"scope":"Headless geometry/contract checks, not rendering or art-quality approval"}))
	world.root=null;world=null;view.free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
