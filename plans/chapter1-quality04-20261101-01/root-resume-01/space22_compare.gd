extends Node3D
const Before22=preload("res://chapter1/view/chapter_world_quality18.gd")
const After22=preload("res://chapter1/view/chapter_world_quality22.gd")
var run=preload("res://chapter1/core/chapter_run_quality16.gd").new()
var world: RefCounted
var report: Dictionary={"records":[],"scope":"World-only architecture/camera study; fixed core menu fixture, no actors or gameplay. Before18/after22, no new package/manual/performance claim."}
func _ready() -> void:
	call_deferred("_study")
func _study() -> void:
	DirAccess.make_dir_recursive_absolute("res://space22-shots")
	var frozen: Dictionary=run.snapshot().duplicate(true)
	for revision in [22]:
		world=Before22.new() if revision==18 else After22.new()
		world.setup(self)
		for zone in 3:
			for z in [-8.0,-17.0]:
				world.update_camera(Vector2(zone*48,z),10)
				await RenderingServer.frame_post_draw
				await RenderingServer.frame_post_draw
				var label := "%d-zone%d-z%d"%[revision,zone,z]
				get_viewport().get_texture().get_image().save_png("res://space22-shots/"+label+".png")
				report.records.append({"label":label,"art":world.art_status.duplicate(true),"core_unchanged":frozen==run.snapshot()})
		if revision==22:
			var outside := true
			for record in world.masonry22:
				var t: Transform3D=record.transform
				# Both unit boxes and the fixed voussoir stay north of z=-19.
				var depth := .55 if t.origin.y>3 else absf(t.basis.x.z)*.5+absf(t.basis.z.z)*.5
				outside=outside and t.origin.z+depth< -19.0
			report.all_new_masonry_outside_walkable=outside
		for child in get_children():child.queue_free()
		await get_tree().process_frame
		world=null
	report.same_complete_core=frozen==run.snapshot()
	var f := FileAccess.open("res://space22-result.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close()
	get_tree().quit(0 if report.same_complete_core and report.all_new_masonry_outside_walkable else 1)
