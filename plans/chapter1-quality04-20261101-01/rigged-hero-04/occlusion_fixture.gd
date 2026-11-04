extends "res://chapter1/chapter_one_view.gd"
## Visual fixture only: fixed hero, enemy behind/front/lateral/front-untinted.
var shots := {}
var _fixture_dir := "res://plans/chapter1-quality04-20261101-01/rigged-hero-04/occlusion-fixture/captures"
func _ready() -> void:
	super._ready();world.camera.size=8
	run.enemies.clear();run.projectiles.clear();run.orbs.clear();run.items.clear()
	run.hero.position=Vector2.ZERO;run.hero.direction=Vector2.DOWN
	run._spawn("walker",Vector2(1,1));run.events.clear()
func _physics_process(_delta: float) -> void:
	run.tick+=1
	var nearer := Vector2(world.camera.global_basis.z.x,world.camera.global_basis.z.z).normalized()
	var right := Vector2(world.camera.global_basis.x.x,world.camera.global_basis.x.z).normalized()
	var phase := mini(3,int(_wall_age/1.5))
	var e: Dictionary=run.enemies.values()[0]
	e.position=-nearer*.9 if phase==0 else nearer*.8+(right*2.3 if phase==2 else Vector2.ZERO)
	e.state="recover";e.direction=Vector2.DOWN
	actors.consume([])
func _process(delta: float) -> void:
	super._process(delta)
	var phase := mini(3,int(_wall_age/1.5))
	if phase==3:
		for overlay in actors._overlays:overlay.visible=false
	if not shots.has(phase) and fmod(_wall_age,1.5)>.65:
		shots[phase]=true
		DirAccess.make_dir_recursive_absolute(_fixture_dir)
		await RenderingServer.frame_post_draw
		var path := _fixture_dir.path_join("phase-%d.png"%phase)
		if not FileAccess.file_exists(path):get_viewport().get_texture().get_image().save_png(path)
		print("RIG_OCCLUSION_FIXTURE ",JSON.stringify({"phase":phase,"overlap":actors._hero_overlapped,"overlay_visible":actors._overlays[0].visible,"enemy_alpha_cut":actors.actors.values()[0].get_meta("sprite").alpha_cut,"scope":"Visual placement fixture; no real combat or performance claim"}))
