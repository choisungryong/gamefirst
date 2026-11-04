extends SceneTree
var output := "res://evidence/phase7/presentation-resume-20261030-02"
var view
func _initialize() -> void:
	call_deferred("run")
func capture(name_: String) -> void:
	await RenderingServer.frame_post_draw
	var frame := root.get_texture().get_image()
	frame.save_png(output.path_join(name_+".png"))
func run() -> void:
	DirAccess.make_dir_recursive_absolute(output)
	root.size=Vector2i(1920,1080)
	view=load("res://Expedition.tscn").instantiate()
	root.add_child(view)
	await create_timer(1.0).timeout
	await capture("ready")
	view.start_run()
	view.input_controller.auto_cast=true
	await create_timer(8.0).timeout
	await capture("active")
	view.controller.elapsed_ticks=10800
	await create_timer(1.0).timeout
	await capture("elite-synthetic")
	var summary={"scope":"implementation-only visual snapshots; synthetic elapsed clock for elite image","viewport":[root.size.x,root.size.y],"snapshot":view.controller.snapshot(),"audio_played":view.audio.played,"audio_voices":view.audio.voices.size()}
	var file=FileAccess.open(output.path_join("capture.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify(summary,"\t"))
	view.queue_free()
	await process_frame
	quit(0)
