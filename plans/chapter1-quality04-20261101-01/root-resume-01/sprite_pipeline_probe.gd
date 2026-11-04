extends SceneTree
func _initialize() -> void:call_deferred("_test")
func _test() -> void:
	var node := Node3D.new();root.add_child(node)
	var camera := Camera3D.new();camera.projection=Camera3D.PROJECTION_ORTHOGONAL;camera.size=5.0;camera.position=Vector3(0,2.7,14);node.add_child(camera);camera.look_at(Vector3(0,1.3,0));camera.current=true
	var canvas := CanvasLayer.new();node.add_child(canvas)
	var title := Label.new();title.text="등록 스프라이트 · 같은 설정으로 Godot 표시";title.position=Vector2(28,20);title.add_theme_font_size_override("font_size",23);canvas.add_child(title)
	var checks: Dictionary={};var rows: Array=[];var sample_count := 0
	var roles := ["hero","walker","ranged","charger","elite"]
	for index in roles.size():
		var role: String=roles[index]
		var actor=load("res://chapter1/presentation/sprite_asset_presenter.gd").new();node.add_child(actor);actor.position=Vector3((index-2)*1.85,0,0)
		var path := "res://plans/chapter1-quality04-20261101-01/sprite-pipeline01/assets/"+role+"-demo/actor.json"
		var configured: bool=actor.configure(path);checks[role+"_configured"]=configured
		var all_frames := true
		for name_ in actor.clips:
			var parts: PackedStringArray=String(name_).split("_");var action: String=parts[0];var direction: String=parts[1] if parts.size()>1 else "south"
			var ids: Array=actor.clips[name_];var total := 0.0
			for id_ in ids:total+=float(actor.document.frames[id_].get("duration",.125))
			var elapsed := 0.0
			for i in ids.size():
				var duration: float=actor.document.frames[ids[i]].get("duration",.125)
				var sampled: bool=actor.sample(action,direction,(elapsed+duration*.5)/total)
				all_frames=all_frames and sampled and actor.last_sample.frame_index==ids[i];elapsed+=duration;sample_count+=1
		checks[role+"_all_authored_frames_sampled"]=all_frames
		actor.sample("death","south",1.0);checks[role+"_death_holds_last"]=actor.last_sample.local_frame==actor.clips.death.size()-1
		actor.sample("missing","west",.8);checks[role+"_missing_pose_explicit_fallback"]=actor.last_sample.fallback and actor.last_sample.local_frame==0
		actor.sample("move","south",.6);rows.append({"role":role,"sample":actor.last_sample,"pixel_size":actor.sprite.pixel_size,"offset":actor.sprite.offset})
	var headless := DisplayServer.get_name()=="headless"
	if not headless:
		for i in 6:await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png("res://sprite-pipeline-preview.png")
	var ok := true
	for value in checks.values():ok=ok and bool(value)
	var file := FileAccess.open("res://sprite-pipeline-"+("headless" if headless else "gpu")+"-result.json",FileAccess.WRITE);file.store_string(JSON.stringify({"checks":checks,"passed":ok,"sample_count":sample_count,"rows":rows,"scope":"Isolated Godot sprite presenter/catalog proof. Five legacy sprites, exact clip frame selection, death clamp and explicit missing-pose fallback. Not current product30 actor replacement or full combat approval."},"\t"));file.close()
	node.queue_free()
	for i in 8:await process_frame
	quit(0 if ok else 1)
