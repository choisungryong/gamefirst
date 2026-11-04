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
	check(world.art_status.get("court_half_extents")==[6.5,8.0],"narrower court metadata matches deployed composition")
	check(world.art_status.get("foliage_quads",0)>=400 and world.art_status.get("foliage_quads",0)<=700,"bounded dense verge population")
	var foliage_positions: Array[Vector2]=[]
	var foliage_inside_path := 0
	var quadrants := [0,0,0,0]
	for entry in world._prop_entries:
		if not world._prop_defs[entry.id]._atlas.ends_with("cloister_foliage_v01.png"):continue
		var at: Vector2=Vector2(entry.at.x,entry.at.z)
		foliage_positions.append(at)
		if world._paving_distance(at)<.319:foliage_inside_path+=1
		quadrants[(0 if at.x<0 else 1)+(0 if at.y<0 else 2)]+=1
	check(foliage_inside_path==0,"clear central paths are retained between vegetation ribbons")
	check(quadrants.min()>50,"verges populate every quadrant rather than a capped first strip")
	var min_spacing := 99.0
	for i in foliage_positions.size():
		for j in range(i):min_spacing=minf(min_spacing,foliage_positions[i].distance_to(foliage_positions[j]))
	check(min_spacing>.60,"jittered lattice prevents coincident clump stacks")
	check(world._prop_materials.size()==2,"only two shared prop materials receive lighting and occlusion uniforms")
	var cool_source := FileAccess.get_file_as_string("res://chapter1/view/cloister_props_quality03.gdshader")
	check(cool_source.contains("light_tint") and cool_source.contains("hero_position"),"unshaded art receives coherent warmth and bounded hero occlusion fade")
	var before: Vector3=world.camera.position
	world.set_reduced_motion(true);world.kick_camera(100.0);world.update_camera(Vector2.ZERO,1.0/60)
	check(world.camera.position.distance_to(before)<.00001,"reduced motion ignores impact feedback")
	world.set_reduced_motion(false);world.kick_camera(100.0);world.update_camera(Vector2.ZERO,1.0/60)
	check(world.camera.position.distance_to(before)<.06,"oversized cosmetic kick stays bounded")
	for i in 30:world.update_camera(Vector2.ZERO,1.0/60)
	check(world.camera.position.distance_to(before)<.00001,"impact decays without camera drift")
	check(view.find_children("*","CollisionObject3D",true,false).is_empty(),"decorative art adds no invisible collision")
	if OS.get_cmdline_user_args().has("--prove-failure"):check(false,"intentional fixture failure")
	print("WORLD_QUALITY03_TEST ",JSON.stringify({"checks":checks,"failures":failures,"art":world.art_status,"foliage_quadrants":quadrants,"minimum_foliage_spacing":min_spacing,"scope":"Headless geometry/contract checks, not rendering or art-quality approval"}))
	world.root=null;world=null;view.free()
	await process_frame
	quit(0 if failures.is_empty() else 1)

