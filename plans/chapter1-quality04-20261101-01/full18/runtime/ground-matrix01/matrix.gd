extends "res://chapter1/chapter_one_view.gd"
var cases: Array[Dictionary]=[]
func _ready() -> void:
	super._ready()
	set_process(false);set_physics_process(false);_pilot=false
	var before: Dictionary=run.snapshot()
	var original_position: Vector2=run.hero.position
	var old_failures := 0
	get_tree().root.content_scale_mode=Window.CONTENT_SCALE_MODE_DISABLED
	get_tree().root.content_scale_size=Vector2i.ZERO
	for resolution in [Vector2i(1440,810),Vector2i(1200,900),Vector2i(1920,540)]:
		get_tree().root.size=resolution
		for i in 3:await get_tree().process_frame
		for zone in 3:
			for side_x in [-1,1]:
				for side_z in [-1,1]:
					var point := Vector2(zone*48+side_x*19,side_z*19)
					run.hero.position=point
					world.update_camera(point,10);world.sync(run,0);actors.sync(run,0);hud.sync(run,0)
					var row := _coverage_case(resolution,zone,point)
					cases.append(row)
					if not row.old_floor_covers:old_failures+=1
					if (zone==0 and side_x==-1) or (zone==2 and side_x==1):
						await _shot("%dx%d-zone%d-x%d-z%d"%[resolution.x,resolution.y,zone,side_x,side_z])
		if resolution==Vector2i(1440,810):
			run.hero.position=Vector2(-4,19);world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);hud.sync(run,0)
			await _shot("same17b-boundary-z19")
	run.hero.position=original_position
	var successful := old_failures>0 and before==run.snapshot()
	for row in cases:successful=successful and row.new_floor_covers and row.one_surface
	var result := {"cases":cases,"old_floor_fails":old_failures,"all_new_floor_covers":successful,"core_unchanged":before==run.snapshot(),"scope":"Source18 actual GPU edge/corner fixtures across3viewport ratios/3zones. Direct hero placement, no core progress, not normal fullrun/manual/performance."}
	var f := FileAccess.open('C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/full18/runtime/ground-matrix01/RESULT.json',FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"));f.close()
	print("GROUND18_MATRIX ",JSON.stringify({"cases":cases.size(),"old_failures":old_failures,"success":successful}))
	_qa_quit_sent=true;audio.reset()
	var release_at := Time.get_ticks_usec()+150000
	while Time.get_ticks_usec()<release_at:await get_tree().process_frame
	get_tree().quit(0 if successful else 1)
func _coverage_case(resolution: Vector2i,zone: int,point: Vector2) -> Dictionary:
	var floor_: MeshInstance3D=world.root.get_child(0)
	var mesh: PlaneMesh=floor_.mesh
	var coverage := Rect2(Vector2(floor_.position.x,floor_.position.z)-mesh.size*.5,mesh.size)
	var old := Rect2(Vector2(-32,-35),Vector2(160,70))
	var new_ok := true;var old_ok := true
	var size_: Vector2=world.camera.get_viewport().get_visible_rect().size
	for x in [0.0,size_.x]:
		for y in [0.0,size_.y]:
			var hit: Variant=Plane(Vector3.UP,floor_.position.y).intersects_ray(world.camera.project_ray_origin(Vector2(x,y)),world.camera.project_ray_normal(Vector2(x,y)))
			if not hit is Vector3:new_ok=false;old_ok=false;continue
			new_ok=new_ok and coverage.has_point(Vector2(hit.x,hit.z));old_ok=old_ok and old.has_point(Vector2(hit.x,hit.z))
	return {"resolution":resolution,"actual_viewport":size_,"zone":zone,"hero":point,"old_floor_covers":old_ok,"new_floor_covers":new_ok,"one_surface":mesh.get_surface_count()==1,"plane_size":mesh.size}
func _shot(name_: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute('C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/full18/runtime/ground-matrix01/shots')
	get_viewport().get_texture().get_image().save_png('C:/Project/d2r-combat-baseline/plans/chapter1-quality04-20261101-01/full18/runtime/ground-matrix01/shots/'+name_+".png")
