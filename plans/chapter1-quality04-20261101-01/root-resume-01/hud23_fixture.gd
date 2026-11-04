extends "res://chapter1/chapter_one_input21.gd"
const NewHUD23=preload("res://chapter1/view/chapter_hud_quality23.gd")
var rows: Array[Dictionary]=[]
var frozen: Dictionary
func _ready() -> void:
	super._ready()
	set_physics_process(false)
	while run.tick<16000:run.step(full_pilot.decide())
	actors.reset();effects.reset();hud.reset();run.events.clear()
	world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);effects.sync(run,0);hud.sync(run,0)
	frozen=run.snapshot().duplicate(true)
	call_deferred("_fixture23")
func _process(_delta: float) -> void:pass
func _fixture23() -> void:
	DirAccess.make_dir_recursive_absolute("res://hud23-shots")
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://hud23-shots/before.png")
	var old_root: Control=hud.root
	old_root.queue_free()
	await get_tree().process_frame
	hud=NewHUD23.new();hud.temporary_art=actors.temporary_art;hud.setup(self)
	for size_ in [Vector2i(1920,1080),Vector2i(1280,720),Vector2i(1280,960)]:
		get_window().size=size_
		for state in ["ready","cooldown","empty"]:
			var saved_potions: int=run.potions
			var saved_dash: int=run.get_next_dash_tick()
			# Only these display fixture fields differ. Restore before comparison.
			run._next_dash=run.tick if state=="ready" else run.tick+149
			run.potions=0 if state=="empty" else 5
			hud.sync(run,0)
			await RenderingServer.frame_post_draw
			await RenderingServer.frame_post_draw
			var font: Font=hud.dash.get_theme_font("font")
			var font_size: int=hud.dash.get_theme_font_size("font_size")
			var needed := font.get_multiline_string_size(hud.dash.text,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size)
			var rect: Rect2=hud.dash.get_global_rect()
			rows.append({"window":size_,"state":state,"text":hud.dash.text,"rect":rect,"needed":needed,"fits":needed.x<=rect.size.x and needed.y<=rect.size.y,"two_lines":hud.dash.get_line_count()==2,"inside_viewport":get_viewport().get_visible_rect().encloses(rect)})
			get_viewport().get_texture().get_image().save_png("res://hud23-shots/%dx%d-%s.png"%[size_.x,size_.y,state])
			run._next_dash=saved_dash;run.potions=saved_potions
	var same := frozen==run.snapshot()
	var ok := same
	for row in rows:ok=ok and row.fits and row.two_lines and row.inside_viewport
	var f := FileAccess.open("res://hud23-result.json",FileAccess.WRITE);f.store_string(JSON.stringify({"same_complete_core_restored":same,"records":rows,"scope":"HUD23 display fixture on normal earned16000tick build, temporary potion/dash fields restored. Physics stopped; not gameplay or final responsiveness/performance."},"\t"));f.close()
	get_tree().quit(0 if ok else 1)
