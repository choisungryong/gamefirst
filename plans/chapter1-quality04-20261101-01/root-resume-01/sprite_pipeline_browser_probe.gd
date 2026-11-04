extends SceneTree
func _initialize() -> void:call_deferred("_test")
func _test() -> void:
	var owner := Node3D.new();root.add_child(owner)
	var actor=load("res://chapter1/presentation/sprite_asset_presenter.gd").new();owner.add_child(actor)
	var configured: bool=actor.configure("res://plans/chapter1-quality04-20261101-01/sprite-pipeline01/assets/grid-walker-browser/actor.json")
	var all_frames := true;var count := 0
	for direction in ["south","east","north","west"]:
		for i in 4:
			all_frames=all_frames and actor.sample("move",direction,(float(i)+.5)/4) and actor.last_sample.local_frame==i and not actor.last_sample.fallback;count+=1
	var missing: bool=actor.sample("death","west",1) and actor.last_sample.fallback and actor.last_sample.local_frame==0
	actor.sample("move","south",.6)
	var camera := Camera3D.new();owner.add_child(camera);camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=3.2;camera.position=Vector3(0,1.5,8);camera.look_at(Vector3(0,1,0));camera.current=true
	var headless := DisplayServer.get_name()=="headless"
	if not headless:
		for i in 6:await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://sprite-pipeline-preview.png")
	var ok: bool=configured and all_frames and missing
	var f := FileAccess.open("res://sprite-pipeline-"+("headless" if headless else "gpu")+"-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"configured":configured,"all16_authored_frames":all_frames,"missing_action_explicit":missing,"sample_count":count,"passed":ok,"scope":"Actual browser PNG registration and downloaded JSON, compiled unchanged, then same Godot presenter. Four directions16frames. No invented combat actions or active chapter modification."},"\t"));f.close()
	owner.queue_free()
	for i in 8:await process_frame
	quit(0 if ok else 1)
