extends Node3D
var model: Node3D
var player: AnimationPlayer
var age := 0.0
var last_clip := ""
var shot := 0
var times := [1.0,2.08,2.23,2.38,2.53,5.12,5.25,5.45,8.12,10.1,10.6,11.1]
var label: Label
func _ready() -> void:
	DisplayServer.window_set_title("Mage rig · actual Godot motion research")
	var env := WorldEnvironment.new();env.environment=Environment.new();env.environment.background_mode=Environment.BG_COLOR
	env.environment.background_color=Color("161d24");env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color=Color("c7d3ed");env.environment.ambient_light_energy=.65
	env.environment.tonemap_mode=Environment.TONE_MAPPER_FILMIC;add_child(env)
	var sun := DirectionalLight3D.new();sun.rotation_degrees=Vector3(-52,-35,0);sun.light_color=Color("e3d5bf");sun.light_energy=1.2;sun.shadow_enabled=true;add_child(sun)
	var floor_ := MeshInstance3D.new();var plane := PlaneMesh.new();plane.size=Vector2(30,30);floor_.mesh=plane
	var mat := StandardMaterial3D.new();mat.albedo_color=Color("343e3b");mat.roughness=.93;floor_.material_override=mat;floor_.position.y=-.015;add_child(floor_)
	model=load("res://mage_animated.glb").instantiate();add_child(model)
	player=model.find_child("AnimationPlayer",true,false)
	assert(player!=null)
	var report := {}
	for key in player.get_animation_list():
		var animation := player.get_animation(key);report[key]={"length":animation.length,"tracks":animation.get_track_count()}
		if key in ["idle","run"]:animation.loop_mode=Animation.LOOP_LINEAR
	assert(player.has_animation("run") and player.has_animation("cast") and player.has_animation("death"))
	print("MAGE_GODOT_ANIMATIONS ",JSON.stringify(report))
	var skeleton: Skeleton3D=model.find_child("Skeleton3D",true,false)
	assert(skeleton!=null);print("MAGE_GODOT_BONES ",skeleton.get_bone_count())
	var camera := Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=4.2;camera.position=Vector3(3,5.2,4.4);add_child(camera);camera.look_at(Vector3(0,.9,0));camera.current=true
	var canvas := CanvasLayer.new();add_child(canvas);label=Label.new();label.position=Vector2(30,22);label.add_theme_font_size_override("font_size",24);canvas.add_child(label)
	DirAccess.make_dir_recursive_absolute("res://captures")
func _process(delta: float) -> void:
	age+=delta
	var clip := "idle" if age<2 else ("run" if age<5 else ("cast" if age<6.5 else ("run" if age<8 else ("hit" if age<8.4 else ("run" if age<10 else "death")))))
	if clip!=last_clip:player.play(clip,.08);last_clip=clip
	label.text="RIG MOTION STUDY  /  "+clip.to_upper()+"\nCC BY-SA 3.0 · thecubber / rig credit Julius"
	if age>=6.5 and age<8:model.rotation.y=(age-6.5)*2
	elif age>=8.4 and age<10:model.rotation.y=0
	if shot<times.size() and age>=times[shot]:
		var id_ := shot;shot+=1
		await RenderingServer.frame_post_draw
		var error := get_viewport().get_texture().get_image().save_png("res://captures/%02d_%s.png"%[id_,clip]);assert(error==OK)
	if age>12.5:
		print("MAGE_PREVIEW_COMPLETE captures=",shot);get_tree().quit()
