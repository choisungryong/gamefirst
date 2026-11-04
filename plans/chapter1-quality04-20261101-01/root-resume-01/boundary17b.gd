extends SceneTree
var view: Node
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:
	view=load("res://chapter1/ChapterOne.tscn").instantiate();root.add_child(view)
	view._pilot=false;view.set_physics_process(false)
	var before: Dictionary=view.run.snapshot()
	var original_zone: int=view.run.zone
	var bound_ok := true
	for zone in 3:
		view.run.zone=zone
		bound_ok=bound_ok and is_equal_approx(view.run._clamp_point(Vector2(zone*48,100)).y,19)
	view.run.zone=original_zone
	var min_abs_z := INF
	var stones := 0
	var batches := 0
	for node in view.world.root.get_children():
		if not node is MultiMeshInstance3D:continue
		var mm: MultiMesh=node.multimesh
		if not (mm.mesh is CylinderMesh or mm.mesh is BoxMesh):continue
		if mm.instance_count not in [6,32]:continue
		batches+=1;stones+=mm.instance_count
		var box := mm.mesh.get_aabb()
		for i in mm.instance_count:
			var transform_: Transform3D=node.global_transform*mm.get_instance_transform(i)
			for x in [box.position.x,box.end.x]:
				for y in [box.position.y,box.end.y]:
					for z in [box.position.z,box.end.z]:min_abs_z=minf(min_abs_z,absf((transform_*Vector3(x,y,z)).z))
	var report := {"core_boundary_19":bound_ok,"stone_batches":batches,"stones":stones,"minimum_abs_z_corner":min_abs_z,"all_stones_outside_walkable_plus_0_8":min_abs_z>19.8,"core_queries_unchanged":before==view.run.snapshot(),"scope":"Actual17b packaged GPU edge fixture. Then hero deliberately placed at z19 for visibility; not a normal earned full run/manual/performance."}
	print("BOUNDARY17B ",JSON.stringify(report))
	view.run.hero.position=Vector2(-4,19)
	view.actors.reset();view.effects.reset();view.world.update_camera(view.run.hero.position,10);view.actors.sync(view.run,0);view.world.sync(view.run,0);view.hud.invalidate();view.hud.sync(view.run,0)
	for i in 2:await process_frame
	view._capture_file("boundary-z19.png")
