extends "res://chapter1/chapter_one_input21.gd"
var frozen: Dictionary
func _ready() -> void:
	super._ready()
	set_physics_process(false)
	while run.tick<7700:
		run.step(full_pilot.decide())
		if run.tick<900:continue
		var nearby := 0
		for p in run.projectiles:
			if p.hostile and p.position.distance_to(run.hero.position)<6.0:nearby+=1
		if nearby>=6:break
	actors.reset();effects.reset();hud.reset();run.events.clear()
	world.update_camera(run.hero.position,10);world.sync(run,0);actors.sync(run,0);effects.sync(run,0);hud.sync(run,0)
	frozen=run.snapshot().duplicate(true)
	call_deferred("_compare")
func _process(_delta: float) -> void:pass
func _compare() -> void:
	DirAccess.make_dir_recursive_absolute("res://hostile22-shots")
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://hostile22-shots/before.png")
	var material := ShaderMaterial.new()
	material.shader=load("res://chapter1/view/comet_hostile22.gdshader")
	effects.projectiles.material_override=material
	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw
	get_viewport().get_texture().get_image().save_png("res://hostile22-shots/after.png")
	var hostile := 0
	for p in run.projectiles:
		if p.hostile:hostile+=1
	var same := frozen==run.snapshot()
	var report := {"same_complete_core":same,"tick":run.tick,"hostile_count":hostile,"projectiles":run.projectiles.size(),"viewport":get_viewport().get_visible_rect().size,"scope":"Normal earned policy to first >=900tick state with6 nearby hostile bolts, then physics stopped. Same core/camera/batch, shader swap only. Static visual comparison, not manual or performance."}
	var f := FileAccess.open("res://hostile22-result.json",FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close()
	get_tree().quit(0 if same and hostile>=6 else 1)
