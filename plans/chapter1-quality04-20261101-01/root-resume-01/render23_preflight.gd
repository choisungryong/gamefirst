extends SceneTree
var frames := 0
func _initialize() -> void:call_deferred("_boot")
func _boot() -> void:root.add_child(load("res://chapter1/ChapterOne.tscn").instantiate())
func _process(_delta: float) -> bool:
	frames+=1
	if frames==15:call_deferred("_inspect")
	return false
func _inspect() -> void:
	await RenderingServer.frame_post_draw
	var texture := root.get_texture()
	var image_ := texture.get_image()
	var report := {"window":root.size,"display_window":DisplayServer.window_get_size(),"visible_rect":root.get_visible_rect(),"texture_reported":texture.get_size(),"readback_image":image_.get_size(),"screen_scale":DisplayServer.screen_get_scale(),"screen_dpi":DisplayServer.screen_get_dpi(),"rendering_method":RenderingServer.get_current_rendering_method(),"gpu":RenderingServer.get_video_adapter_name(),"scope":"Actual23 live menu same-frame dimension preflight; one image readback, not performance sample."}
	print("RENDER23_PREFLIGHT ",JSON.stringify(report))
	var folder := OS.get_executable_path().get_base_dir().path_join("qa-captures/render23-preflight01")
	DirAccess.make_dir_recursive_absolute(folder)
	image_.save_png(folder.path_join("menu.png"))
	quit()
