extends Node3D
var age := 0.0
var actor: Node3D
var player: AnimationPlayer
var skeleton: Skeleton3D
var label: Label
var shots := {}
const CLIPS := ["idle","walk","windup_slam","slam","windup_fan","fan","hit","death"]
func _ready() -> void:
	var env := Environment.new();env.background_mode=Environment.BG_COLOR;env.background_color=Color("172128")
	env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR;env.ambient_light_color=Color("9baab9");env.ambient_light_energy=.4;env.tonemap_mode=Environment.TONE_MAPPER_FILMIC
	var we := WorldEnvironment.new();we.environment=env;add_child(we)
	for spec in [[Vector3(-42,-35,0),Color("eddbc4"),1.6],[Vector3(-28,145,0),Color("7faad8"),.85]]:
		var light := DirectionalLight3D.new();light.rotation_degrees=spec[0];light.light_color=spec[1];light.light_energy=spec[2];light.shadow_enabled=true;add_child(light)
	var ground := MeshInstance3D.new();var plane := PlaneMesh.new();plane.size=Vector2(20,20);ground.mesh=plane
	var material := StandardMaterial3D.new();material.albedo_color=Color("3c4546");material.roughness=.9;ground.material_override=material;ground.position.y=-.04;add_child(ground)
	actor=load("res://art/chained_demon_animated.glb").instantiate();add_child(actor)
	player=actor.find_child("AnimationPlayer",true,false);skeleton=actor.find_child("Skeleton3D",true,false)
	player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	var camera := Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=6.0;camera.position=Vector3(4,5,7);add_child(camera);camera.look_at(Vector3(0,1.6,0));camera.current=true
	label=Label.new();label.position=Vector2(20,16);label.add_theme_font_size_override("font_size",24);label.add_theme_color_override("font_color",Color("e6d6aa"));add_child(label)
	print("DEMON_PREVIEW_READY ",JSON.stringify({"bones":skeleton.get_bone_count(),"clips":Array(player.get_animation_list()),"scope":"Own eight clips on Mophs rig, legacy material/weights repaired; research, not runtime/art approval"}))
func _process(delta: float) -> void:
	age+=delta
	var index := int(age/1.7)
	if index>=CLIPS.size():get_tree().quit();return
	var name_: String=CLIPS[index];var t := fmod(age,1.7)/1.7
	var clip := player.get_animation(name_)
	player.play(name_,0);player.seek(t*clip.length,true);player.advance(0)
	label.text="%s · %.2f / %.2fs · CC-BY3.0 research"%[name_,t*clip.length,clip.length]
	for part in 3:
		var key := name_+"-%d"%part
		if t>=[.2,.5,.85][part] and not shots.has(key):
			shots[key]=true;capture(key)
func capture(key: String) -> void:
	await RenderingServer.frame_post_draw
	var folder := "res://captures";DirAccess.make_dir_recursive_absolute(folder)
	var path := folder.path_join(key+".png")
	if not FileAccess.file_exists(path):get_viewport().get_texture().get_image().save_png(path)
