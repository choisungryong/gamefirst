extends Node3D
var run=preload("res://chapter1/core/chapter_run_quality16.gd").new()
var records: Array[Dictionary]=[]
func _ready() -> void:call_deferred("_study")
func _study() -> void:
	DirAccess.make_dir_recursive_absolute("res://space27-shots")
	var frozen: Dictionary=run.snapshot().duplicate(true)
	for revision in [22,27]:
		var world=load("res://chapter1/view/chapter_world_quality%d.gd"%revision).new()
		world.setup(self)
		for zone in 3:
			world.update_camera(Vector2(zone*48,0),10)
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			var label := "%d-zone%d"%[revision,zone]
			var image := get_viewport().get_texture().get_image()
			image.save_png("res://space27-shots/"+label+".png")
			records.append({"label":label,"size":[image.get_width(),image.get_height()],"same_core":frozen==run.snapshot()})
		for child in get_children():child.queue_free()
		await get_tree().process_frame
		world=null
	var same: bool=frozen==run.snapshot()
	var f := FileAccess.open("res://space27-result.json",FileAccess.WRITE)
	f.store_string(JSON.stringify({"records":records,"same_complete_core":same,"scope":"Unconnected world-only shader study; same fixed core, no actors. Not a packaged or gameplay/performance approval."},"\t"));f.close()
	get_tree().quit(0 if same else 1)
