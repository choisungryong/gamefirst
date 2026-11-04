extends SceneTree
func _init() -> void:call_deferred("go")
func different(a: Variant,b: Variant) -> bool:
	if a is Quaternion:return a.angle_to(b)>.0001
	if a is Vector3:return a.distance_to(b)>.000002
	return a!=b
func go() -> void:
	var scene=load("res://derived/skeleton_outlaw.glb").instantiate();root.add_child(scene)
	var player: AnimationPlayer=scene.find_child("AnimationPlayer",true,false)
	var report := {}
	for key in player.get_animation_list():
		if key=="RESET":continue
		var animation: Animation=player.get_animation(key)
		var start := INF;var end := -INF;var changes := 0;var examples: Array=[]
		for track in animation.get_track_count():
			var count := animation.track_get_key_count(track)
			var track_start := INF;var track_end := -INF
			for i in range(1,count):
				if different(animation.track_get_key_value(track,i-1),animation.track_get_key_value(track,i)):
					track_start=minf(track_start,animation.track_get_key_time(track,i-1));track_end=maxf(track_end,animation.track_get_key_time(track,i));changes+=1
			if track_start<INF:
				start=minf(start,track_start);end=maxf(end,track_end)
				if examples.size()<4:examples.append({"path":str(animation.track_get_path(track)),"keys":count,"first_change":track_start,"last_change":track_end})
		report[key]={"length":animation.length,"first_change":start,"last_change":end,"changes":changes,"examples":examples}
	var path := "res://motion-inventory03.json"
	if FileAccess.file_exists(path):push_error("Preserve inventory");quit(1);return
	var f := FileAccess.open(path,FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close()
	print("SKELETON_MOTION_INTERVALS ",JSON.stringify(report));scene.queue_free();await process_frame;quit()
