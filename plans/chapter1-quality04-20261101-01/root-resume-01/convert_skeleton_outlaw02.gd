extends SceneTree
const CLIPS={"idle":"Idle00","idle_alert":"Idle01","walk":"Walk00","run":"Run00","attack_slam":"Attack00","attack_fan":"Attack01","attack_cross":"Attack02","hit":"Damage00","death":"Dead01"}
var report := {"clips":{},"meshes":[],"removed":["SkeletonHair","MetalJaw"],"scope":"Public CC0 art research. Native ufbx ASCII import, author clips merged, diffuse path repaired. No runtime adoption or art approval."}
func _init() -> void:call_deferred("go")
func go() -> void:
	var source=load("res://art/SkeletonOutlaw.fbx").instantiate();root.add_child(source)
	var skeleton: Skeleton3D=source.find_child("Skeleton3D",true,false)
	var player: AnimationPlayer=source.find_child("AnimationPlayer",true,false)
	player.stop()
	for key in player.get_animation_library_list():player.remove_animation_library(key)
	var library := AnimationLibrary.new()
	for key in CLIPS:
		var scene=load("res://art/"+CLIPS[key]+".fbx").instantiate()
		var other: AnimationPlayer=scene.find_child("AnimationPlayer",true,false)
		var names: Array=[]
		for name_ in other.get_animation_list():
			if name_!="RESET":names.append(name_)
		if names.size()!=1:push_error("Expected one author clip "+str(names));scene.free();source.queue_free();quit(1);return
		var animation: Animation=other.get_animation(names[0]).duplicate(true)
		animation.loop_mode=Animation.LOOP_LINEAR if key in ["idle","idle_alert","walk","run"] else Animation.LOOP_NONE
		library.add_animation(key,animation)
		report.clips[key]={"author_file":CLIPS[key]+".fbx","length":animation.length,"tracks":animation.get_track_count()}
		scene.free()
	player.add_animation_library("",library)
	var body_texture=load("res://art/Atlas.png")
	var axe_texture=load("res://art/Axe00.png")
	setup_meshes(source,body_texture,axe_texture)
	var low := INF;var high := -INF
	for bone in ["ORG-head","ORG-toe_L","ORG-toe_R"]:
		var at: Vector3=(skeleton.global_transform*skeleton.get_bone_global_rest(skeleton.find_bone(bone))).origin
		low=minf(low,at.y);high=maxf(high,at.y)
	var factor := 2.4/((high-low)*1.14)
	var normalized := Node3D.new();normalized.name="OutlawResearchMetres";root.add_child(normalized)
	source.reparent(normalized);source.transform=Transform3D(Basis.IDENTITY.scaled(Vector3.ONE*factor),Vector3(0,-low*factor+.025,0))
	report.source_bone_height=high-low;report.uniform_scale=factor;report.bones=skeleton.get_bone_count()
	var path := "res://derived/skeleton_outlaw.glb"
	if FileAccess.file_exists(path):push_error("Preserve existing GLB");quit(1);return
	DirAccess.make_dir_recursive_absolute("res://derived")
	var document := GLTFDocument.new();var state := GLTFState.new()
	var append_error := document.append_from_scene(normalized,state)
	if append_error!=OK:push_error("GLTF append failed "+str(append_error));quit(1);return
	var write_error := document.write_to_filesystem(state,path)
	if write_error!=OK:push_error("GLTF write failed "+str(write_error));quit(1);return
	var file := FileAccess.open("res://derived/REPORT.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));file.close()
	print("SKELETON_GLTF_RESEARCH ",JSON.stringify(report))
	normalized.queue_free();await process_frame;quit()
func setup_meshes(node: Node,body: Texture2D,axe: Texture2D) -> void:
	for child in node.get_children():
		if child is MeshInstance3D:
			if child.name in ["SkeletonHair","MetalJaw"]:child.get_parent().remove_child(child);child.free();continue
			for i in child.mesh.get_surface_count():
				var material := child.get_active_material(i).duplicate() as StandardMaterial3D
				material.albedo_texture=axe if String(material.resource_name).begins_with("Axes") else body
				material.roughness=.79;material.metallic=.1 if child.name in ["Shoulder00","Shoulder01","Axe00"] else 0.0
				child.set_surface_override_material(i,material)
			report.meshes.append(child.name)
		else:setup_meshes(child,body,axe)
